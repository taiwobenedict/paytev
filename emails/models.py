from django.db import models
from django.conf import settings

class SentEmail(models.Model):
    subject = models.CharField(max_length=255)
    body = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    recipients = models.ManyToManyField(settings.AUTH_USER_MODEL)

    def __str__(self):
        return self.subject



class EmailConfig(models.Model):
    host = models.CharField(max_length=255, default='smtp.example.com')
    port = models.PositiveIntegerField(default=587)
    use_tls = models.BooleanField(default=True)
    use_ssl = models.BooleanField(default=False)
    host_user = models.EmailField(default='your-email@example.com')
    host_password = models.CharField(max_length=255, default='your-password')
    default_from_email = models.EmailField(default='your-email@example.com')

    def __str__(self):
        return 'Email Configuration'
