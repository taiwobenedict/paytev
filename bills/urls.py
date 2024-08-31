from django.urls import path
from .views import general_logic
from django.urls import include, path
from bills.views import *

app_name = 'bills'
urlpatterns = [
    
    path('iuc/', iuc_view, name='iuc'),
    path('process/', process_topup, name='process'),
    path('cable/', Givemecable, name='cable'),
    path('cable/<str:code>', CableProcessTemplate, name='cabletemplate_process'),
    path('databundle-topup', DataTopUpView, name='datatopup'),
    path('general/', general_logic, name='general'),
    path('buyairtime/', buynow, name='buyairtime'),
    #path('buydata/', buynow, name='buydata'),
    path('airtime/', AirtimeEmptyTemplate, name='airtime'),
    path('data/', Godata, name='data'),
    path('go/<str:code>',
         AirtimeProcessTemplate, name='airtimeprocess'),
    path('airtime-topup/', AirtimeView, name='airtimetopup'),
    path('m/<str:code>',
         DataProcessTemplate, name='dataprocess'),

     
]
