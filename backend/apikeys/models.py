# === FEATURE: apikeys ===
import hashlib
import secrets
import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class ApiKey(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="api_keys",
    )
    name = models.CharField(max_length=100)
    key_hash = models.CharField(max_length=64)
    prefix = models.CharField(max_length=8)
    last_used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "sk_api_keys"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.prefix}…)"

    @classmethod
    def create(cls, user, name):
        """Generate a new API key. Returns (ApiKey instance, raw_key string).
        The raw key is shown once and never stored."""
        raw_key = secrets.token_urlsafe(32)
        prefix = raw_key[:8]
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        instance = cls.objects.create(
            user=user,
            name=name,
            key_hash=key_hash,
            prefix=prefix,
        )
        return instance, raw_key

    @classmethod
    def authenticate(cls, raw_key):
        """Look up an active ApiKey by its raw value. Returns ApiKey or None."""
        if not raw_key:
            return None
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        try:
            return cls.objects.select_related("user").get(
                key_hash=key_hash, is_active=True
            )
        except cls.DoesNotExist:
            return None
# === END FEATURE: apikeys ===
