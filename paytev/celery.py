# celery.py

import os
from celery import Celery



# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paytev.settings')

# Create the Celery application
celery_app = Celery('paytev')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
celery_app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
celery_app.autodiscover_tasks()
