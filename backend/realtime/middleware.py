# === FEATURE: websockets ===
"""
JWT authentication middleware for Django Channels.

Reads an access token from the WebSocket query string (?token=<jwt>),
validates it with SimpleJWT, and populates scope["user"].

Usage in asgi.py:
    from realtime.middleware import JWTAuthMiddleware

    application = ProtocolTypeRouter({
        "websocket": JWTAuthMiddleware(URLRouter(websocket_urlpatterns)),
    })
"""
from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()


@database_sync_to_async
def _get_user(token_key: str):
    """Validate JWT and return the corresponding User, or AnonymousUser."""
    try:
        token = AccessToken(token_key)
        user_id = token["user_id"]
        return User.objects.get(pk=user_id)
    except (InvalidToken, TokenError, User.DoesNotExist, KeyError):
        return AnonymousUser()


class JWTAuthMiddleware:
    """
    ASGI middleware that authenticates WebSocket connections via a JWT
    access token supplied in the query string (?token=<access_token>).

    Populates scope["user"]. Unauthenticated connections receive an
    AnonymousUser; the consumer is responsible for closing them.
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "websocket":
            query_string = scope.get("query_string", b"").decode()
            params = parse_qs(query_string)
            token_list = params.get("token", [])
            token_key = token_list[0] if token_list else ""

            scope["user"] = await _get_user(token_key) if token_key else AnonymousUser()

        return await self.app(scope, receive, send)
# === END FEATURE: websockets ===
