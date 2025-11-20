from django.core.management.base import BaseCommand
from apps.notifications.models import NotificationModel
from django.contrib.auth import get_user_model
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from apps.notifications.serializers import NotificationSerializer

User = get_user_model()

class Command(BaseCommand):
    help = 'Create a test notification for user ID 2 and send via WebSocket'

    def handle(self, *args, **options):
        try:
            user = User.objects.get(id=2)
            notification = NotificationModel.objects.create(user=user, message="Test notification from management command")
            serializer = NotificationSerializer(notification)
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'notifications_{user.id}',
                {
                    'type': 'notification_message',
                    'notification': serializer.data
                }
            )
            self.stdout.write(self.style.SUCCESS('Notification created and sent via WebSocket'))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('User with id 2 does not exist'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))