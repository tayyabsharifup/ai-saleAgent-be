"""
ASGI config for ai_sales project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_sales.settings')

# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may need it.
django_asgi_app = get_asgi_application()

# Import routing modules after Django is configured
async def application(scope, receive, send):
    from apps.home.routing import websocket_urlpatterns as home_websocket_urlpatterns
    from apps.notifications.routing import websocket_urlpatterns as notifications_websocket_urlpatterns
    
    if scope["type"] == "http":
        # Django HTTP application
        await django_asgi_app(scope, receive, send)
    elif scope["type"] == "websocket":
        # WebSocket application
        application = AuthMiddlewareStack(
            URLRouter(
                home_websocket_urlpatterns + notifications_websocket_urlpatterns
            )
        )
        await application(scope, receive, send)
    else:
        raise RuntimeError(f"Unknown scope type {scope['type']}")

# Keep the module-level 'application' variable for backwards compatibility
application = application
