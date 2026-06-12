try:
    import stripe  # noqa: F401
    from billing.models import Plan, Subscription
except ImportError:
    import pytest
    pytestmark = pytest.mark.skip(reason="billing/stripe feature not installed")
    Plan = None
    Subscription = None

import pytest
from unittest.mock import patch, MagicMock
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import User


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def user(db):
    u = User.objects.create_user(email="billing@example.com", language_preference="en")
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
def active_plan(db):
    return Plan.objects.create(
        name="Pro",
        stripe_price_id="price_test_pro",
        amount_cents=1999,
        currency="usd",
        interval="month",
        is_active=True,
    )


# ── Tests ─────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_list_plans_unauthenticated(client, active_plan):
    """GET /api/billing/plans/ is public and returns 200."""
    resp = client.get("/api/billing/plans/")
    assert resp.status_code == 200
    assert isinstance(resp.data, list)
    assert any(p["name"] == "Pro" for p in resp.data)


@pytest.mark.django_db
def test_current_subscription_no_sub(auth_client):
    """Authenticated user with no subscription gets null back."""
    resp = auth_client.get("/api/billing/subscription/")
    assert resp.status_code == 200
    assert resp.data is None


@pytest.mark.django_db
def test_checkout_requires_auth(client):
    """Unauthenticated POST /api/billing/checkout/ returns 401."""
    resp = client.post("/api/billing/checkout/", {"price_id": "price_test_pro"})
    assert resp.status_code == 401


@pytest.mark.django_db
@patch("stripe.checkout.Session.create")
def test_checkout_returns_url(mock_create, auth_client, active_plan, settings):
    """Authenticated checkout with valid price_id returns a redirect URL."""
    settings.STRIPE_SECRET_KEY = "sk_test_fake"
    settings.FRONTEND_URL = "http://localhost:5173"

    mock_session = MagicMock()
    mock_session.url = "https://checkout.stripe.com/pay/cs_test_fake"
    mock_create.return_value = mock_session

    resp = auth_client.post("/api/billing/checkout/", {"price_id": active_plan.stripe_price_id})
    assert resp.status_code == 200
    assert resp.data["url"] == "https://checkout.stripe.com/pay/cs_test_fake"
    mock_create.assert_called_once()
