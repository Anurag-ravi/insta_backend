from django.db.models.signals import post_save,post_delete,pre_save
from django.contrib.auth.models import User
from django.dispatch import receiver,Signal
from .models import Profile
from django.core.files.storage import default_storage
import shutil
    

@receiver(post_delete, sender=Profile)
def delete_associated_files(sender, instance, **kwargs):
    """Remove all files of an image after deletion."""
    path = instance.dp.name
    if path:
        arr = path.split('/');
        folder = 'media/'+arr[0]
        shutil.rmtree(folder)

@receiver(pre_save, sender=Profile)
def pre_save_image(sender, instance, *args, **kwargs):
    """ instance old image file will delete from os """
    try:
        old_img = Profile.objects.get(id=instance.id).dp.path
        try:
            new_img = instance.dp.path
        except:
            new_img = None
        if new_img != old_img:
            default_storage.delete(old_img)
    except:
        pass
