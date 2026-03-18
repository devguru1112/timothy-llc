import base64
import hashlib
import hmac
import json
import os
from decimal import Decimal
from typing import Any, Optional

import requests

from .models import TopUp, TopUpProvider, TopUpStatus


def _frontend_default_url(path: str = "/settings") -> str:
    base = os.getenv("FRONTEND_URL", "http://localhost:3000")
    return base.rstrip("/") + path


def create_manual_payoneer_topup(*, topup: TopUp) -> dict[str, Any]:
    # Manual provider: user is instructed to transfer, admin later marks it succeeded.
    receive_email = os.getenv("PAYONEER_RECEIVE_EMAIL", "").strip()
    reference = f"PAYONEER-TOPUP-{topup.id}"
    topup.status = TopUpStatus.PENDING
    topup.save(update_fields=["status", "updated_at"])
    if receive_email:
        message = (
            f"Send the Payoneer transfer to {receive_email} and include reference {reference}. "
            "Once payment is received, support/admin will confirm it and your balance will be updated."
        )
    else:
        message = (
            f"Payoneer top-up created as pending. Use reference {reference} when sending the transfer "
            "and follow the Payoneer receiving details provided by support/admin."
        )
    return {
        "kind": "manual",
        "message": message,
        "payoneer_receive_email": receive_email or None,
        "reference": reference,
        "instructions": (
            "If your Payoneer account supports email transfers, send the payment to the receiving email above. "
            "If not, use the payment request or receiving details shared by support/admin."
        ),
    }


def create_paypal_order(*, topup: TopUp) -> dict[str, Any]:
    """
    Creates a PayPal order and returns approval URL.
    Uses PayPal REST API with client credentials.
    """
    client_id = os.getenv("PAYPAL_CLIENT_ID", "")
    client_secret = os.getenv("PAYPAL_CLIENT_SECRET", "")
    environment = os.getenv("PAYPAL_ENV", "sandbox").lower()
    if not client_id or not client_secret:
        raise RuntimeError("Missing PAYPAL_CLIENT_ID/PAYPAL_CLIENT_SECRET.")

    api_base = "https://api-m.sandbox.paypal.com" if environment != "live" else "https://api-m.paypal.com"

    auth = base64.b64encode(f"{client_id}:{client_secret}".encode("utf-8")).decode("utf-8")
    token_res = requests.post(
        f"{api_base}/v1/oauth2/token",
        headers={"Authorization": f"Basic {auth}"},
        data={"grant_type": "client_credentials"},
        timeout=30,
    )
    token_res.raise_for_status()
    access_token = token_res.json()["access_token"]

    success_url = topup.success_url or _frontend_default_url("/settings?topup=success")
    cancel_url = topup.cancel_url or _frontend_default_url("/settings?topup=cancel")

    order_res = requests.post(
        f"{api_base}/v2/checkout/orders",
        headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
        json={
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "custom_id": str(topup.id),
                    "reference_id": f"topup-{topup.id}",
                    "amount": {"currency_code": topup.currency, "value": str(topup.amount)},
                }
            ],
            "application_context": {
                "return_url": success_url,
                "cancel_url": cancel_url,
                "brand_name": "Timothy LLC",
                "user_action": "PAY_NOW",
            },
        },
        timeout=30,
    )
    order_res.raise_for_status()
    order = order_res.json()
    topup.provider_reference = order.get("id")
    topup.status = TopUpStatus.PENDING
    topup.save(update_fields=["provider_reference", "status", "updated_at"])

    approve_url: Optional[str] = None
    for link in order.get("links", []):
        if link.get("rel") == "approve":
            approve_url = link.get("href")
            break
    if not approve_url:
        raise RuntimeError("PayPal approval link missing.")

    return {"kind": "redirect", "redirect_url": approve_url, "provider_reference": topup.provider_reference}


