from __future__ import absolute_import
import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yourproject.settings')
app = Celery('yourproject')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks()

@app.task
def send_daily_stock_alerts():
    from inventory.utils.alerts import check_low_stock_and_alert
    check_low_stock_and_alert()