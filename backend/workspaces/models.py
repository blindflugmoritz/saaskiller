import uuid
from django.conf import settings
from django.db import models
from django.utils import timezone


class Workspace(models.Model):
    KIND_CHOICES = [
        ("personal", "Personal"),
        ("family", "Family"),
        ("school", "School"),
        ("business", "Business"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, default="Personal")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_workspaces",
    )
    kind = models.CharField(max_length=20, choices=KIND_CHOICES, default="personal")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "sk_workspaces"

    def __str__(self):
        return f"{self.name} ({self.kind})"


class Membership(models.Model):
    ROLE_CHOICES = [
        ("owner", "Owner"),
        ("admin", "Admin"),
        ("member", "Member"),
        ("viewer", "Viewer"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="owner")
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "sk_memberships"
        unique_together = [("workspace", "user")]

    def __str__(self):
        return f"{self.user} — {self.workspace} ({self.role})"


INVITATION_EXPIRY_DAYS = 7


class Invitation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name="invitations")
    invited_email = models.EmailField()
    role = models.CharField(max_length=20, choices=Membership.ROLE_CHOICES, default="member")
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_invitations",
    )
    accepted_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "sk_invitations"

    def __str__(self):
        return f"Invite {self.invited_email} → {self.workspace} ({self.role})"

    def is_expired(self):
        return self.expires_at is not None and self.expires_at < timezone.now()

    def accept(self, user):
        """Create membership and mark invitation accepted."""
        from django.db import transaction
        with transaction.atomic():
            Membership.objects.get_or_create(
                workspace=self.workspace,
                user=user,
                defaults={"role": self.role},
            )
            self.accepted_at = timezone.now()
            self.save(update_fields=["accepted_at"])
