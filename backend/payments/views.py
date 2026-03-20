import json
import importlib.util
import os
from decimal import Decimal

from django.db import transaction
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from projects.models import SystemSettings
from .models import TopUp, TopUpProvider, TopUpStatus
from .serializers import CreateTopUpSerializer, PlanPurchaseSerializer
from .services import (
    create_coinbase_charge,
    create_manual_payoneer_topup,
    create_paypal_order,
    capture_paypal_order,
    mark_topup_succeeded,
    verify_coinbase_webhook,
)

PLAN_DEFS = {
    "pro": {
        "setting_key": "plan_pro_monthly_price",
        "default_monthly_price": Decimal("29.00"),
        "priority_level": 3,
        "display_name": "Pro",
    },
    "premium": {
        "setting_key": "plan_premium_monthly_price",
        "default_monthly_price": Decimal("79.00"),
        "priority_level": 5,
        "display_name": "Premium",
    },
}

PLAN_DURATIONS = [
    {"months": 1, "discount_pct": 0},
    {"months": 3, "discount_pct": 10},
    {"months": 6, "discount_pct": 15},
    {"months": 12, "discount_pct": 25},
]


def _to_money(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"))


def _get_monthly_price(plan_key: str) -> Decimal:
    config = PLAN_DEFS[plan_key]
    default_price = config["default_monthly_price"]
    setting_key = config["setting_key"]
    setting, _ = SystemSettings.objects.get_or_create(
        key=setting_key,
        defaults={
            "value": str(_to_money(default_price)),
            "description": f"Monthly price for {config['display_name']} plan in USD.",
        },
    )
    raw = setting.value
    try:
        price = Decimal(str(raw))
    except Exception:
        price = default_price
    if price <= 0:
        price = default_price
    return _to_money(price)


def _plan_catalog_for_response() -> dict:
    plans = {}
    for key, config in PLAN_DEFS.items():
        monthly = _get_monthly_price(key)
        options = []
        for duration in PLAN_DURATIONS:
            months = duration["months"]
            discount_pct = duration["discount_pct"]
            subtotal = _to_money(monthly * months)
            total = _to_money(subtotal * (Decimal("1") - (Decimal(discount_pct) / Decimal("100"))))
            options.append(
                {
                    "months": months,
                    "discount_pct": discount_pct,
                    "subtotal": str(subtotal),
                    "total": str(total),
                    "monthly_equivalent": str(_to_money(total / months)),
                }
            )
        plans[key] = {
            "id": key,
            "name": config["display_name"],
            "priority_level": config["priority_level"],
            "monthly_price": str(monthly),
            "options": options,
        }
    return {"plans": plans}


class PlanPricingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(_plan_catalog_for_response(), status=200)

    def patch(self, request):
        if not request.user.is_superuser:
            return Response({"detail": "Only super admin can update plan prices."}, status=403)

        updates = [
            ("pro_monthly_price", PLAN_DEFS["pro"]["setting_key"], "Monthly price for Pro plan in USD."),
            ("premium_monthly_price", PLAN_DEFS["premium"]["setting_key"], "Monthly price for Premium plan in USD."),
        ]
        updated = False

        for payload_key, setting_key, description in updates:
            if payload_key not in request.data:
                continue
            try:
                amount = _to_money(Decimal(str(request.data.get(payload_key))))
            except Exception:
                return Response({"detail": f"Invalid value for {payload_key}."}, status=400)
            if amount <= 0:
                return Response({"detail": f"{payload_key} must be greater than 0."}, status=400)

            setting, _ = SystemSettings.objects.get_or_create(
                key=setting_key,
                defaults={"value": str(amount), "description": description},
            )
            setting.value = str(amount)
            setting.description = description
            setting.updated_by = request.user
            setting.save(update_fields=["value", "description", "updated_by", "updated_at"])
            updated = True

        if not updated:
            return Response({"detail": "No valid fields provided."}, status=400)

        return Response(_plan_catalog_for_response(), status=200)


class PlanPurchaseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PlanPurchaseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        plan_key = serializer.validated_data["plan"]
        months = int(serializer.validated_data["months"])
        config = PLAN_DEFS[plan_key]

        monthly = _get_monthly_price(plan_key)
        duration = next((d for d in PLAN_DURATIONS if d["months"] == months), None)
        if not duration:
            return Response({"detail": "Unsupported duration."}, status=400)

        subtotal = _to_money(monthly * months)
        discount_pct = duration["discount_pct"]
        total = _to_money(subtotal * (Decimal("1") - (Decimal(discount_pct) / Decimal("100"))))

        with transaction.atomic():
            user = request.user.__class__.objects.select_for_update().get(pk=request.user.pk)
            current_balance = _to_money(Decimal(user.balance))
            if current_balance < total:
                shortfall = _to_money(total - current_balance)
                return Response(
                    {
                        "detail": "Insufficient balance.",
                        "required": str(total),
                        "current_balance": str(current_balance),
                        "shortfall": str(shortfall),
                    },
                    status=400,
                )

            user.balance = _to_money(current_balance - total)
            user.priority_level = max(int(user.priority_level or 1), int(config["priority_level"]))
            user.save(update_fields=["balance", "priority_level", "updated_at"])

        return Response(
            {
                "status": "succeeded",
                "plan": plan_key,
                "months": months,
                "discount_pct": discount_pct,
                "charged_amount": str(total),
                "new_balance": str(_to_money(Decimal(user.balance))),
                "priority_level": user.priority_level,
            },
            status=200,
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

