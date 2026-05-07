import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'outvier_core.settings')

app = Celery('outvier_core')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Scheduled tasks
app.conf.beat_schedule = {
    'sync-salesforce-every-15-minutes': {
        'task': 'salesforce_integration.tasks.sync_salesforce_data',
        'schedule': crontab(minute='*/15'),
    },
}

app.conf.timezone = 'UTC'