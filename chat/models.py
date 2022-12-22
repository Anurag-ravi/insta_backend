from django.db import models
from django.utils import timezone
# Create your models here.
def message_path(instance, filename):
    ext = filename.split('.')[-1]
    return 'message_image/message-{}.{}'.format(instance.id,ext)
    
class Message(models.Model):
    to = models.ForeignKey('users.Profile',on_delete=models.CASCADE,related_name='tomessage',related_query_name='tomessage')
    by = models.ForeignKey('users.Profile',on_delete=models.CASCADE,related_name='bychat',related_query_name='bychat')
    timedate = models.DateTimeField(default=timezone.datetime.now)
    replied_to = models.ForeignKey('self',on_delete=models.CASCADE,blank=True,null=True)
    text = models.TextField(blank=True,null=True)
    post = models.ForeignKey('feed.Post',on_delete=models.CASCADE,blank=True,null=True)
    image = models.ImageField(upload_to=message_path)
    seen = models.BooleanField(default=False)
    reaction_by = models.CharField(max_length=255,blank=True,null=True)
    reaction_to = models.CharField(max_length=255,blank=True,null=True)

    def __str__(self):
        return f'{self.text} {self.to.username} {self.by.username}'
    
class AnoUser(models.Model):
    def is_anonymous(self):
        return True
    