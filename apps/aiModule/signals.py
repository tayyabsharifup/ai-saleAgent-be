from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.aiModule.models import ChatMessageHistory
from apps.notifications.utils.send_async_notification import send_async_notification


@receiver(post_save, sender=ChatMessageHistory)
def send_notification_on_new_message(sender, instance, created, **kwargs):
    if created:
        lead = instance.lead
        agent = lead.assign_to
        if lead and agent:
            user_id = agent.user.id
            message = f"New message from {lead.name} in your inbox."
            
            # Additional check: only send notification if the message is from the client or AI
            if instance.wroteBy in ['client', 'ai']:
                send_async_notification(user_id, message)
