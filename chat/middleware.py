from channels.db import database_sync_to_async
from superuser.models import Superadmin


@database_sync_to_async
def get_superuser(superuser_id):
    try:
        return Superadmin.objects.get(id=superuser_id)
    except Superadmin.DoesNotExist:
        return None


class SuperuserMiddleware:

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):

        scope["superuser"] = None

        session = scope.get("session")

        print("Session:", session)

        if session:
            print("super_user_id:", session.get("super_user_id"))

            superuser_id = session.get("super_user_id")

            if superuser_id:
                scope["superuser"] = await get_superuser(superuser_id)

        print("Loaded Superuser:", scope["superuser"])

        return await self.inner(scope, receive, send)