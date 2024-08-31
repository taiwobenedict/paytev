from django.shortcuts import render
from .models import AppInfo
from django.contrib.auth.decorators import login_required

def home(request):
    app_info = AppInfo.objects.first()  # Get the first entry of AppInfo
    return render(request, 'home.html', {'app_info': app_info})


@login_required
def dashboard(request):
    app_info = {
        'app_name': 'Paytev',  # Replace with your actual app name
    }
    return render(request, 'dashboard.html', {'app_info': app_info, 'user': request.user})