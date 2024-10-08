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
            name='KYCSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kyc_charge_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('transaction_limit', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
            ],
            options={
                'verbose_name': 'KYC Settings',
                'verbose_name_plural': 'KYC Settings',
            },
        ),
        migrations.CreateModel(
            name='KYC',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(blank=True, max_length=50)),
                ('last_name', models.CharField(blank=True, max_length=50)),
                ('middle_name', models.CharField(blank=True, max_length=50)),
                ('date_of_birth', models.DateField(null=True)),
                ('phone_number', models.CharField(max_length=15)),
                ('residential_address', models.TextField(blank=True)),
                ('verification_type', models.CharField(choices=[('BVN', 'BVN'), ('NIN', 'NIN'), ('Both', 'Both')], default='Select', max_length=10)),
                ('bvn', models.CharField(blank=True, max_length=11)),
                ('nin', models.CharField(blank=True, max_length=11)),
                ('id_type', models.CharField(choices=[('NIN', 'NIN Slip'), ('National ID', 'National ID (Plastic)'), ('Driver’s License', 'Driver’s License'), ('Passport', 'International Passport'), ('Voter’s Card', 'Voter’s Card')], max_length=20)),
                ('id_number', models.CharField(max_length=20)),
                ('bank_name', models.CharField(max_length=100)),
                ('account_number', models.CharField(max_length=10)),
                ('next_of_kin_name', models.CharField(max_length=100)),
                ('next_of_kin_relationship', models.CharField(max_length=50)),
                ('next_of_kin_phone', models.CharField(max_length=15)),
                ('declaration', models.BooleanField(default=False)),
                ('status', models.CharField(choices=[('Not Verified', 'Not Verified'), ('Submitted', 'Submitted'), ('Verified', 'Verified'), ('Rejected', 'Rejected')], default='Not Verified', max_length=20)),
                ('rejection_reason', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
