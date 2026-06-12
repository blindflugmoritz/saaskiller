# === FEATURE: stripe ===
from django.contrib import admin
from .models import Plan, Subscription


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ["name", "stripe_price_id", "amount_cents", "currency", "interval", "is_active", "created_at"]
    list_filter = ["interval", "is_active", "currency"]
    search_fields = ["name", "stripe_price_id"]
    ordering = ["amount_cents"]


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "workspace",
        "stripe_subscription_id",
        "stripe_customer_id",
        "status",
        "current_period_end",
        "cancel_at_period_end",
        "created_at",
    ]
    list_filter = ["status", "cancel_at_period_end"]
    search_fields = ["user__email", "stripe_subscription_id", "stripe_customer_id"]
    ordering = ["-created_at"]
    raw_id_fields = ["user", "workspace"]
# === END FEATURE: stripe ===
