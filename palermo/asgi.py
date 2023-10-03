import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import re_path
from game_rooms.consumers import RoomConsumer
# Add your consumer import here
# from game_rooms.consumers import YourWebSocketConsumer

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "palermo.settings")

websocket_urlpatterns = [
    re_path(r'ws/game/(?P<room_uuid>[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})/(?P<username>\w+)/$', RoomConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})