def capture_paypal_order(*, topup: TopUp) -> None:
    """Server-side capture to finalize payment (called from frontend success handler)."""
    client_id = os.getenv("PAYPAL_CLIENT_ID", "")
    client_secret = os.getenv("PAYPAL_CLIENT_SECRET", "")
    environment = os.getenv("PAYPAL_ENV", "sandbox").lower()
    api_base = "https://api-m.sandbox.paypal.com" if environment != "live" else "https://api-m.paypal.com"

    auth = base64.b64encode(f"{client_id}:{client_secret}".encode("utf-8")).decode("utf-8")
    token_res = requests.post(
        f"{api_base}/v1/oauth2/token",
        headers={"Authorization": f"Basic {auth}"},
        data={"grant_type": "client_credentials"},
        timeout=30,
    )
    token_res.raise_for_status()
    access_token = token_res.json()["access_token"]

    if not topup.provider_reference:
        raise RuntimeError("TopUp has no PayPal order id.")

    cap_res = requests.post(
        f"{api_base}/v2/checkout/orders/{topup.provider_reference}/capture",
        headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
        timeout=30,
    )
    cap_res.raise_for_status()
    data = cap_res.json()

    # If capture completed, credit the user (idempotent via status check)
    status_ = (data.get("status") or "").upper()
    if status_ == "COMPLETED":
        mark_topup_succeeded(topup=topup, provider_reference=topup.provider_reference)
    else:
        # Leave pending; PayPal may need further action.
        topup.status = TopUpStatus.PENDING
        topup.save(update_fields=["status", "updated_at"])


def create_coinbase_charge(*, topup: TopUp) -> dict[str, Any]:
    """
    Coinbase Commerce charge (hosted checkout).
    """
    api_key = os.getenv("COINBASE_COMMERCE_API_KEY", "")
    if not api_key:
        raise RuntimeError("Missing COINBASE_COMMERCE_API_KEY.")

    success_url = topup.success_url or _frontend_default_url("/settings?topup=success")
    cancel_url = topup.cancel_url or _frontend_default_url("/settings?topup=cancel")

    res = requests.post(
        "https://api.commerce.coinbase.com/charges",
        headers={
            "X-CC-Api-Key": api_key,
            "X-CC-Version": "2018-03-22",
            "Content-Type": "application/json",
        },
        json={
            "name": "Balance top up",
            "description": f"Top up #{topup.id}",
            "pricing_type": "fixed_price",
            "local_price": {"amount": str(topup.amount), "currency": topup.currency},
            "metadata": {"topup_id": str(topup.id)},
            "redirect_url": success_url,
            "cancel_url": cancel_url,
        },
        timeout=30,
    )
    res.raise_for_status()
    data = res.json()["data"]
    topup.provider_reference = data.get("id")
    topup.status = TopUpStatus.PENDING
    topup.save(update_fields=["provider_reference", "status", "updated_at"])
    hosted_url = data.get("hosted_url")
    if not hosted_url:
        raise RuntimeError("Coinbase hosted_url missing.")
    return {"kind": "redirect", "redirect_url": hosted_url, "provider_reference": topup.provider_reference}


def verify_coinbase_webhook(*, raw_body: bytes, signature: str) -> bool:
    secret = os.getenv("COINBASE_COMMERCE_WEBHOOK_SECRET", "")
    if not secret:
        return False
    computed = hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(computed, signature or "")


def mark_topup_succeeded(*, topup: TopUp, provider_reference: Optional[str] = None) -> None:
    if topup.status == TopUpStatus.SUCCEEDED:
        return
    if provider_reference and not topup.provider_reference:
        topup.provider_reference = provider_reference

    # Credit user balance atomically
    from django.db import transaction
    from django.db.models import F

    with transaction.atomic():
        TopUp.objects.select_for_update().get(pk=topup.pk)
        if topup.status == TopUpStatus.SUCCEEDED:
            return
        topup.status = TopUpStatus.SUCCEEDED
        topup.save(update_fields=["status", "provider_reference", "updated_at"])
        topup.user.__class__.objects.filter(pk=topup.user_id).update(balance=F("balance") + Decimal(topup.amount))

