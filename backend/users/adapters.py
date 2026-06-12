from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class AccountAdapter(DefaultAccountAdapter):
    """Custom account adapter — disables allauth's built-in signup page
    since we handle signup ourselves via the API."""

    def is_open_for_signup(self, request):
        return False


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    """Custom social account adapter.

    - Links incoming social accounts to existing users by email.
    - Marks email as verified after a successful OAuth login (Google has
      already verified the email on their end).
    """

    def pre_social_login(self, request, sociallogin):
        """Link social account to existing user by email if one exists."""
        if sociallogin.is_existing:
            return

        email = sociallogin.account.extra_data.get("email", "").lower().strip()
        if not email:
            return

        from users.models import User

        try:
            user = User.objects.get(email=email)
            sociallogin.connect(request, user)
        except User.DoesNotExist:
            pass

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        # Google has already verified the email
        if not user.email_verified:
            user.email_verified = True
            user.save(update_fields=["email_verified"])
        return user
