# === FEATURE: stripe ===
from django.urls import path
from .views import (
    ListPlansView,
    CurrentSubscriptionView,
    CreateCheckoutSessionView,
    CreatePortalSessionView,
    StripeWebhookView,
)

urlpatterns = [
    path("plans/", ListPlansView.as_view(), name="billing-plans"),
    path("subscription/", CurrentSubscriptionView.as_view(), name="billing-subscription"),
    path("checkout/", CreateCheckoutSessionView.as_view(), name="billing-checkout"),
    path("portal/", CreatePortalSessionView.as_view(), name="billing-portal"),
    path("webhook/", StripeWebhookView.as_view(), name="billing-webhook"),
]
# === END FEATURE: stripe ===
