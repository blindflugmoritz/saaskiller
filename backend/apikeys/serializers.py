# === FEATURE: apikeys ===
from rest_framework import serializers

from .models import ApiKey


class ApiKeySerializer(serializers.ModelSerializer):
    """Read-only representation shown in list/detail responses."""

    class Meta:
        model = ApiKey
        fields = ["id", "name", "prefix", "last_used_at", "created_at", "is_active"]
        read_only_fields = fields


class ApiKeyCreateSerializer(serializers.Serializer):
    """Write serializer — accepts only a name to create a new key."""

    name = serializers.CharField(max_length=100)


class ApiKeyCreatedSerializer(ApiKeySerializer):
    """Returned once after creation — extends ApiKeySerializer with the raw key."""

    raw_key = serializers.CharField(read_only=True)

    class Meta(ApiKeySerializer.Meta):
        fields = ApiKeySerializer.Meta.fields + ["raw_key"]
        read_only_fields = fields
# === END FEATURE: apikeys ===
