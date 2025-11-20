import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_sales.settings')
import django
django.setup()

from apps.notifications.models import NotificationModel
from django.contrib.auth import get_user_model
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from apps.notifications.serializers import NotificationSerializer

User = get_user_model()

try:
    user = User.objects.get(id=2)
    notification = NotificationModel.objects.create(user=user, message="Test notification from tmp.py")
    serializer = NotificationSerializer(notification)
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'notifications_{user.id}',
        {
            'type': 'notification_message',
            'notification': serializer.data
        }
    )
    print("Notification created and sent via websocket")
except User.DoesNotExist:
    print("User with id 1 does not exist")
except Exception as e:
    print(f"Error: {e}")