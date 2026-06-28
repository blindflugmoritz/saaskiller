try:
    from workspaces.models import Workspace, Membership, Invitation
except ImportError:
    import pytest
    pytestmark = pytest.mark.skip(reason="workspaces feature not installed")
    Workspace = None
    Membership = None
    Invitation = None

import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import User


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def user(db):
    u = User.objects.create_user(email="ws_api@example.com", language_preference="en")
    u.email_verified = True
    u.save()
    return u


@pytest.fixture
def other_user(db):
    u = User.objects.create_user(email="ws_member@example.com", language_preference="en")
    u.email_verified = True
    u.save()
    return u


@pytest.fixture
def auth_client(user):
    c = APIClient()
    refresh = RefreshToken.for_user(user)
    c.credentials(HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}")
    return c


@pytest.fixture
def other_auth_client(other_user):
    c = APIClient()
    refresh = RefreshToken.for_user(other_user)
    c.credentials(HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}")
    return c


@pytest.fixture
def workspace(user):
    """A non-personal workspace owned by `user`."""
    ws = Workspace.objects.create(name="Test Workspace", owner=user, kind="business")
    Membership.objects.create(workspace=ws, user=user, role="owner")
    return ws


# ── Tests ─────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_list_workspaces(auth_client, user):
    """Authenticated user sees their workspaces (the personal one created on signup)."""
    resp = auth_client.get("/api/workspaces/")
    assert resp.status_code == 200
    assert isinstance(resp.data, list)
    # At least the personal workspace created via signal on user creation
    assert len(resp.data) >= 1
    workspace_names = [ws["name"] for ws in resp.data]
    # The personal workspace should exist
    assert any(ws["kind"] == "personal" for ws in resp.data)


@pytest.mark.django_db
def test_create_workspace(auth_client, user):
    """POST /api/workspaces/ creates a workspace and an owner membership."""
    resp = auth_client.post("/api/workspaces/", {"name": "My Team", "kind": "business"})
    assert resp.status_code == 201
    assert resp.data["name"] == "My Team"

    ws = Workspace.objects.get(pk=resp.data["id"])
    assert ws.owner == user
    assert Membership.objects.filter(workspace=ws, user=user, role="owner").exists()


@pytest.mark.django_db
def test_invite_member(auth_client, workspace, mailoutbox):
    """POST /api/workspaces/<id>/invite/ with {email, role} creates an invitation and sends email."""
    resp = auth_client.post(
        f"/api/workspaces/{workspace.id}/invite/",
        {"email": "invited@example.com", "role": "member"},
    )
    assert resp.status_code == 201
    assert "token" not in resp.data
    assert resp.data.get("detail") == "Invitation sent."

    assert Invitation.objects.filter(
        workspace=workspace, invited_email="invited@example.com"
    ).exists()

    assert len(mailoutbox) == 1
    assert "invited@example.com" in mailoutbox[0].to


@pytest.mark.django_db
def test_accept_invitation(auth_client, other_auth_client, workspace, other_user):
    """GET /api/workspaces/invite/<token>/ creates membership for the authenticated user."""
    invitation = Invitation.objects.create(
        workspace=workspace,
        invited_email=other_user.email,
        role="member",
        invited_by=workspace.owner,
    )

    resp = other_auth_client.get(f"/api/workspaces/invite/{invitation.token}/")
    assert resp.status_code == 200
    assert resp.data["role"] == "member"

    assert Membership.objects.filter(
        workspace=workspace, user=other_user, role="member"
    ).exists()

    invitation.refresh_from_db()
    assert invitation.accepted_at is not None


@pytest.mark.django_db
def test_remove_member(auth_client, workspace, other_user):
    """Owner can DELETE a member via /api/workspaces/<id>/members/<membership_id>/remove/."""
    membership = Membership.objects.create(workspace=workspace, user=other_user, role="member")

    resp = auth_client.delete(
        f"/api/workspaces/{workspace.id}/members/{membership.id}/remove/"
    )
    assert resp.status_code == 204
    assert not Membership.objects.filter(pk=membership.id).exists()


