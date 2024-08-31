from django.contrib import admin
from .models import SentEmail

@admin.register(SentEmail)
class SentEmailAdmin(admin.ModelAdmin):
    list_display = ('subject', 'sent_at')
    filter_horizontal = ('recipients',)


from django.contrib import admin
from .models import EmailConfig

@admin.register(EmailConfig)
class EmailConfigAdmin(admin.ModelAdmin):
    pass
