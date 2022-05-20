import datetime
import random
import string
from django.shortcuts import render
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework import status
from users.decorators import login_is_required
from .models import Profile, ResetTable, VerifyTable
from .serializer import  ProfileSerializer
from insta_backend import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
import jwt,json,time
from rest_framework.decorators import api_view
from fuzzywuzzy import fuzz
# Create your views here.

@api_view(['POST'])
def register(request):
    try:
        data=json.loads(request.body)
        email = data['email']
        password = data['password']
        user,created= create_or_get_user(request,email,password)
        if created:
            return Response({'message':f'Account verification link sent to {email}'},status=status.HTTP_201_CREATED)
        return Response({'message':f'User with this email id already exists'},status=status.HTTP_400_BAD_REQUEST)
    except:
        print("error")
        return Response({'message':'some error occured'},status=status.HTTP_400_BAD_REQUEST)

def create_or_get_user(request,email,password=None):
    user = User.objects.filter(email=email).first()
    if(user):
        return user,False
    user = User(username=email, email=email,is_active=False)
    user.set_password(password)
    user.save()
    # create url for verification
    while True:
        hash = ''.join(random.choices(string.ascii_letters, k=20))
        entry = VerifyTable.objects.filter(hash=hash).first()
        if(entry):
            continue
        VerifyTable.objects.create(hash=hash,email=email)
        url = f'{request.build_absolute_uri("/user/")}verify_account/{hash}'
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
        return render(request,'users/success.html',{'m1':'Account Verified','m2':'Thank you for joining us, You can now continue to our app'})
    return render(request,'users/error.html',{'error':'Invalid Account Verification link'})

