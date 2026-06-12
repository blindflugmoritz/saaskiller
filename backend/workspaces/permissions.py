from rest_framework.permissions import BasePermission

from workspaces.models import Membership


def _get_membership(request, view):
    # Prefer explicit workspace_id kwarg; fall back to pk only when workspace_id is absent
    workspace_id = view.kwargs.get("workspace_id") or view.kwargs.get("pk")
    if not workspace_id:
        return None
    try:
        return Membership.objects.get(workspace_id=workspace_id, user=request.user)
    except Membership.DoesNotExist:
        return None


class IsWorkspaceMember(BasePermission):
    """Allow any member (owner/admin/member/viewer) of the workspace."""

    def has_permission(self, request, view):
        return _get_membership(request, view) is not None


class IsWorkspaceOwner(BasePermission):
    """Allow only the workspace owner."""

    def has_permission(self, request, view):
        membership = _get_membership(request, view)
        return membership is not None and membership.role == "owner"


class IsWorkspaceAdminOrOwner(BasePermission):
    """Allow owners and admins."""

    def has_permission(self, request, view):
        membership = _get_membership(request, view)
        return membership is not None and membership.role in ("owner", "admin")
