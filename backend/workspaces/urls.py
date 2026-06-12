from django.urls import path

from workspaces.views import (
    InvitationAcceptView,
    InvitationCreateView,
    MembershipListView,
    MembershipRemoveView,
    MembershipUpdateView,
    WorkspaceDetailView,
    WorkspaceListCreateView,
)

urlpatterns = [
    # Workspace CRUD
    path("", WorkspaceListCreateView.as_view(), name="workspace-list-create"),
    path("<uuid:pk>/", WorkspaceDetailView.as_view(), name="workspace-detail"),

    # Members
    path("<uuid:workspace_id>/members/", MembershipListView.as_view(), name="membership-list"),
    path("<uuid:workspace_id>/members/<uuid:pk>/", MembershipUpdateView.as_view(), name="membership-update"),
    path("<uuid:workspace_id>/members/<uuid:pk>/remove/", MembershipRemoveView.as_view(), name="membership-remove"),

    # Invitations
    path("<uuid:workspace_id>/invite/", InvitationCreateView.as_view(), name="invitation-create"),
    path("invite/<uuid:token>/", InvitationAcceptView.as_view(), name="invitation-accept"),
]
