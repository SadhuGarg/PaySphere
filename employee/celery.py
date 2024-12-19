# from __future__ import absolute_import, unicode_literals
# import os
# from celery import Celery

# # Set the default Django settings module
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project.settings')

# app = Celery('your_project')

# # Using a string here means the worker doesn't need to serialize
# # the configuration object to child processes.
# app.config_from_object('django.conf:settings', namespace='CELERY')

# # Autodiscover tasks in all registered apps
# app.autodiscover_tasks()
from celery import Celery
from celery.schedules import crontab

app = Celery('your_project_name')

# Load settings from Django settings file
app.config_from_object('django.conf:settings', namespace='CELERY')

# Periodic task configuration
app.conf.beat_schedule = {
    'generate-salaries-daily': {
        'task': 'yourapp.tasks.generate_salaries_for_today',
        'schedule': crontab(minute=0, hour=0),  # This will run daily at midnight
    },
}

# Auto-discover tasks in your Django app
app.autodiscover_tasks()

