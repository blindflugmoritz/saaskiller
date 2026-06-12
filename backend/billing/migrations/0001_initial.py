# === FEATURE: stripe ===
# Generated migration for billing app
import uuid
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("workspaces", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Plan",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=255)),
                ("stripe_price_id", models.CharField(max_length=255, unique=True)),
                ("amount_cents", models.PositiveIntegerField(help_text="Price in smallest currency unit (cents)")),
                ("currency", models.CharField(default="usd", max_length=3)),
                ("interval", models.CharField(
                    choices=[("month", "Monthly"), ("year", "Yearly")],
                    default="month",
                    max_length=10,
                )),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "db_table": "sk_plans",
                "ordering": ["amount_cents"],
            },
        ),
        migrations.CreateModel(
            name="Subscription",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                (
                    "workspace",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="subscriptions",
                        to="workspaces.workspace",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="subscriptions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                ("stripe_subscription_id", models.CharField(max_length=255, unique=True)),
                ("stripe_customer_id", models.CharField(db_index=True, max_length=255)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("trialing", "Trialing"),
                            ("active", "Active"),
                            ("past_due", "Past Due"),
                            ("canceled", "Canceled"),
                            ("unpaid", "Unpaid"),
                        ],
                        default="active",
                        max_length=20,
                    ),
                ),
                ("current_period_end", models.DateTimeField()),
                ("cancel_at_period_end", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table": "sk_subscriptions",
                "ordering": ["-created_at"],
            },
        ),
    ]
# === END FEATURE: stripe ===
