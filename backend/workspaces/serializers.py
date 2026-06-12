from rest_framework import serializers

from workspaces.models import Invitation, Membership, Workspace


class WorkspaceSerializer(serializers.ModelSerializer):
    owner = serializers.EmailField(source="owner.email", read_only=True)

    class Meta:
        model = Workspace
        fields = ["id", "name", "kind", "owner", "created_at"]
        read_only_fields = ["id", "owner", "created_at"]


class MembershipSerializer(serializers.ModelSerializer):
    workspace = serializers.PrimaryKeyRelatedField(read_only=True)
    user = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = Membership
        fields = ["id", "workspace", "user", "role", "joined_at"]
        read_only_fields = ["id", "workspace", "user", "joined_at"]


class InvitationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    role = serializers.ChoiceField(choices=Membership.ROLE_CHOICES, default="member")
