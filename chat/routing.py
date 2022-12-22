from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path("ws/awc/",consumers.ChatConsumer.as_asgi()),
]