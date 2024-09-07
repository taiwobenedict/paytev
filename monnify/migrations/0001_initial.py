# Generated by Django 5.0.6 on 2024-09-07 09:06

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
            name='MonnifyConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('base_url', models.URLField(default='https://sandbox.monnify.com/api/v1/')),
                ('api_key', models.CharField(max_length=255)),
                ('secret_key', models.CharField(max_length=255)),
                ('contract_code', models.CharField(max_length=255)),
                ('fee', models.FloatField(default=0.015, help_text="<strong style='color:red;'>This shoulg be a percentage of the amount the user buys</strong>")),
                ('wallet_account_number', models.CharField(blank=True, max_length=20, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProcessedNotification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_reference', models.CharField(max_length=255, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='VirtualAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account_number', models.CharField(default='', max_length=500)),
                ('bank_name', models.CharField(default='', max_length=500)),
                ('account_name', models.CharField(max_length=100)),
                ('account_reference', models.CharField(default='', max_length=50, unique=True)),
                ('reservation_reference', models.CharField(default='', max_length=50)),
                ('status', models.CharField(default='', max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('response_body', models.JSONField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
