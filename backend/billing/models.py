# === FEATURE: stripe ===
import uuid
from django.conf import settings
from django.db import models


class Plan(models.Model):
    INTERVAL_CHOICES = [
        ("month", "Monthly"),
        ("year", "Yearly"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    stripe_price_id = models.CharField(max_length=255, unique=True)
    amount_cents = models.PositiveIntegerField(help_text="Price in smallest currency unit (cents)")
    currency = models.CharField(max_length=3, default="usd")
    interval = models.CharField(max_length=10, choices=INTERVAL_CHOICES, default="month")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "sk_plans"
        ordering = ["amount_cents"]

    def __str__(self):
        return f"{self.name} ({self.interval}) — {self.amount_cents} {self.currency.upper()}"


class Subscription(models.Model):
    STATUS_CHOICES = [
        ("trialing", "Trialing"),
        ("active", "Active"),
        ("past_due", "Past Due"),
        ("canceled", "Canceled"),
        ("unpaid", "Unpaid"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(
        "workspaces.Workspace",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subscriptions",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subscriptions",
    )
    stripe_subscription_id = models.CharField(max_length=255, unique=True)
    stripe_customer_id = models.CharField(max_length=255, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    current_period_end = models.DateTimeField()
    cancel_at_period_end = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "sk_subscriptions"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} — {self.status} ({self.stripe_subscription_id})"

    @property
    def is_active(self):
        return self.status in ("trialing", "active")
# === END FEATURE: stripe ===
