import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_sales.settings')
import django
django.setup()

from apps.notifications.utils.send_async_notification import send_async_notification as notification

notification(2, 'New message here')