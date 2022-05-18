import datetime
from functools import partial
import re
from pytz import utc
from rest_framework.response import Response
from rest_framework import status
from users.decorators import login_is_required
from users.views import set_token
from .models import Post,Comment,Story,Activity
from .serializer import  PostSerializer,CommentSerializer,StorySerializer,ActivitySerializer
from django.core.mail import send_mail
import jwt,json,time
from rest_framework.decorators import api_view
from django.utils import timezone

# Create your views here.
@api_view(['POST'])
@login_is_required
def create_post(request):
    serializer = PostSerializer(data=request.data)
    if not serializer.is_valid():
        response = Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        set_token(response,request.user)
        return response

    if serializer.is_valid():
        serializer.save()
        response = Response(serializer.data,status=status.HTTP_201_CREATED)
        set_token(response,request.user)
        return response

@api_view(['PUT'])
@login_is_required
def update_post(request,id):
    try:
        post = Post.objects.get(id=id)
    except:
        response = Response({"message":"no such post"},status=status.HTTP_404_NOT_FOUND)
        set_token(response,request.user)
        return response
    if post.creator != request.user:
        response = Response({"message":"not allowed"},status=status.HTTP_403_FORBIDDEN)
        set_token(response,request.user)
        return response
    serializer = PostSerializer(post,data=request.data,partial=True)
    if not serializer.is_valid():
        response = Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        set_token(response,request.user)
        return response

    if serializer.is_valid():
        serializer.save()
        response = Response(serializer.data,status=status.HTTP_201_CREATED)
        set_token(response,request.user)
        return response

@api_view(['DELETE'])
@login_is_required
def delete_post(request,id):
    try:
        post = Post.objects.get(id=id)
    except:
        response = Response({"message":"no such post"},status=status.HTTP_404_NOT_FOUND)
        set_token(response,request.user)
        return response
    if post.creator != request.user:
        response = Response({"message":"not allowed"},status=status.HTTP_403_FORBIDDEN)
        set_token(response,request.user)
        return response
    post.delete()
    response = Response(status=status.HTTP_204_NO_CONTENT)
    set_token(response,request.user)
    return response

def json_post(post,me):
    if post.creator.dp:
        url = post.creator.dp.url
    else:
        url = None
    liked = me in post.likes.all()
    saved = me in post.saved_by.all()
    likes = post.likes.all()
    data = {
        'id':post.id,
        'author_dp':url,
        'author_username':post.creator.username,
        'location':post.location,
        'image':post.image.url,
        'liked':liked,
        'saved':saved,
        'caption':post.caption,
        'first_like':'',
        'first_like_dp':'',
        'comment_count':post.comment_set.all().count()
    }
    time_created = post.timedate
    time_now = datetime.datetime.now(tz=utc)
    diff = time_now - time_created
    days = diff.days
    seconds = diff.seconds
    years = days // 365
    months = days // 30
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    second = seconds % 60
    if days == 0:
        if hours == 0:
            if minutes == 0:
                delta = f'{second} sec ago'
            else:
                delta = f'{minutes} min ago'
        else:
            delta = f'{hours} hr, {minutes} min ago'
    else:
        if years == 0:
            if months == 0:
                delta = f'{days} days ago'
            else:
                delta = f'{months} month, {days} days ago'
        else:
            delta = f'{years} year ago'
    
    data['ago'] = delta

    find = False
    for profile in likes:
        if profile in me.following.all():
                data['first_like'] = profile.username
                if profile.dp:
                    url2 = profile.dp.url
                else:
                    url2 = None
                data['first_like_dp'] = url2
                find = True
                break
    if find:
        data['like_count'] = likes.count() - 1
    else:
        data['like_count'] = likes.count()
    return data
    

@api_view(['GET'])
@login_is_required
def get_post(request,id):
    try:
        post = Post.objects.get(id=id)
    except:
        response = Response({"message":"no such post"},status=status.HTTP_404_NOT_FOUND)
        set_token(response,request.user)
        return response
    
    jsondata = json.dumps(json_post(post,request.user))
    response = Response(jsondata,status=status.HTTP_200_OK)
    set_token(response,request.user)
    return response

def create_feed(me,index):
    feed = []
    load_count = 5
    following = list(me.following.all())
    following.append(me)
    for profile in following:
        for post in profile.posts.all():
            feed.append(post)
    feed.sort(key=lambda x:x.timedate,reverse=True)
    res = []
    if len(feed)>index*load_count:
        for post in feed[index*load_count:min(len(feed),load_count*(index+1))]:
            res.append(json_post(post,me))
    return res


@api_view(['GET'])
@login_is_required
def get_feed(request,index):
    feed = create_feed(request.user,index)
    response = Response(feed,status=status.HTTP_200_OK)
    set_token(response,request.user)
    return response


