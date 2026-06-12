# === FEATURE: apikeys ===
from django.utils import timezone
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from .models import ApiKey


class ApiKeyAuthentication(BaseAuthentication):
    """Authenticate requests using an 'Authorization: ApiKey <key>' header."""

    keyword = "ApiKey"

    def authenticate(self, request):
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        if not auth_header.startswith(f"{self.keyword} "):
            return None  # Not our scheme — let other authenticators try

        raw_key = auth_header[len(self.keyword) + 1:].strip()
        if not raw_key:
            raise AuthenticationFailed("Empty API key.")

        api_key = ApiKey.authenticate(raw_key)
        if api_key is None:
            raise AuthenticationFailed("Invalid or revoked API key.")

        # Stamp last-used timestamp (best-effort — don't let this crash the request)
        try:
            ApiKey.objects.filter(pk=api_key.pk).update(last_used_at=timezone.now())
        except Exception:
            pass

        return (api_key.user, api_key)

    def authenticate_header(self, request):
        return self.keyword
# === END FEATURE: apikeys ===
