import imp
from django.contrib import admin
from .models import Profile,VerifyTable
# Register your models here.
admin.site.register(Profile)
admin.site.register(VerifyTable)