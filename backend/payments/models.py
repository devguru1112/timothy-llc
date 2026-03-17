from decimal import Decimal
from django.conf import settings
from django.db import models


class TopUpProvider(models.TextChoices):
    STRIPE = "stripe", "Stripe (card)"
    PAYPAL = "paypal", "PayPal"
    CRYPTO = "crypto", "Crypto"
    PAYONEER = "payoneer", "Payoneer (manual)"


class TopUpStatus(models.TextChoices):
    CREATED = "created", "Created"
    PENDING = "pending", "Pending"
    SUCCEEDED = "succeeded", "Succeeded"
    FAILED = "failed", "Failed"
    CANCELED = "canceled", "Canceled"


class TopUp(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="topups")
    provider = models.CharField(max_length=20, choices=TopUpProvider.choices)
    status = models.CharField(max_length=20, choices=TopUpStatus.choices, default=TopUpStatus.CREATED)

    # Amount in USD for now (can extend to multi-currency later)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10, default="USD")

    # Provider identifiers (idempotency / reconciliation)
    provider_reference = models.CharField(max_length=255, blank=True, null=True, db_index=True)

    # Where the user is redirected after payment
    success_url = models.URLField(blank=True, null=True)
    cancel_url = models.URLField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["provider", "provider_reference"]),
            models.Index(fields=["user", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"TopUp<{self.id}> {self.user_id} {self.provider} {self.amount} {self.status}"

    @property
    def amount_decimal(self) -> Decimal:
        return Decimal(self.amount)

