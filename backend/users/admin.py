from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("email", "email_verified", "language_preference", "is_staff", "created_at")
    list_filter = ("email_verified", "is_staff", "is_active", "language_preference")
    search_fields = ("email",)
    ordering = ("-created_at",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Profile", {"fields": ("language_preference",)}),
        ("Verification", {"fields": ("email_verified", "email_verification_token", "email_verification_expires_at")}),
        ("Magic Link", {"fields": ("magic_link_token", "magic_link_expires_at")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Dates", {"fields": ("created_at", "updated_at", "last_login")}),
    )
    readonly_fields = ("created_at", "updated_at")

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2"),
        }),
    )
