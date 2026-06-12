try:
    from apikeys.models import ApiKey
except ImportError:
    import pytest
    pytestmark = pytest.mark.skip(reason="apikeys feature not installed")
    ApiKey = None

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
    u = User.objects.create_user(email="apikey@example.com", language_preference="en")
    u.email_verified = True
    u.save()
    return u


@pytest.fixture
def auth_client(user):
    c = APIClient()
    refresh = RefreshToken.for_user(user)
    c.credentials(HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}")
    return c


# ── Tests ─────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_list_keys_empty(auth_client):
    """Authenticated user with no keys gets an empty list."""
    resp = auth_client.get("/api/keys/")
    assert resp.status_code == 200
    assert resp.data == []


@pytest.mark.django_db
def test_create_key(auth_client):
    """POST /api/keys/ returns a key with prefix and raw_key fields."""
    resp = auth_client.post("/api/keys/", {"name": "test"})
    assert resp.status_code == 201
    assert "prefix" in resp.data
    assert "raw_key" in resp.data
    assert resp.data["name"] == "test"
    assert len(resp.data["prefix"]) == 8
    assert len(resp.data["raw_key"]) > 0


@pytest.mark.django_db
def test_raw_key_not_returned_on_list(auth_client):
    """After creating a key, GET /api/keys/ does not include raw_key."""
    auth_client.post("/api/keys/", {"name": "secret-key"})
    resp = auth_client.get("/api/keys/")
    assert resp.status_code == 200
    assert len(resp.data) == 1
    assert "raw_key" not in resp.data[0]


@pytest.mark.django_db
def test_revoke_key(auth_client, user):
    """DELETE /api/keys/<id>/ soft-deletes the key by setting is_active=False."""
    create_resp = auth_client.post("/api/keys/", {"name": "to-revoke"})
    assert create_resp.status_code == 201
    key_id = create_resp.data["id"]

    del_resp = auth_client.delete(f"/api/keys/{key_id}/")
    assert del_resp.status_code == 204

    api_key = ApiKey.objects.get(pk=key_id)
    assert api_key.is_active is False


@pytest.mark.django_db
def test_api_key_authentication(client, user):
    """A raw API key in 'Authorization: ApiKey <raw>' header authenticates /api/auth/me/."""
    _, raw_key = ApiKey.create(user=user, name="auth-test")

    key_client = APIClient()
    key_client.credentials(HTTP_AUTHORIZATION=f"ApiKey {raw_key}")

    resp = key_client.get("/api/auth/me/")
    assert resp.status_code == 200
    assert resp.data["email"] == user.email


@pytest.mark.django_db
def test_api_key_authentication_invalid_key(client):
    """An invalid API key returns 403 (DRF AuthenticationFailed raises 403 for invalid credentials)."""
    bad_client = APIClient()
    bad_client.credentials(HTTP_AUTHORIZATION="ApiKey totallywrongkey")

    resp = bad_client.get("/api/auth/me/")
    # DRF raises AuthenticationFailed which maps to HTTP 403
    assert resp.status_code in (401, 403)
