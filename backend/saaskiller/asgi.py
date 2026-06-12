"""
ASGI config for saaskiller project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "saaskiller.settings")

# Base Django ASGI application — always present
django_asgi_app = get_asgi_application()

# === FEATURE: websockets ===
try:
    from channels.routing import ProtocolTypeRouter, URLRouter
    from realtime.middleware import JWTAuthMiddleware
    from realtime.routing import websocket_urlpatterns

    application = ProtocolTypeRouter(
        {
            "http": django_asgi_app,
            "websocket": JWTAuthMiddleware(
                URLRouter(websocket_urlpatterns)
            ),
        }
    )
except ImportError:
    # channels not installed — fall back to plain ASGI
    application = django_asgi_app
# === END FEATURE: websockets ===
