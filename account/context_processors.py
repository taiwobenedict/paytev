from main.models import AppInfo

def app_info(request):
    app_info = AppInfo.objects.first()
    return {'app_info': app_info}
