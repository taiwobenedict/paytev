from django.contrib import admin
from .models import Alert, UserAlertView

@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ('title', 'view_times', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'message')

@admin.register(UserAlertView)
class UserAlertViewAdmin(admin.ModelAdmin):
    list_display = ('user', 'alert', 'view_count')
    search_fields = ('user__username', 'alert__title')
