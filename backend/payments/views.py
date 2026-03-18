import json
import importlib.util
import os
from decimal import Decimal

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import TopUp, TopUpProvider, TopUpStatus
from .serializers import CreateTopUpSerializer
from .services import (
    create_coinbase_charge,
    create_manual_payoneer_topup,
    create_paypal_order,
    capture_paypal_order,
    mark_topup_succeeded,
    verify_coinbase_webhook,
)


class CreateTopUpView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreateTopUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        provider = serializer.validated_data["provider"]
        amount = Decimal(serializer.validated_data["amount"])
        success_url = serializer.validated_data.get("success_url") or None
        cancel_url = serializer.validated_data.get("cancel_url") or None

        provider_error = self._get_provider_setup_error(provider)
        if provider_error:
            return Response({"detail": provider_error}, status=400)

        topup = TopUp.objects.create(
            user=request.user,
            provider=provider,
            amount=amount,
            currency="USD",
            status=TopUpStatus.CREATED,
            success_url=success_url,
            cancel_url=cancel_url,
        )

        try:
            if provider == TopUpProvider.PAYONEER:
                payload = create_manual_payoneer_topup(topup=topup)
            elif provider == TopUpProvider.PAYPAL:
                payload = create_paypal_order(topup=topup)
            elif provider == TopUpProvider.CRYPTO:
                payload = create_coinbase_charge(topup=topup)
            elif provider == TopUpProvider.STRIPE:
                # We use Stripe Checkout Session for card payments.
                import stripe  # type: ignore

                stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")
                if not stripe.api_key:
                    raise RuntimeError("Missing STRIPE_SECRET_KEY.")

                success = (success_url or os.getenv("FRONTEND_URL", "http://localhost:3000").rstrip("/") + "/settings?topup=success")
                cancel = (cancel_url or os.getenv("FRONTEND_URL", "http://localhost:3000").rstrip("/") + "/settings?topup=cancel")

                session = stripe.checkout.Session.create(
                    mode="payment",
                    payment_method_types=["card"],
                    line_items=[
                        {
                            "price_data": {
                                "currency": "usd",
                                "product_data": {"name": "Balance top up"},
                                "unit_amount": int(amount * 100),
                            },
                            "quantity": 1,
                        }
                    ],
                    client_reference_id=str(topup.id),
                    metadata={"topup_id": str(topup.id)},
                    success_url=success + "&session_id={CHECKOUT_SESSION_ID}",
                    cancel_url=cancel,
                )
                topup.provider_reference = session.get("id")
                topup.status = TopUpStatus.PENDING
                topup.save(update_fields=["provider_reference", "status", "updated_at"])
                payload = {"kind": "redirect", "redirect_url": session.get("url"), "provider_reference": topup.provider_reference}
            else:
                return Response({"detail": "Unsupported provider."}, status=400)

            return Response({"topup_id": topup.id, **payload}, status=201)
        except Exception as e:
            topup.status = TopUpStatus.FAILED
            topup.save(update_fields=["status", "updated_at"])
            return Response({"detail": str(e)}, status=400)

    def _get_provider_setup_error(self, provider: str) -> str | None:
        if provider == TopUpProvider.STRIPE:
            missing = []
            if importlib.util.find_spec("stripe") is None:
                missing.append("Python package 'stripe' is not installed")
            if not os.getenv("STRIPE_SECRET_KEY"):
                missing.append("STRIPE_SECRET_KEY")
            if missing:
                return "Stripe is not configured: " + ", ".join(missing) + "."

        if provider == TopUpProvider.PAYPAL:
            missing = [name for name in ("PAYPAL_CLIENT_ID", "PAYPAL_CLIENT_SECRET") if not os.getenv(name)]
            if missing:
                return "PayPal is not configured: missing " + ", ".join(missing) + "."

        if provider == TopUpProvider.CRYPTO:
            missing = [name for name in ("COINBASE_COMMERCE_API_KEY",) if not os.getenv(name)]
            if missing:
                return "Crypto top-ups are not configured: missing " + ", ".join(missing) + "."

        return None


class PayPalCaptureView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, topup_id: int):
        try:
            topup = TopUp.objects.get(pk=topup_id, user=request.user, provider=TopUpProvider.PAYPAL)
        except TopUp.DoesNotExist:
            return Response({"detail": "Top-up not found."}, status=404)

        try:
            capture_paypal_order(topup=topup)
        except Exception as e:
            return Response({"detail": str(e)}, status=400)
        return Response({"status": topup.status}, status=200)


@csrf_exempt
def stripe_webhook(request):
    """
    Stripe webhook handler: credits balance when checkout.session.completed
    """
    try:
        import stripe  # type: ignore
    except Exception:
        return HttpResponse(status=500)

    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    if not webhook_secret:
        return HttpResponse(status=400)

    try:
        event = stripe.Webhook.construct_event(payload=payload, sig_header=sig_header, secret=webhook_secret)
    except Exception:
        return HttpResponse(status=400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        topup_id = (session.get("metadata") or {}).get("topup_id") or session.get("client_reference_id")
        if topup_id:
            try:
                topup = TopUp.objects.select_related("user").get(pk=int(topup_id), provider=TopUpProvider.STRIPE)
                mark_topup_succeeded(topup=topup, provider_reference=session.get("id"))
            except Exception:
                pass

    return HttpResponse(status=200)


@csrf_exempt
def coinbase_webhook(request):
    """
    Coinbase Commerce webhook: credits balance when charge:confirmed
    """
    signature = request.META.get("HTTP_X_CC_WEBHOOK_SIGNATURE", "")
    raw = request.body
    if not verify_coinbase_webhook(raw_body=raw, signature=signature):
        return HttpResponse(status=400)

    try:
        payload = json.loads(raw.decode("utf-8"))
    except Exception:
        return HttpResponse(status=400)

    event_type = payload.get("event", {}).get("type")
    data = payload.get("event", {}).get("data", {})
    topup_id = (data.get("metadata") or {}).get("topup_id")

    if event_type in {"charge:confirmed", "charge:resolved"} and topup_id:
        try:
            topup = TopUp.objects.select_related("user").get(pk=int(topup_id), provider=TopUpProvider.CRYPTO)
            mark_topup_succeeded(topup=topup, provider_reference=data.get("id"))
        except Exception:
            pass

    return HttpResponse(status=200)

