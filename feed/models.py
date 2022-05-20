from django.db import models
from django.utils import timezone

# Create your models here.
ACT_CHOICES = (
    ('1','tagged in a post'),
    ('2','tagged in a comment'),
    ('3','liked your post'),
    ('4','commented on your post'),
    ('5','started following you'),
)
def post_path(instance, filename):
    ext = filename.split('.')[-1]
    return 'profile-{}/posts/post-{}.{}'.format(instance.creator.id,instance.id,ext)


class Post(models.Model):
    creator = models.ForeignKey('users.Profile',on_delete=models.CASCADE,related_name='posts',related_query_name='posts')
    caption = models.CharField(max_length=500,blank=True,null=True)
    location = models.CharField(max_length=500,blank=True,null=True)
    tags = models.ManyToManyField('users.Profile',related_name='tagged_to',related_query_name='tagged_to',blank=True)
    image = models.ImageField(upload_to=post_path)
    timedate = models.DateTimeField(default=timezone.datetime.now)
    likes = models.ManyToManyField('users.Profile',related_name='liked_posts',related_query_name='liked_posts',blank=True)

    def __str__(self):
        return f'{self.caption}'

class Comment(models.Model):
    commentor = models.ForeignKey('users.Profile',on_delete=models.CASCADE)
    likes = models.ManyToManyField('users.Profile',related_name='liked_comments',related_query_name='liked_comments',blank=True)
    tags = models.ManyToManyField('users.Profile',related_name='tagged_to_comment',related_query_name='tagged_to_comment',blank=True)
    content = models.CharField(max_length=500,blank=True,null=True)
    timedate = models.DateTimeField(default=timezone.datetime.now)
    replied_to = models.ForeignKey('self',on_delete=models.CASCADE,blank=True,null=True)
    post = models.ForeignKey('Post',on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.content}'

class Story(models.Model):
    creator = models.ForeignKey('users.Profile',on_delete=models.CASCADE)
    timedate = models.DateTimeField(default=timezone.datetime.now)
    image = models.ImageField(upload_to=post_path,blank=True,null=True)
    seen = models.ManyToManyField('users.Profile',related_name='seen_stories',related_query_name='seen_stories',blank=True)
    close = models.BooleanField(default=False)
    post = models.ForeignKey('Post',on_delete=models.CASCADE,blank=True,null=True)


class Activity(models.Model):
    of = models.ForeignKey('users.Profile',related_name='activity',related_query_name='activity',on_delete=models.CASCADE)
    timedate = models.DateTimeField(default=timezone.datetime.now)
    category = models.CharField(max_length=20,choices=ACT_CHOICES)
    post = models.ForeignKey('Post',on_delete=models.CASCADE,blank=True,null=True)
    comment = models.ForeignKey('Comment',on_delete=models.CASCADE,blank=True,null=True)
    profile = models.ForeignKey('users.Profile',on_delete=models.CASCADE,related_name='in_activity',related_query_name='in_activity',blank=True,null=True)