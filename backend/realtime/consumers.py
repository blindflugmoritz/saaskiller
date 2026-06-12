# === FEATURE: websockets ===
import json

from channels.generic.websocket import AsyncWebsocketConsumer


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for per-user notifications.

    Connection requires a valid JWT access token passed as a query parameter:
        ws://host/ws/notifications/?token=<access_token>

    The token is validated by JWTAuthMiddleware before reaching this consumer.
    Authenticated user is available via self.scope["user"].

    Group name: notifications_<user_pk>
    Send a notification to a user from anywhere in the backend:

        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"notifications_{user.pk}",
            {"type": "notification.send", "payload": {...}},
        )
    """

    async def connect(self) -> None:
        user = self.scope.get("user")

        if user is None or not user.is_authenticated:
            await self.close(code=4001)
            return

        self.group_name = f"notifications_{user.pk}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code: int) -> None:
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data: str = "", bytes_data: bytes = b"") -> None:
        """Echo the received message back to the sender (for testing)."""
        try:
            data = json.loads(text_data)
        except (json.JSONDecodeError, TypeError):
            data = {"raw": text_data}

        await self.send(text_data=json.dumps({"echo": data}))

    # ── Channel layer event handlers ──────────────────────────────────────────

    async def notification_send(self, event: dict) -> None:
        """Forward a group message to the WebSocket client."""
        payload = event.get("payload", {})
        await self.send(text_data=json.dumps(payload))
# === END FEATURE: websockets ===
