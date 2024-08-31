from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Alert, UserAlertView

@login_required
def user_dashboard(request):
    alerts = Alert.objects.filter(is_active=True)
    for alert in alerts:
        user_alert_view, created = UserAlertView.objects.get_or_create(user=request.user, alert=alert)
        if user_alert_view.view_count < alert.view_times:
            user_alert_view.view_count += 1
            user_alert_view.save()
            return render(request, 'alert_system/alert_popup.html', {'alert': alert})

    return render(request, 'account/dashboard.html')
