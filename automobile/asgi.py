from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application

from services.routing import websocket_urlpatterns
from services.middleware import SuperadminAuthMiddleware

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({

    "http": django_asgi_app,

    "websocket": SuperadminAuthMiddleware(

        AuthMiddlewareStack(

            URLRouter(

                websocket_urlpatterns

            )

        )

    ),

})