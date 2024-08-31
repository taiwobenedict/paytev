
from django.contrib import admin
from bills.models import CableRecharegAPI, DataNetworks, RechargeAirtimeAPI

class RechargeAirtimeAPIAdmin(admin.ModelAdmin):
    list_display = ('api_name', 'api_url', 'identifier',
                    'is_active', 'success_code')
    list_filter = ('api_name',)
    search_fields = ('api_name', 'success_code',)
    ordering = ('-api_name',)
    list_editable = ('is_active',)
    save_as = True


class DataNetworksAdmin(admin.ModelAdmin):
    list_display = ('api_name', 'is_active', 'identifier',
                    'api_url', 'success_code')
    list_filter = ('api_name',)
    search_fields = ('api_name', 'success_code',)
    ordering = ('-api_name',)
    list_editable = ('is_active',)
    save_as = True


class CableRecharegAPIAdmin(admin.ModelAdmin):
    list_display = ('api_name', 'is_active', 'api_url',
                    'identifier', 'success_code')
    list_filter = ('api_name',)
    search_fields = ('api_name', 'success_code',)
    ordering = ('-api_name',)
    list_editable = ('is_active',)
    save_as = True


admin.site.register(CableRecharegAPI, CableRecharegAPIAdmin)

admin.site.register(DataNetworks, DataNetworksAdmin)
admin.site.register(RechargeAirtimeAPI, RechargeAirtimeAPIAdmin)
# admin.site.register(AirtimeTopup, AirtimeTopupDetailsAdmin)
# admin.site.register(CableRecharge, CableRecharegesAdmin)
# admin.site.register(DataPlansPrices)
# admin.site.register(MtnDataShare, MtnDataShareDetailsAdmin)
