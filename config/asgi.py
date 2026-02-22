"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import ORBIT.routing  # routing.py が ORBIT アプリ内にある場合

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings') # ここも config に！

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            ORBIT.routing.websocket_urlpatterns
        )
    ),
})