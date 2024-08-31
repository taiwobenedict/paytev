from django.contrib import admin
from .models import AirtimePurchase

@admin.register(AirtimePurchase)
class AirtimePurchaseAdmin(admin.ModelAdmin):
    list_display = ('user', 'request_id', 'phone_number', 'amount', 'network_provider', 'status', 'old_balance', 'new_balance', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at', 'updated_at')
    search_fields = ('user__username', 'request_id', 'phone_number', 'network_provider', 'status')
    readonly_fields = ('user', 'request_id', 'phone_number', 'amount', 'network_provider', 'status', 'old_balance', 'new_balance', 'api_response', 'created_at', 'updated_at')

    def has_add_permission(self, request):
        return False  # Disable ability to add new AirtimePurchase entries from admin

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if not request.user.is_superuser:
            queryset = queryset.filter(user=request.user)
        return queryset





from django.contrib import admin
from .models import AirtimeAPIConfiguration

@admin.register(AirtimeAPIConfiguration)
class AirtimeAPIConfigurationAdmin(admin.ModelAdmin):
    list_display = ('api_name', 'network_name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('api_name', 'network_name', 'identifier')