def generate_token(profile):
    payload = {
        'user_id': profile.user.id,
        'profile_id': profile.id,
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
                if profile.dp:
                    url = profile.dp.url
                else:
                    url = ''
                encoded_jwt = generate_token(profile)
                response = Response({"message":"success","jwt":encoded_jwt,"dp":url,"username":profile.username,"id":profile.id},status=status.HTTP_200_OK)
                response['jwt'] = encoded_jwt
                return response
            return Response({"message":"Please Verify your account first"},status=status.HTTP_400_BAD_REQUEST)
        return Response({"message":"invalid email/password"},status=status.HTTP_400_BAD_REQUEST)
    # except:
    #     print("error")
    #     return Response({"message":"some error occured, please try after sometime"},status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def reset_pass(request):
    data=json.loads(request.body)
    email = data['email']
    user = User.objects.filter(email=email).first()
    if not user:
        return Response({"message":"No such user exists"},status=status.HTTP_400_BAD_REQUEST)
    # create url for verification
    while True:
        hash = ''.join(random.choices(string.ascii_letters, k=20))
        entry = ResetTable.objects.filter(hash=hash).first()
        if(entry):
            continue
        ResetTable.objects.create(hash=hash,email=email)
        url = f'{request.build_absolute_uri("/user/")}forgot_password/{hash}'
        # send email for verification
        send_mail(
        f'Password reset for your instagram account',
        f'Hey User, \nYou have Requested For Password reset for your account. \nHere is the link to reset your account password - {url} \n \n \nThank You \nTeam Instagram.',
        'teaminstaclone@gmail.com',
        [f'{email}']
        )
        print('email sent')
        break
    return Response({"message":f"Password reset link is sent to the {email}"},status=status.HTTP_200_OK)


def forgot_pass(request,hash):
    entry = ResetTable.objects.filter(hash=hash).first()
    if(entry):
        context = {
            'email':entry.email,
            'done':False,
            'error':''
        }
        if request.method == 'POST':
            user = User.objects.filter(email=entry.email).first()
            password = request.POST.get('password')
            password2 = request.POST.get('password2')
            if password != password2:
                context['error'] = "Password Didn't Matched, Try Again"
            else:
                try:
                    context['error'] = ''
                    user.set_password(password)
                    user.save()
                    entry.delete()
                    context['done'] = True
                except:
                    context['error'] = "Some Error Occured, Try Again"
        else:
            context['error'] = ''
            context['done'] = False
        return render(request,'users/reset_pass.html',context)
    return render(request,'users/error.html',{'error':'Invalid Password reset link'})

def get_user_from_request(request):
    token = request.headers['Authorization']
    if not token:
        return Response({"message":"unauthenticated"},status=status.HTTP_401_UNAUTHORIZED)
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return Response({"message":"unauthenticated"},status=status.HTTP_401_UNAUTHORIZED)
    
    expires = int(time.time())
    if(payload['exp'] < expires ):
        return Response({"message":"unauthenticated"},status=status.HTTP_401_UNAUTHORIZED)
    profile = Profile.objects.filter(id = payload['profile_id']).first()
    if(profile):
        return profile
    return Response({"message":"unauthenticated"},status=status.HTTP_401_UNAUTHORIZED)

def set_token(response,profile):
    token = generate_token(profile)
    response['jwt'] = token
    response['Access-Control-Expose-Headers'] = 'jwt'

@api_view(['POST'])
@login_is_required
def check_username(request):
    data=json.loads(request.body)
    username = data['username']
    profile = Profile.objects.filter(username = username).first()
    if not profile:
        return Response({"message":"ok"},status=status.HTTP_200_OK)
    if profile == request.user:
        return Response({"message":"ok"},status=status.HTTP_200_OK)
    return Response({"message":"no"},status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@login_is_required
def update_profile(request):
    serializer = ProfileSerializer(request.user,data=request.data,partial=True)
    
    if not serializer.is_valid():
        response = Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        set_token(response,request.user)
        return response

    if serializer.is_valid():
        serializer.save()
        response = Response(serializer.data,status=status.HTTP_200_OK)
        set_token(response,request.user)
        return response

@api_view(['POST'])
@login_is_required
def follow(request):
    data=json.loads(request.body)
    try:
        you = Profile.objects.filter(username = data['username']).first()
        me = request.user
        if me in you.followers.all():
            you.followers.remove(me)
            message = 'follow'
        else:
            you.followers.add(me)
            message = 'unfollow'
        you.save()
        print(you.username)
        response = Response({"message":message},status=status.HTTP_200_OK)
        set_token(response,me)
        return response
    except:
        response = Response({"message":"no such user"},status=status.HTTP_400_BAD_REQUEST)
        set_token(response,me)
        return response

@api_view(['GET','POST'])
@login_is_required
def get_profile(request):
    try:
        data=json.loads(request.body)
        profile = Profile.objects.filter(username = data['username']).first()
    except:
        profile = request.user
    if profile.dp:
        url = profile.dp.url
    else:
        url = ''
    res = {
        'profile_id':profile.id,
        'username':profile.username,
        'verified':profile.verified,
        'total_posts':profile.posts.all().count(),
        'followers': profile.followers.all().count(),
        'following': profile.following.all().count(),
        'name': profile.name,
        'bio': profile.bio,
        'dp': url,
    }
    if profile != request.user:
        their_followers = profile.followers.all()
        my_followers = request.user.followers.all()
        mutual_friends = their_followers.intersection(my_followers)
        res['first_mutual'] = []
        c = 0
        n = mutual_friends.count()
        while c < 3 and n > 0:
            one = mutual_friends[c]
            if one.dp:
                url = one.dp.url
            else:
                url = ''
            res['first_mutual'].append({
                'username':one.username,
                'url':url,
            })
            c = c+1
            n = n-1
        if c == 3:
            c = 2
        res['mutual_friends'] = mutual_friends.count() - c
        if request.user not in profile.followers.all():
            res['me_following']=False
        else:
            res['me_following']=True
    else:
        res['mutual_friends'] = 0
        res['first_mutual'] = []
        res['me_following']=True
    res['posts'] = []
    res['tags'] = []
    for post in profile.posts.all().order_by('-timedate'):
        res['posts'].append({'id':post.id,'url':post.image.url})
    for post in profile.tagged_to.all().order_by('-timedate'):
        res['tags'].append({'id':post.id,'url':post.image.url})
    jsondata = json.dumps(res)
    response = Response(jsondata,status=status.HTTP_200_OK)
    set_token(response,request.user)
    return response

def get_suggestion(me):
    res = []
    rest_people = Profile.objects.all().difference(me.following.all())
    for profile in rest_people:
        if profile == me:
            continue
        score = 0
        follows = False
        if me in profile.following.all():
            follows = True
            score += 50
        their_followers = profile.followers.all()
        my_followers = me.followers.all()
        mutual_friends = their_followers.intersection(my_followers)
        score += mutual_friends.count() * 2
        if profile.dp:
            url = profile.dp.url
        else:
            url = ''
        if mutual_friends.count() == 0:
            by = ''
        if mutual_friends.count() == 1:
            fname = mutual_friends.first().name
            by = f'{fname}'
        if mutual_friends.count() > 1:
            fname = mutual_friends.first().name
            by = f'{fname} + {mutual_friends.count() - 1} others'
        ele = {
            'id':profile.id,
            'url':url,
            'username':profile.username,
            'name':profile.name,
            'me_following':False,
            'follows_me':follows,
            'followed_by':by,
            'score':score,
        }
        res.append(ele)
    res.sort(key=lambda x : x['score'],reverse=True)
    return res

@api_view(['GET'])
@login_is_required
def follow_suggestion(request):
    res = get_suggestion(request.user)
    jsondata = json.dumps(res)
    response = Response(jsondata,status=status.HTTP_200_OK)
    set_token(response,request.user)
    return response

        
@api_view(['GET','POST'])
@login_is_required
def get_followers(request):
    try:
        data=json.loads(request.body)
        profile = Profile.objects.filter(username = data['username']).first()
    except:
        profile = request.user
    
    res = {
        'mutual': [],
        'followers': [],
        'following': [],
        'suggestion': [],
    }
    for people in profile.followers.all():
        if people.dp:
            url = people.dp.url
        else:
            url = ''
        res['followers'].append({'url':url,'username':people.username,'name':people.name,'me_following': people in request.user.following.all()})
    for people in profile.following.all():
        if people.dp:
            url = people.dp.url
        else:
            url = ''
        res['following'].append({'url':url,'username':people.username,'name':people.name,'me_following': people in request.user.following.all()})
    if request.user != profile:
        their_followers = profile.followers.all()
        my_followers = request.user.followers.all()
        mutual_friends = their_followers.intersection(my_followers)
        for people in mutual_friends:
            if people.dp:
                url = people.dp.url
            else:
                url = ''
            res['mutual'].append({'url':url,'username':people.username,'name':people.name,'me_following': people in request.user.following.all()})
        res['suggestion'] = get_suggestion(request.user)
    jsondata = json.dumps(res)
    response = Response(jsondata,status=status.HTTP_200_OK)
    set_token(response,request.user)
    return response

def search(query, me):
    res = []
    all_profile = Profile.objects.all()
    for profile in all_profile:
        if profile == me:
            continue
        s2 = fuzz.partial_ratio(query, profile.name)
        s3 = fuzz.partial_ratio(query, profile.bio)
        s1 = fuzz.partial_ratio(query, profile.username)
        score = (2 * s1) + (2 * s2) + s3
        if score > 50:
            if profile.dp:
                url = profile.dp.url
            else:
                url = ''
            ele = {
                'id':profile.id,
                'url':url,
                'username':profile.username,
                'name':profile.name,
                'me_following': profile in me.following.all(),
                'score':score
            }
            res.append(ele)
    res.sort(key=lambda x : x['score'],reverse=True)
    return res

@api_view(['POST'])
@login_is_required
def get_search_result(request):
    res = []
    try:
        data=json.loads(request.body)
        res = search(data['query'],request.user)
    except:
        pass
    jsondata = json.dumps(res)
    response = Response(jsondata,status=status.HTTP_200_OK)
    return response
