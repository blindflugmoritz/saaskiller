from django.conf import settings
from django.core.mail import send_mail
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from workspaces.models import Invitation, Membership, Workspace
from workspaces.permissions import IsWorkspaceAdminOrOwner, IsWorkspaceMember, IsWorkspaceOwner
from workspaces.serializers import InvitationSerializer, MembershipSerializer, WorkspaceSerializer


# ---------------------------------------------------------------------------
# Workspace CRUD
# ---------------------------------------------------------------------------

class WorkspaceListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/workspaces/          — list workspaces the requesting user belongs to
    POST /api/workspaces/          — create a new workspace; auto-creates owner membership
    """

    serializer_class = WorkspaceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Workspace.objects.filter(memberships__user=self.request.user)

    def perform_create(self, serializer):
        workspace = serializer.save(owner=self.request.user)
        Membership.objects.create(workspace=workspace, user=self.request.user, role="owner")


class WorkspaceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/workspaces/<pk>/   — any member
    PATCH  /api/workspaces/<pk>/   — owner only
    DELETE /api/workspaces/<pk>/   — owner only
    """

    serializer_class = WorkspaceSerializer
    http_method_names = ["get", "patch", "delete", "head", "options"]

    def get_queryset(self):
        return Workspace.objects.filter(memberships__user=self.request.user)

    def get_permissions(self):
        if self.request.method in ("PATCH", "DELETE"):
            return [IsAuthenticated(), IsWorkspaceOwner()]
        return [IsAuthenticated(), IsWorkspaceMember()]


# ---------------------------------------------------------------------------
# Membership management
# ---------------------------------------------------------------------------

class MembershipListView(generics.ListAPIView):
    """
    GET /api/workspaces/<workspace_id>/members/   — any member can view
    """

    serializer_class = MembershipSerializer
    permission_classes = [IsAuthenticated, IsWorkspaceMember]

    def get_queryset(self):
        return Membership.objects.filter(workspace_id=self.kwargs["workspace_id"])


class MembershipUpdateView(generics.UpdateAPIView):
    """
    PATCH /api/workspaces/<workspace_id>/members/<pk>/   — owner/admin can change role
    """

    serializer_class = MembershipSerializer
    http_method_names = ["patch", "head", "options"]
    permission_classes = [IsAuthenticated, IsWorkspaceAdminOrOwner]

    def get_queryset(self):
        return Membership.objects.filter(workspace_id=self.kwargs["workspace_id"])


class MembershipRemoveView(APIView):
    """
    DELETE /api/workspaces/<workspace_id>/members/<pk>/
      - owner/admin can remove any other member
      - any member can remove themselves (leave)
    """

    permission_classes = [IsAuthenticated, IsWorkspaceMember]

    def delete(self, request, workspace_id, pk):
        try:
            target = Membership.objects.get(workspace_id=workspace_id, pk=pk)
        except Membership.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        requesting = Membership.objects.get(workspace_id=workspace_id, user=request.user)

        is_self = target.user == request.user
        is_admin_or_owner = requesting.role in ("owner", "admin")

        if not (is_self or is_admin_or_owner):
            return Response(
                {"detail": "You do not have permission to remove this member."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Prevent removing the sole owner
        if target.role == "owner":
            owner_count = Membership.objects.filter(workspace_id=workspace_id, role="owner").count()
            if owner_count <= 1:
                return Response(
                    {"detail": "Cannot remove the sole owner of a workspace."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        target.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---------------------------------------------------------------------------
# Invitations
# ---------------------------------------------------------------------------

class InvitationCreateView(APIView):
    """
    POST /api/workspaces/<workspace_id>/invite/
    Body: { email, role }
    Sends an invite email with an accept link.
    """

    permission_classes = [IsAuthenticated, IsWorkspaceAdminOrOwner]

    def post(self, request, workspace_id):
        try:
            workspace = Workspace.objects.get(pk=workspace_id)
        except Workspace.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # Verify the caller is actually a member (permission class checks kwargs pk, not workspace_id)
        if not Membership.objects.filter(workspace=workspace, user=request.user, role__in=("owner", "admin")).exists():
            return Response({"detail": "Not allowed."}, status=status.HTTP_403_FORBIDDEN)

        serializer = InvitationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        role = serializer.validated_data["role"]

        invitation = Invitation.objects.create(
            workspace=workspace,
            invited_email=email,
            role=role,
            invited_by=request.user,
        )

        frontend_base = getattr(settings, "FRONTEND_URL", "http://localhost:5173")
        accept_url = f"{frontend_base}/workspaces/invite/{invitation.token}"

        send_mail(
            subject=f"You've been invited to {workspace.name}",
            message=(
                f"{request.user.email} has invited you to join '{workspace.name}' as {role}.\n\n"
                f"Accept the invitation: {accept_url}\n\n"
                f"This link is single-use."
            ),
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com"),
            recipient_list=[email],
            fail_silently=False,
        )

        return Response({"detail": "Invitation sent.", "token": str(invitation.token)}, status=status.HTTP_201_CREATED)


class InvitationAcceptView(APIView):
    """
    GET /api/workspaces/invite/<token>/
    Authenticated user accepts the invitation — creates Membership, marks accepted.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, token):
        try:
            invitation = Invitation.objects.select_related("workspace").get(token=token)
        except Invitation.DoesNotExist:
            return Response({"detail": "Invalid or expired invitation."}, status=status.HTTP_404_NOT_FOUND)

        if invitation.accepted_at is not None:
            return Response({"detail": "Invitation already accepted."}, status=status.HTTP_400_BAD_REQUEST)

        invitation.accept(request.user)

        membership = Membership.objects.get(workspace=invitation.workspace, user=request.user)
        return Response(
            {
                "detail": "Invitation accepted.",
                "workspace": str(invitation.workspace_id),
                "role": membership.role,
            },
            status=status.HTTP_200_OK,
        )
