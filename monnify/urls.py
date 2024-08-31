from . import views
from django.urls import path

# howdy/urls.py
# from django.conf.urls import url


from django.urls import include, path


from monnify.views import *
# from topup.cable_view import *


# urlpatterns = [
#   path('$', views.HomePageView.as_view()),
#   path('daabout/$', views.AboutPageView.as_view()),
#   path('about/$', views.About.as_view()),
#   path('contact/$', views.Contact.as_view()), # Add this /about/ route
# ]
app_name = 'monnify'

urlpatterns = [
    path('generate-virtual-account/', views.generate_virtual_account,
         name='generate_virtual_account'),
    path('virtual-account/', views.wallet, name='virtual_account'),
    path('wallet/', views.wallet, name='wallet'),
    path('mhook/', views.monnify_webhook, name='mhook'),
]
