from django.contrib import admin
from .models import KYC, KYCSettings

class KYCAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'first_name', 'last_name', 'middle_name', 'date_of_birth', 
        'phone_number', 'residential_address',
        'bvn', 'nin', 'id_type', 'id_number', 
        'bank_name', 'account_number', 
        'next_of_kin_name', 'next_of_kin_relationship', 'next_of_kin_phone', 'status', 'created_at', 'updated_at'
    )
    search_fields = (
        'user__username', 'first_name', 'last_name', 'phone_number', 
        'bvn', 'nin', 'account_number'
    )
    list_filter = ('status', 'id_type')
    
    # Make the specified fields read-only
#    readonly_fields = (
 #       'user', 'first_name', 'last_name', 'middle_name', 'date_of_birth', 
  #      'gender', 'phone_number', 'residential_address', 'state_of_residence',
   #     'bvn', 'nin', 'id_type', 'id_number', 
    #    'bank_name', 'account_number', 
     #   'next_of_kin_name', 'next_of_kin_relationship', 'next_of_kin_phone', 
      #  'is_verified', 'created_at', 'updated_at'
    #)

admin.site.register(KYC, KYCAdmin)




@admin.register(KYCSettings)
class KYCSettingsAdmin(admin.ModelAdmin):
    list_display = ('kyc_charge_amount', 'transaction_limit')
    # You can customize the admin form here if needed
