import os

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "automobile.settings"
)

from django.core.asgi import get_asgi_application

django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

from chat.middleware import SuperuserMiddleware
import chat.routing

application = ProtocolTypeRouter({

    "http": django_asgi_app,

    "websocket":
        AuthMiddlewareStack(
            SuperuserMiddleware(
                URLRouter(
                    chat.routing.websocket_urlpatterns
                )
            )
        ),
})