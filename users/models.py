import re
from django.db import models
from django.contrib.auth.models import User
# Create your models here.


def dp_path(instance, filename):
    ext = filename.split('.')[-1]
    return 'dp/profile-{}/dp.{}'.format(instance.id,ext)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=100,unique=True)
    name = models.CharField(max_length=100,default='')
    bio = models.CharField(max_length=500,default='')
    verified = models.BooleanField(default=False)
    dp = models.ImageField(upload_to=dp_path,blank=True,null=True)
    followers = models.ManyToManyField('self',related_name='following',related_query_name='following',blank=True)
    close_friends = models.ManyToManyField('self',related_name='close_friend_of',related_query_name='close_friend_of',blank=True)
    req_rec = models.ManyToManyField('self',related_name='req_sent',related_query_name='req_sent',blank=True)
    saved_posts = models.ManyToManyField('Post',related_name='saved_by',related_query_name='saved_by',blank=True)
    
    def __str__(self):
        return f'{self.username} profile'
