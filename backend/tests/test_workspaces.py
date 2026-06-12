import pytest
from users.models import User
from workspaces.models import Workspace, Membership


@pytest.mark.django_db
def test_personal_workspace_created_on_signup():
    user = User.objects.create_user(email="ws@example.com")
    assert Membership.objects.filter(user=user).count() == 1
    membership = Membership.objects.get(user=user)
    assert membership.workspace.kind == "personal"
    assert membership.role == "owner"
    assert membership.workspace.owner == user


@pytest.mark.django_db
def test_only_one_workspace_created_on_signup():
    user = User.objects.create_user(email="ws2@example.com")
    assert Workspace.objects.filter(owner=user).count() == 1


@pytest.mark.django_db
def test_workspace_membership_unique_constraint():
    user = User.objects.create_user(email="ws3@example.com")
    workspace = Workspace.objects.get(owner=user)
    with pytest.raises(Exception):
        Membership.objects.create(workspace=workspace, user=user, role="member")
