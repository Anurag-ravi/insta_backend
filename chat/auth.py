import time
from channels.db import database_sync_to_async
import jwt
from chat.models import AnoUser
from insta_backend import settings
from users.models import Profile

@database_sync_to_async
def get_user(token):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    except:
        return AnoUser()
    expires = int(time.time())
    if(payload['exp'] < expires ):
        return AnoUser()
    try:
        profile = Profile.objects.filter(id = payload['profile_id']).first()
    except:
        return AnoUser()
    return profile

class TokenAuthMiddleware:
    """
    Custom middleware (insecure) that takes user IDs from the query string.
    """

    def __init__(self, app):
        # Store the ASGI application we were passed
        self.app = app

    async def __call__(self, scope, receive, send):
        # Look up user from query string (you should also do things like
        # checking if it is a valid user ID, or if scope["user"] is already
        # populated).
        try:
            token = scope["query_string"].decode().split("=")[1]
        except:
            token = "alkcnalkcnsLkcns"
        scope['user'] = await get_user(token)

        return await self.app(scope, receive, send)