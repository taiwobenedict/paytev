from django.contrib import admin

# Register your models here.


# Register your models here.
from django.contrib import admin
from .models import MonnifyConfig, VirtualAccount, ProcessedNotification
from .models import VirtualAccount

admin.site.register(MonnifyConfig)
admin.site.register(VirtualAccount)
admin.site.register(ProcessedNotification)

