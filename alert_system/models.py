from django.db import models
from account.models import CustomUser

class Alert(models.Model):
    title = models.CharField(max_length=255)
    message = models.TextField()
    view_times = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class UserAlertView(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    alert = models.ForeignKey(Alert, on_delete=models.CASCADE)
    view_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.alert.title}"
