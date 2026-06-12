# === FEATURE: apikeys ===
# Generated migration for apikeys app

import uuid
import django.db.models.deletion
import django.conf
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(django.conf.settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ApiKey",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="api_keys",
                        to=django.conf.settings.AUTH_USER_MODEL,
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("key_hash", models.CharField(max_length=64)),
                ("prefix", models.CharField(max_length=8)),
                ("last_used_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "db_table": "sk_api_keys",
                "ordering": ["-created_at"],
            },
        ),
    ]
# === END FEATURE: apikeys ===
