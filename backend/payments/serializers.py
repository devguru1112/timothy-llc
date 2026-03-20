from decimal import Decimal, InvalidOperation
from rest_framework import serializers
from .models import TopUpProvider


class CreateTopUpSerializer(serializers.Serializer):
    provider = serializers.ChoiceField(choices=TopUpProvider.choices)
    amount = serializers.CharField()
    success_url = serializers.URLField(required=False, allow_null=True, allow_blank=True)
    cancel_url = serializers.URLField(required=False, allow_null=True, allow_blank=True)

    def validate_amount(self, value: str) -> str:
        try:
            amount = Decimal(value)
        except (InvalidOperation, TypeError):
            raise serializers.ValidationError("Invalid amount.")
        if amount <= 0:
            raise serializers.ValidationError("Amount must be greater than 0.")
        if amount > Decimal("100000"):
            raise serializers.ValidationError("Amount too large.")
        # 2-decimal for USD
        if amount.quantize(Decimal("0.01")) != amount:
            raise serializers.ValidationError("Amount must have max 2 decimal places.")
        return value


class PlanPurchaseSerializer(serializers.Serializer):
    plan = serializers.ChoiceField(choices=[("pro", "pro"), ("premium", "premium")])
    months = serializers.ChoiceField(choices=[(1, 1), (3, 3), (6, 6), (12, 12)])

