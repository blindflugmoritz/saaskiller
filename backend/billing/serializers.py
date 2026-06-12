# === FEATURE: stripe ===
from rest_framework import serializers
from .models import Plan, Subscription


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = [
            "id",
            "name",
            "stripe_price_id",
            "amount_cents",
            "currency",
            "interval",
            "is_active",
            "created_at",
        ]
        read_only_fields = fields


class SubscriptionSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = Subscription
        fields = [
            "id",
            "workspace",
            "user",
            "stripe_subscription_id",
            "stripe_customer_id",
            "status",
            "current_period_end",
            "cancel_at_period_end",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields
# === END FEATURE: stripe ===
