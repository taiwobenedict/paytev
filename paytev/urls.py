"""
URL configuration for paytev project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from main.models import AppInfo

# Function to get the admin URL dynamically
def get_admin_url():
    try:
        app_info = AppInfo.objects.first()
        return app_info.admin_url if app_info else 'admin'
    except:
        return 'admin'

admin_url = get_admin_url()

urlpatterns = [
    path(f'{admin_url}/', admin.site.urls),
    path('', include('main.urls')),
    path('account/', include('account.urls')),
    path('airtime_recharge/', include('airtime_recharge.urls')),
    path('paystack/', include('paystack.urls', namespace='paystack')),
    path('bills/', include('bills.urls')),
    path('transactions/', include('transactions.urls')),
    path('strowallet/', include('strowallet.urls')),
    path('monnify/', include('monnify.urls')),
]

# Serving static and media files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
