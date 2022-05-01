from asyncio.windows_events import NULL
import datetime
from pickle import TRUE
import random
import string
from django.shortcuts import render
from django.contrib.auth import authenticate
from django.http import HttpResponse, JsonResponse
from rest_framework.response import Response
from rest_framework import status
from .models import Profile, VerifyTable
from .serializer import  ProfileSerializer
from insta_backend import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
import jwt,json,time
from rest_framework.decorators import api_view
from rest_framework.exceptions import AuthenticationFailed
from django.views.decorators.csrf import csrf_exempt
# Create your views here.

@api_view(['POST'])
def register(request):
    try:
        data=json.loads(request.body)
        email = data['email']
        password = data['password']
        user,created= create_or_get_user(email,password)
        if created:
            return Response(f'Account verification link sent to {email}',status=status.HTTP_201_CREATED)
        return Response(f'User with this email id already exists',status=status.HTTP_400_BAD_REQUEST)
    except:
        print("error")
        return Response('some error occured',status=status.HTTP_400_BAD_REQUEST)

def create_or_get_user(email,password=None):
    user = User.objects.filter(email=email).first()
    if(user):
        return user,False
    user= User(username=email, email=email,is_active=False)
    user.set_password(password)
    user.save()
    # create url for verification
    while True:
        hash = ''.join(random.choices(string.ascii_letters, k=20))
        entry = VerifyTable.objects.filter(hash=hash).first()
        if(entry):
            continue
        VerifyTable.objects.create(hash=hash,email=email)
        url = f'http://localhost:8000/user/verify_account/{hash}'
        # send email for verification
        send_mail(
        f'verify your email for instagram',
        f'Hey User, \nYou have Successfully Created your Instagram Account. \nHere is the link to verify your account - {url} \n \n \nThank You \nTeam Instagram.',
        'teaminstaclone@gmail.com',
        [f'{email}']
        )
        print('email sent')
        break
    return user,True

@api_view(['GET'])
def verify_account(request,hash):
    entry = VerifyTable.objects.filter(hash=hash).first()
    if(entry):
        user = User.objects.filter(email=entry.email).first()
        user.is_active = True
        user.save()
        Profile.objects.create(user=user,username=user.email)
        entry.delete()
        return HttpResponse('Your account has been verified, You can now continue to our app😊😊')
    return HttpResponse('Sorry, The Link Was invalid')

def generate_token(profile):
    if profile.dp:
        url = profile.dp.url
    else:
        url = NULL
    payload = {
        'user_id': profile.user.id,
        'profile_id': profile.id,
        'username': profile.username,
        'name': profile.name,
        'bio': profile.bio,
        'verified': profile.verified,
        'dp': url,
        'followers': profile.followers.all().count(),
        'following': profile.following.all().count(),
        'exp':datetime.datetime.utcnow()+ datetime.timedelta(days=30),
        'iat':datetime.datetime.utcnow()
    }
    encoded_jwt = jwt.encode(payload,settings.SECRET_KEY , algorithm="HS256")
    return encoded_jwt

@api_view(['POST'])
def login(request):
    # try:
        data=json.loads(request.body)
        email = data['email']
        password = data['password']
        user1 = User.objects.filter(email=email).first()
        if user1:
            if not user1.is_active:
                return Response({"message":"Please Verify your account first"},status=status.HTTP_400_BAD_REQUEST)
        user = authenticate(username=email, password=password)
        if user is not None:
            if user.is_active:
                profile = Profile.objects.filter(user=user).first()
                encoded_jwt = generate_token(profile)
                response = Response({"message":"success","jwt":encoded_jwt},status=status.HTTP_200_OK)
                response['jwt'] = encoded_jwt
                return response
            return Response({"message":"Please Verify your account first"},status=status.HTTP_400_BAD_REQUEST)
        return Response({"message":"invalid email/password"},status=status.HTTP_400_BAD_REQUEST)
    # except:
    #     print("error")
    #     return Response('some error occured',status=status.HTTP_400_BAD_REQUEST)