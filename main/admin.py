from django.contrib import admin

# Register your models here.
from main.models import AppInfo , ActivationKeys

admin.site.register(AppInfo)
admin.site.register(ActivationKeys)