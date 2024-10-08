# Generated by Django 5.0.6 on 2024-09-08 02:17

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AirtimeAPIConfiguration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('api_name', models.CharField(default='MTN', max_length=30)),
                ('is_active', models.BooleanField(default=False)),
                ('network_image', models.ImageField(default='', help_text='the best image needed here is a square image recommended is 500 x 500', upload_to='network_images/')),
                ('identifier', models.CharField(default='mtn_airtime', help_text='this should be a unique identifier', max_length=50)),
                ('api_url', models.TextField(default='https://api-service.vtpass.com/api/pay', max_length=1000)),
                ('api_data', models.JSONField(default=dict, help_text='e.g: copy and paste this => {"data": {"serviceID": "mtn", "amount": "amount_float", "phone": "phone_number", "request_id": "request_id"}, "headers": {"Authorization": "Basic UHJpbmNlb295ZXNAZ21haWwuY29tOjFQYXl0ZXZUZWFt"}}')),
                ('success_code', models.CharField(default='true', max_length=500)),
                ('network_name', models.CharField(default='MTN', help_text='Network name for display', max_length=50)),
                ('network_identifier_code', models.CharField(default='1', help_text='The network code or identifier (ID) used by the API', max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='AirtimePurchase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('network_provider', models.CharField(max_length=20)),
                ('phone_number', models.CharField(max_length=20)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('old_balance', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('new_balance', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('status', models.CharField(default='pending', max_length=20)),
                ('api_response', models.TextField(blank=True, null=True)),
                ('request_id', models.CharField(blank=True, max_length=100, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
