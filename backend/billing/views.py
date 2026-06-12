# === FEATURE: stripe ===
import stripe
from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from datetime import datetime, timezone as dt_timezone

from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Plan, Subscription
from .serializers import PlanSerializer, SubscriptionSerializer


def _get_stripe_client():
    stripe.api_key = settings.STRIPE_SECRET_KEY
    return stripe


class ListPlansView(APIView):
    """GET /api/billing/plans/ — list all active plans, no auth required."""

    permission_classes = [AllowAny]

    def get(self, request):
        plans = Plan.objects.filter(is_active=True)
        serializer = PlanSerializer(plans, many=True)
        return Response(serializer.data)


class CurrentSubscriptionView(APIView):
    """GET /api/billing/subscription/ — return user's active subscription or null."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        subscription = (
            Subscription.objects.filter(
                user=request.user,
                status__in=["trialing", "active", "past_due"],
            )
            .order_by("-created_at")
            .first()
        )
        if subscription is None:
            return Response(None)
        serializer = SubscriptionSerializer(subscription)
        return Response(serializer.data)


class CreateCheckoutSessionView(APIView):
    """POST /api/billing/checkout/ — create a Stripe Checkout session, return {url}."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        price_id = request.data.get("price_id")
        if not price_id:
            return Response(
                {"detail": "price_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        _get_stripe_client()

        success_url = f"{settings.FRONTEND_URL}/billing/success?session_id={{CHECKOUT_SESSION_ID}}"
        cancel_url = f"{settings.FRONTEND_URL}/billing/canceled"

        try:
            session = stripe.checkout.Session.create(
                mode="subscription",
                line_items=[{"price": price_id, "quantity": 1}],
                success_url=success_url,
                cancel_url=cancel_url,
                customer_email=request.user.email,
                metadata={"user_id": str(request.user.pk)},
            )
        except stripe.error.StripeError as exc:
            return Response(
                {"detail": str(exc.user_message or exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"url": session.url})


class CreatePortalSessionView(APIView):
    """POST /api/billing/portal/ — create a Stripe billing portal session, return {url}."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        subscription = (
            Subscription.objects.filter(
                user=request.user,
                status__in=["trialing", "active", "past_due"],
            )
            .order_by("-created_at")
            .first()
        )

        if subscription is None:
            return Response(
                {"detail": "No active subscription found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        _get_stripe_client()

        return_url = f"{settings.FRONTEND_URL}/billing"

        try:
            session = stripe.billing_portal.Session.create(
                customer=subscription.stripe_customer_id,
                return_url=return_url,
            )
        except stripe.error.StripeError as exc:
            return Response(
                {"detail": str(exc.user_message or exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"url": session.url})


class StripeWebhookView(APIView):
    """POST /api/billing/webhook/ — handle Stripe webhook events."""

    permission_classes = [AllowAny]
    authentication_classes = []  # skip JWT for webhooks

    def post(self, request):
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")
        webhook_secret = getattr(settings, "STRIPE_WEBHOOK_SECRET", "")

        _get_stripe_client()

        try:
            event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
        except ValueError:
            return HttpResponse("Invalid payload", status=400)
        except stripe.error.SignatureVerificationError:
            return HttpResponse("Invalid signature", status=400)

        event_type = event["type"]
        data_object = event["data"]["object"]

        if event_type in ("customer.subscription.updated", "customer.subscription.deleted"):
            _handle_subscription_event(data_object)
        elif event_type == "invoice.payment_failed":
            _handle_invoice_payment_failed(data_object)

        return HttpResponse(status=200)


def _handle_subscription_event(stripe_sub):
    """Sync a Stripe subscription object into our Subscription model."""
    stripe_sub_id = stripe_sub["id"]
    customer_id = stripe_sub["customer"]
    raw_status = stripe_sub["status"]
    period_end_ts = stripe_sub["current_period_end"]
    cancel_at_period_end = stripe_sub.get("cancel_at_period_end", False)

    period_end_dt = datetime.fromtimestamp(period_end_ts, tz=dt_timezone.utc)

    Subscription.objects.filter(stripe_subscription_id=stripe_sub_id).update(
        stripe_customer_id=customer_id,
        status=raw_status,
        current_period_end=period_end_dt,
        cancel_at_period_end=cancel_at_period_end,
    )


def _handle_invoice_payment_failed(invoice):
    """Mark subscription as past_due when a payment fails."""
    stripe_sub_id = invoice.get("subscription")
    if stripe_sub_id:
        Subscription.objects.filter(stripe_subscription_id=stripe_sub_id).update(
            status="past_due"
        )
# === END FEATURE: stripe ===
