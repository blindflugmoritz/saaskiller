from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_personal_workspace(sender, instance, created, **kwargs):
    """Auto-provision a personal workspace + owner membership on user signup."""
    if not created:
        return
    from workspaces.models import Workspace, Membership

    workspace = Workspace.objects.create(
        owner=instance,
        name="Personal",
        kind="personal",
    )
    Membership.objects.create(workspace=workspace, user=instance, role="owner")
