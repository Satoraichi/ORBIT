from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/instruction/(?P<event_slug>[\w-]+)/$', consumers.InstructionConsumer.as_asgi()),
]