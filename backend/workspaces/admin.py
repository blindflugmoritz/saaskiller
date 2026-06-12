from django.contrib import admin
from .models import Workspace, Membership


class MembershipInline(admin.TabularInline):
    model = Membership
    extra = 0
    readonly_fields = ("joined_at",)


@admin.register(Workspace)
class WorkspaceAdmin(admin.ModelAdmin):
    list_display = ("name", "kind", "owner", "created_at")
    list_filter = ("kind",)
    search_fields = ("name", "owner__email")
    inlines = [MembershipInline]
    readonly_fields = ("created_at", "updated_at")


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "workspace", "role", "joined_at")
    list_filter = ("role",)
    search_fields = ("user__email", "workspace__name")
