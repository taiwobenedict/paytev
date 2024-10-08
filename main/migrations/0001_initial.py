# Generated by Django 5.0.6 on 2024-09-08 02:17

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ActivationKeys',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('activation_key', models.CharField(max_length=250)),
                ('secret_key', models.CharField(max_length=250)),
                ('activation_url', models.CharField(max_length=300)),
                ('activated', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='AppInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('app_domain', models.CharField(default='paytev.com', help_text='Domain name of this site', max_length=50)),
                ('app_name', models.CharField(default='Paytev', max_length=20)),
                ('phone', models.CharField(default='', help_text='Format: 2348144216361', max_length=13)),
                ('email', models.EmailField(default='princeooyes@gmail.com', max_length=254)),
                ('keywords', models.TextField(default='Paytev', max_length=2000)),
                ('content_field', models.TextField(default='Paytev - Best VTU site', help_text='Site Description', max_length=2000)),
                ('app_logo', models.ImageField(blank=True, default='', null=True, upload_to='')),
                ('paystack_sk_token', models.CharField(blank=True, default='', max_length=100, null=True)),
                ('paystack_pk_token', models.CharField(blank=True, default='', max_length=100, null=True)),
                ('paystack_amount_funding_percentage', models.FloatField(default=0.016, help_text='0.016 means 1.6%, it is the commission Paystack will deduct')),
                ('bank_account_no', models.CharField(default='2005309292', max_length=15)),
                ('bank_name', models.CharField(default='Kuda Bank', max_length=300)),
                ('account_name', models.CharField(default='VICTOR OYEDOKUN', max_length=300)),
                ('dashboard_extra_info', models.TextField(blank=True, default='', max_length=1000000, null=True)),
                ('admin_url', models.CharField(default='admin', max_length=300)),
            ],
        ),
    ]