@pytest.mark.django_db
def test_non_owner_cannot_delete_workspace(auth_client, other_auth_client, workspace, other_user):
    """A member (non-owner) cannot DELETE the workspace and gets 403."""
    Membership.objects.create(workspace=workspace, user=other_user, role="member")

    resp = other_auth_client.delete(f"/api/workspaces/{workspace.id}/")
    assert resp.status_code == 403


# ── Privilege escalation guards ───────────────────────────────────────────────

@pytest.mark.django_db
def test_admin_cannot_promote_to_owner(auth_client, workspace, other_user, other_auth_client):
    """An admin cannot promote another member to owner."""
    membership = Membership.objects.create(workspace=workspace, user=other_user, role="member")
    # Make the caller an admin (not owner)
    admin_user = User.objects.create_user(email="admin@example.com", language_preference="en")
    admin_user.email_verified = True
    admin_user.save()
    admin_membership = Membership.objects.create(workspace=workspace, user=admin_user, role="admin")
    admin_client = APIClient()
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(admin_user)
    admin_client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}")

    resp = admin_client.patch(
        f"/api/workspaces/{workspace.id}/members/{membership.id}/",
        {"role": "owner"},
    )
    assert resp.status_code == 403


@pytest.mark.django_db
def test_admin_cannot_modify_owner_membership(auth_client, workspace, other_user):
    """An admin cannot touch the owner's membership."""
    owner_membership = Membership.objects.get(workspace=workspace, role="owner")
    admin_user = User.objects.create_user(email="admin2@example.com", language_preference="en")
    admin_user.email_verified = True
    admin_user.save()
    Membership.objects.create(workspace=workspace, user=admin_user, role="admin")
    admin_client = APIClient()
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(admin_user)
    admin_client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}")

    resp = admin_client.patch(
        f"/api/workspaces/{workspace.id}/members/{owner_membership.id}/",
        {"role": "admin"},
    )
    assert resp.status_code == 403


@pytest.mark.django_db
def test_sole_owner_cannot_demote_themselves(auth_client, workspace, user):
    """The sole owner cannot demote themselves to member."""
    owner_membership = Membership.objects.get(workspace=workspace, user=user, role="owner")

    resp = auth_client.patch(
        f"/api/workspaces/{workspace.id}/members/{owner_membership.id}/",
        {"role": "member"},
    )
    assert resp.status_code == 400


# ── Invitation security ────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_expired_invitation_rejected(other_auth_client, workspace, other_user):
    """An expired invitation returns 404."""
    from django.utils import timezone
    invitation = Invitation.objects.create(
        workspace=workspace,
        invited_email=other_user.email,
        role="member",
        invited_by=workspace.owner,
        expires_at=timezone.now() - timezone.timedelta(days=1),
    )

    resp = other_auth_client.get(f"/api/workspaces/invite/{invitation.token}/")
    assert resp.status_code == 404


@pytest.mark.django_db
def test_wrong_email_invitation_rejected(auth_client, workspace, user):
    """A user whose email doesn't match the invitation gets 403."""
    invitation = Invitation.objects.create(
        workspace=workspace,
        invited_email="someone_else@example.com",
        role="member",
        invited_by=workspace.owner,
    )

    # auth_client is logged in as `user` (ws_api@example.com), not someone_else
    resp = auth_client.get(f"/api/workspaces/invite/{invitation.token}/")
    assert resp.status_code == 403


@pytest.mark.django_db
def test_already_accepted_invitation_rejected(other_auth_client, workspace, other_user):
    """Replaying an already-accepted invitation token returns 400."""
    invitation = Invitation.objects.create(
        workspace=workspace,
        invited_email=other_user.email,
        role="member",
        invited_by=workspace.owner,
    )
    invitation.accept(other_user)

    resp = other_auth_client.get(f"/api/workspaces/invite/{invitation.token}/")
    assert resp.status_code == 400
