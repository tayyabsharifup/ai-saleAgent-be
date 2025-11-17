"""
ASGI config for ai_sales project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

from django.core.asgi import get_asgi_application
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_sales.settings')


# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may be used by the application.
django_asgi_app = get_asgi_application()


async def application(scope, receive, send):
    """
    Main ASGI application.
    """
    if scope["type"] == "http":
        await django_asgi_app(scope, receive, send)
    elif scope["type"] == "websocket":
        # Import these after Django initialization to avoid AppRegistryNotReady error
        from channels.routing import ProtocolTypeRouter, URLRouter
        import apps.home.routing
        import apps.notifications.routing
        from apps.notifications.middleware import TokenAuthMiddleware

        websocket_urlpatterns = apps.home.routing.websocket_urlpatterns + \
            apps.notifications.routing.websocket_urlpatterns

        websocket_application = TokenAuthMiddleware((
            URLRouter(
                websocket_urlpatterns
            )
        ))

        await websocket_application(scope, receive, send)
