try:
    import stripe  # noqa: F401
    from billing.models import Plan, Subscription
except ImportError:
    import pytest
    pytestmark = pytest.mark.skip(reason="billing/stripe feature not installed")
    Plan = None
    Subscription = None

import json
import pytest
from datetime import timedelta
from django.utils import timezone
from unittest.mock import patch, MagicMock


# ── Fixtures ──────────────────────────────────────────────────────────────────

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


# ── Webhook fixtures & helpers ────────────────────────────────────────────────

@pytest.fixture
def subscription(db, user):
    return Subscription.objects.create(
        user=user,
        stripe_subscription_id="sub_test123",
        stripe_customer_id="cus_test123",
        status="active",
        current_period_end=timezone.now() + timedelta(days=30),
    )


def _post_webhook(client, event_type, data_object):
    """Post a mocked Stripe webhook event and return the response."""
    event = {"type": event_type, "data": {"object": data_object}}
    with patch("billing.views.stripe.Webhook.construct_event", return_value=event):
        return client.post(
            "/api/billing/webhook/",
            data=json.dumps({"dummy": True}),
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="t=1,v1=fakesig",
        )


# ── Webhook tests ─────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_webhook_invalid_signature(client):
    """A bad Stripe signature returns 400."""
    with patch(
        "billing.views.stripe.Webhook.construct_event",
        side_effect=stripe.error.SignatureVerificationError("bad sig", "t=1,v1=x"),
    ):
        resp = client.post(
            "/api/billing/webhook/",
            data=json.dumps({}),
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="t=1,v1=badsig",
        )
    assert resp.status_code == 400


@pytest.mark.django_db
def test_webhook_invalid_payload(client):
    """An unparseable payload returns 400."""
    with patch(
        "billing.views.stripe.Webhook.construct_event",
        side_effect=ValueError("invalid payload"),
    ):
        resp = client.post(
            "/api/billing/webhook/",
            data="not-json",
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="t=1,v1=fakesig",
        )
    assert resp.status_code == 400


@pytest.mark.django_db
def test_webhook_subscription_updated(client, subscription):
    """customer.subscription.updated syncs status to past_due."""
    data_object = {
        "id": "sub_test123",
        "customer": "cus_test123",
        "status": "past_due",
        "current_period_end": int((timezone.now() + timedelta(days=30)).timestamp()),
        "cancel_at_period_end": False,
    }
    resp = _post_webhook(client, "customer.subscription.updated", data_object)
    assert resp.status_code == 200
    subscription.refresh_from_db()
    assert subscription.status == "past_due"


@pytest.mark.django_db
def test_webhook_subscription_deleted(client, subscription):
    """customer.subscription.deleted syncs status to canceled."""
    data_object = {
        "id": "sub_test123",
        "customer": "cus_test123",
        "status": "canceled",
        "current_period_end": int((timezone.now() + timedelta(days=30)).timestamp()),
        "cancel_at_period_end": False,
    }
    resp = _post_webhook(client, "customer.subscription.deleted", data_object)
    assert resp.status_code == 200
    subscription.refresh_from_db()
    assert subscription.status == "canceled"


@pytest.mark.django_db
def test_webhook_invoice_payment_failed(client, subscription):
    """invoice.payment_failed sets subscription status to past_due."""
    data_object = {
        "id": "in_test123",
        "subscription": "sub_test123",
    }
    resp = _post_webhook(client, "invoice.payment_failed", data_object)
    assert resp.status_code == 200
    subscription.refresh_from_db()
    assert subscription.status == "past_due"


@pytest.mark.django_db
def test_webhook_unknown_event_ignored(client, subscription):
    """An unrecognised event type is silently accepted with 200."""
    data_object = {"id": "evt_unknown"}
    resp = _post_webhook(client, "some.unknown.event", data_object)
    assert resp.status_code == 200
