# Generated by Django 5.0.6 on 2024-09-07 09:06

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('host', models.CharField(default='smtp.example.com', max_length=255)),
                ('port', models.PositiveIntegerField(default=587)),
                ('use_tls', models.BooleanField(default=True)),
                ('use_ssl', models.BooleanField(default=False)),
                ('host_user', models.EmailField(default='your-email@example.com', max_length=254)),
                ('host_password', models.CharField(default='your-password', max_length=255)),
                ('default_from_email', models.EmailField(default='your-email@example.com', max_length=254)),
            ],
        ),
        migrations.CreateModel(
            name='SentEmail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=255)),
                ('body', models.TextField()),
                ('sent_at', models.DateTimeField(auto_now_add=True)),
                ('recipients', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
