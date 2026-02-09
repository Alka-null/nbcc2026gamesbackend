import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nbcc_backend.settings')

from django.core.asgi import get_asgi_application

# Initialize Django ASGI application early to ensure the AppRegistry is populated 
# before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import apps.gameplay.routing

application = ProtocolTypeRouter({
	"http": django_asgi_app,
	"websocket": AuthMiddlewareStack(
		URLRouter(
			apps.gameplay.routing.websocket_urlpatterns
		)
	),
})
