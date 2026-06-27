import secrets as secrets_lib
import pytest
from django.utils import timezone
from datetime import timedelta
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import User


# ── Signup ────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_signup_creates_user(client):
    resp = client.post("/api/auth/signup/", {"email": "new@example.com", "language_preference": "en"})
    assert resp.status_code == 201
    assert User.objects.filter(email="new@example.com").exists()


@pytest.mark.django_db
def test_signup_existing_user_sends_magic_link(client, user, mailoutbox):
    resp = client.post("/api/auth/signup/", {"email": user.email})
    assert resp.status_code == 200
    assert resp.data["existing"] is True
    assert len(mailoutbox) == 1
    user.refresh_from_db()
    assert user.magic_link_token is not None


@pytest.mark.django_db
def test_signup_invalid_email(client):
    resp = client.post("/api/auth/signup/", {"email": "notanemail"})
    assert resp.status_code == 400


# ── Email Verification ────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_verify_email_success(client, unverified_user):
    resp = client.post(f"/api/auth/verify-email/{unverified_user.email_verification_token}/")
    assert resp.status_code == 200
    assert "access" in resp.data
    assert "refresh" in resp.data
    unverified_user.refresh_from_db()
    assert unverified_user.email_verified is True
    assert unverified_user.email_verification_token is None


@pytest.mark.django_db
def test_verify_email_invalid_token(client):
    resp = client.post("/api/auth/verify-email/badtoken/")
    assert resp.status_code == 400


@pytest.mark.django_db
def test_verify_email_expired_token(client, unverified_user):
    unverified_user.email_verification_expires_at = timezone.now() - timedelta(hours=1)
    unverified_user.save()
    resp = client.post(f"/api/auth/verify-email/{unverified_user.email_verification_token}/")
    assert resp.status_code == 410
    assert resp.data["expired"] is True


# ── Magic Link ────────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_request_magic_link_known_user(client, user, mailoutbox):
    resp = client.post("/api/auth/request-magic-link/", {"email": user.email})
    assert resp.status_code == 200
    assert len(mailoutbox) == 1
    user.refresh_from_db()
    assert user.magic_link_token is not None


@pytest.mark.django_db
def test_request_magic_link_unknown_user_still_200(client):
    resp = client.post("/api/auth/request-magic-link/", {"email": "ghost@example.com"})
    assert resp.status_code == 200  # Anti-enumeration


@pytest.mark.django_db
def test_login_with_magic_link_success(client, user):
    token = secrets_lib.token_urlsafe(32)
    user.magic_link_token = token
    user.magic_link_expires_at = timezone.now() + timedelta(minutes=15)
    user.save()

    resp = client.post("/api/auth/login/", {"token": token})
    assert resp.status_code == 200
    assert "access" in resp.data
    assert "refresh" in resp.data
    user.refresh_from_db()
    assert user.magic_link_token is None


@pytest.mark.django_db
def test_login_with_magic_link_expired(client, user):
    token = secrets_lib.token_urlsafe(32)
    user.magic_link_token = token
    user.magic_link_expires_at = timezone.now() - timedelta(minutes=1)
    user.save()

    resp = client.post("/api/auth/login/", {"token": token})
    assert resp.status_code == 400


@pytest.mark.django_db
def test_login_with_magic_link_verifies_email(client):
    u = User.objects.create_user(email="notverified@example.com")
    token = secrets_lib.token_urlsafe(32)
    u.magic_link_token = token
    u.magic_link_expires_at = timezone.now() + timedelta(minutes=15)
    u.save()

    client.post("/api/auth/login/", {"token": token})
    u.refresh_from_db()
    assert u.email_verified is True


# ── Current User ──────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_me_returns_user(auth_client, user):
    resp = auth_client.get("/api/auth/me/")
    assert resp.status_code == 200
    assert resp.data["email"] == user.email


@pytest.mark.django_db
def test_me_requires_auth(client):
    resp = client.get("/api/auth/me/")
    assert resp.status_code == 401


@pytest.mark.django_db
def test_me_patch_language(auth_client, user):
    resp = auth_client.patch("/api/auth/me/", {"language_preference": "de"})
    assert resp.status_code == 200
    user.refresh_from_db()
    assert user.language_preference == "de"


# ── Delete Account ────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_delete_account(auth_client, user):
    resp = auth_client.delete("/api/auth/me/delete/")
    assert resp.status_code == 204
    assert not User.objects.filter(email=user.email).exists()


# ── Health ────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_health(client):
    resp = client.get("/api/health/")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
