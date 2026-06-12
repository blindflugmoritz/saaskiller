# === FEATURE: websockets ===
from django.urls import path

from .consumers import NotificationConsumer

websocket_urlpatterns = [
    path("ws/notifications/", NotificationConsumer.as_asgi()),
]
# === END FEATURE: websockets ===
