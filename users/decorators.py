import jwt,time
from insta_backend import settings
from users.models import Profile
from rest_framework.response import Response

def login_is_required(function):
    def _function(request, *args, **kwargs):
        try:
            token = request.headers['Authorization']
        except:
            return Response({"message":"unauthenticated"},status=401)

        if not token:
            return Response({"message":"unauthenticated"},status=401)
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return Response({"message":"unauthenticated"},status=401)
        
        expires = int(time.time())
        if(payload['exp'] < expires ):
            return Response({"message":"unauthenticated"},status=401)
        try:
            profile = Profile.objects.filter(id = payload['profile_id']).first()
        except:
            return Response({"message":"unauthenticated"},status=401)
        request.user = profile
        return function(request, *args, **kwargs)

    return _function
