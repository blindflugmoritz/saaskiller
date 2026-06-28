import secrets
import logging
from django.utils import timezone
from datetime import timedelta
from django.db import transaction
from rest_framework.decorators import api_view, authentication_classes, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.throttling import AnonRateThrottle
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .models import User
from .serializers import UserSerializer, SignupSerializer, UserUpdateSerializer, MagicLinkRequestSerializer
from .utils import send_verification_email, send_magic_link_email

logger = logging.getLogger(__name__)


class SignupThrottle(AnonRateThrottle):
    scope = "signup"


class MagicLinkThrottle(AnonRateThrottle):
    scope = "magic_link"


class LoginThrottle(AnonRateThrottle):
    scope = "login"


class ResendVerificationThrottle(AnonRateThrottle):
    scope = "resend_verification"


def _issue_jwt(user):
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token), str(refresh)


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
@throttle_classes([SignupThrottle])
def signup(request):
    email = request.data.get("email", "").lower().strip()

    # Existing user — send magic link instead
    try:
        user = User.objects.get(email=email)
        token = secrets.token_urlsafe(32)
        with transaction.atomic():
            user.magic_link_token = token
            user.magic_link_expires_at = timezone.now() + timedelta(minutes=15)
            user.save(update_fields=["magic_link_token", "magic_link_expires_at"])
        send_magic_link_email(user)
        # Anti-enumeration: same response as new signup
        return Response(
            {"message": "If this email is new, an account was created. Check your email."},
            status=status.HTTP_200_OK,
        )
    except User.DoesNotExist:
        pass

    serializer = SignupSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    token = secrets.token_urlsafe(32)
    user = User.objects.create_user(
        email=serializer.validated_data["email"],
        language_preference=serializer.validated_data.get("language_preference", "en"),
    )
    with transaction.atomic():
        user.email_verification_token = token
        user.email_verification_expires_at = timezone.now() + timedelta(hours=24)
        user.save(update_fields=["email_verification_token", "email_verification_expires_at"])

    send_verification_email(user)
    return Response(
        {"user": UserSerializer(user).data, "message": "Account created. Please check your email."},
        status=status.HTTP_201_CREATED,
    )


class VerifyEmailThrottle(AnonRateThrottle):
    scope = "verify_email"


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
@throttle_classes([VerifyEmailThrottle])
def verify_email(request, token):
    try:
        user = User.objects.get(email_verification_token=token)
    except User.DoesNotExist:
        return Response({"error": "Invalid verification token."}, status=status.HTTP_400_BAD_REQUEST)

    if user.email_verification_expires_at and user.email_verification_expires_at < timezone.now():
        return Response(
            {"error": "Verification link has expired. Please request a new one.", "expired": True},
            status=status.HTTP_410_GONE,
        )

    with transaction.atomic():
        user.email_verified = True
        user.email_verification_token = None
        user.email_verification_expires_at = None
        user.save(update_fields=["email_verified", "email_verification_token", "email_verification_expires_at"])

    access, refresh = _issue_jwt(user)
    return Response(
        {"message": "Email verified.", "access": access, "refresh": refresh, "user": UserSerializer(user).data},
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
@throttle_classes([ResendVerificationThrottle])
def resend_verification(request):
    email = request.data.get("email", "").lower().strip()
    try:
        user = User.objects.get(email=email, email_verified=False)
        token = secrets.token_urlsafe(32)
        with transaction.atomic():
            user.email_verification_token = token
            user.email_verification_expires_at = timezone.now() + timedelta(hours=24)
            user.save(update_fields=["email_verification_token", "email_verification_expires_at"])
        send_verification_email(user)
    except User.DoesNotExist:
        pass  # Anti-enumeration: always 200
    return Response(
        {"message": "If this email is unverified, a new verification link has been sent."},
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
@throttle_classes([MagicLinkThrottle])
def request_magic_link(request):
    serializer = MagicLinkRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    email = serializer.validated_data["email"].lower().strip()
    try:
        user = User.objects.get(email=email)
        token = secrets.token_urlsafe(32)
        with transaction.atomic():
            user.magic_link_token = token
            user.magic_link_expires_at = timezone.now() + timedelta(minutes=15)
            user.save(update_fields=["magic_link_token", "magic_link_expires_at"])
        send_magic_link_email(user)
    except User.DoesNotExist:
        pass  # Anti-enumeration: always 200
    return Response(
        {"message": "If this email is registered, a login link has been sent."},
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
@throttle_classes([LoginThrottle])
def login_with_magic_link(request):
    token = request.data.get("token")
    if not token:
        return Response({"error": "Token required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(
            magic_link_token=token,
            magic_link_expires_at__gt=timezone.now(),
        )
    except User.DoesNotExist:
        return Response({"error": "Invalid or expired link."}, status=status.HTTP_400_BAD_REQUEST)

    with transaction.atomic():
        user.magic_link_token = None
        user.magic_link_expires_at = None
        if not user.email_verified:
            user.email_verified = True
        # Clear dangling verification token — magic link serves as email proof
        user.email_verification_token = None
        user.email_verification_expires_at = None
        user.save(update_fields=[
            "magic_link_token", "magic_link_expires_at", "email_verified",
            "email_verification_token", "email_verification_expires_at",
        ])

    access, refresh = _issue_jwt(user)
    return Response(
        {"user": UserSerializer(user).data, "access": access, "refresh": refresh},
        status=status.HTTP_200_OK,
    )


@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
def current_user(request):
    if request.method == "GET":
        return Response(UserSerializer(request.user).data)

    serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    serializer.save()
    return Response(UserSerializer(request.user).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    """Blacklist the presented refresh token so it cannot be reused."""
    refresh_token = request.data.get("refresh")
    if refresh_token:
        try:
            RefreshToken(refresh_token).blacklist()
        except TokenError:
            pass  # Already blacklisted or invalid — still 200
    return Response(status=status.HTTP_200_OK)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_account(request):
    # Blacklist refresh token before deleting so it cannot outlive the account
    refresh_token = request.data.get("refresh")
    if refresh_token:
        try:
            RefreshToken(refresh_token).blacklist()
        except TokenError:
            pass
    request.user.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
