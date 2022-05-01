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
from django.contrib.auth.models import User
import jwt,json,time
from rest_framework.exceptions import AuthenticationFailed
from django.views.decorators.csrf import csrf_exempt
# Create your views here.

def register(request):
    try:
        data=json.loads(request.body)
        email = data['email']
        password = data['password']
        user = create_or_get_user(email,password)
        return Response(f'Account verification link sent to {email}',status=status.HTTP_400_BAD_REQUEST)
    except:
        print("error")
        return Response('some error occured',status=status.HTTP_400_BAD_REQUEST)

def create_or_get_user(email,password=None):
    user = User.objects.filter(email=email).first()
    if(user):
        return user
    user= User(username=email, email=email,password=password,is_active=False)
    user.save()
    # create url for verification
    while True:
        hash = ''.join(random.choices(string.ascii_letters, k=20))
        entry = VerifyTable.objects.filter(hash=hash).first()
        if(entry):
            continue
        VerifyTable.objects.create(hash=hash,email=email)
        url = f'http://localhost:8000/verify/{hash}'
        # send email for verification
        
        break
    return user

def verify_account(request,hash):
    entry = VerifyTable.objects.filter(hash=hash).first()
    if(entry):
        user = User.objects.filter(email=entry.email).first()
        user.is_active = True
        user.save()
        entry.delete()
        return HttpResponse('Your account has been verified, You can now continue to our app😊😊')
    return HttpResponse('Sorry, The Link Was invalid')