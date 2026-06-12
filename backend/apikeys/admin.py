# === FEATURE: apikeys ===
from django.contrib import admin

from .models import ApiKey


@admin.register(ApiKey)
class ApiKeyAdmin(admin.ModelAdmin):
    list_display = ["name", "prefix", "user", "is_active", "last_used_at", "created_at"]
    list_filter = ["is_active"]
    search_fields = ["name", "prefix", "user__email"]
    readonly_fields = ["id", "key_hash", "prefix", "created_at", "last_used_at"]
    ordering = ["-created_at"]

    def has_add_permission(self, request):
        # Keys should only be created through the API (to surface the raw key)
        return False
# === END FEATURE: apikeys ===
