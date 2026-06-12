import re
import logging
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

logger = logging.getLogger(__name__)


def _send(subject, template, context, to):
    html = render_to_string(template, context)
    text = re.sub(r"<[^>]+>", "", html)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    msg = EmailMultiAlternatives(subject, text, settings.DEFAULT_FROM_EMAIL, [to])
    msg.attach_alternative(html, "text/html")
    msg.send()


def send_verification_email(user):
    url = f"{settings.FRONTEND_URL}/auth/verify-email/{user.email_verification_token}"
    lang = user.language_preference or "en"
    subject = (
        "Willkommen — bitte bestätige deine E-Mail"
        if lang == "de"
        else "Welcome — please verify your email"
    )
    try:
        _send(
            subject,
            "users/verify_email.html",
            {"url": url, "lang": lang, "subject": subject, "frontend_url": settings.FRONTEND_URL},
            user.email,
        )
    except Exception:
        logger.exception("Failed to send verification email to %s", user.email)


def send_magic_link_email(user):
    url = f"{settings.FRONTEND_URL}/auth/login/{user.magic_link_token}"
    lang = user.language_preference or "en"
    subject = (
        "Dein Login-Link"
        if lang == "de"
        else "Your login link"
    )
    try:
        _send(
            subject,
            "users/magic_link.html",
            {"url": url, "lang": lang, "subject": subject, "frontend_url": settings.FRONTEND_URL},
            user.email,
        )
    except Exception:
        logger.exception("Failed to send magic link email to %s", user.email)
