"""
ASGI config for insta_backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""
import django
import os
from channels.routing import ProtocolTypeRouter,URLRouter
from django.core.asgi import get_asgi_application
from chat import routing as chat_routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'insta_backend.settings')
django.setup()

application = ProtocolTypeRouter(
    {
        # "http": get_asgi_application(),
        "websocket": URLRouter(
                chat_routing.websocket_urlpatterns
            ),
    }
)
