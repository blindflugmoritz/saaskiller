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
    assert "token" in resp.data

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
