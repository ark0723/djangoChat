"""
ASGI config for chatting project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

from chat.routing import websocket_urlpatterns
import chat.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chatting.settings")
# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()
# ProtocolTypeRouter will first inspect the type of connection
application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        # If it is a WebSocket connection (ws:// or wss://),
        # the connection will be given to the AuthMiddlewareStack
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(URLRouter(websocket_urlpatterns))
        ),
    }
)
