import secrets as secrets_lib
import pytest
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import User


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def user(db):
    u = User.objects.create_user(email="test@example.com", language_preference="en")
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
def unverified_user(db):
    u = User.objects.create_user(email="unverified@example.com")
    u.email_verification_token = secrets_lib.token_urlsafe(32)
    u.email_verification_expires_at = timezone.now() + timedelta(hours=24)
    u.save()
    return u
