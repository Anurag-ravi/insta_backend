import imp
from django.contrib import admin
from .models import Profile,VerifyTable,ResetTable
# Register your models here.
admin.site.register(Profile)
admin.site.register(VerifyTable)
admin.site.register(ResetTable)