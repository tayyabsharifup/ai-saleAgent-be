from django.db import models
from django.utils import timezone
from apps.users.models import LeadModel

class ChatMessageHistory(models.Model):
    lead = models.ForeignKey(LeadModel, on_delete=models.CASCADE, blank=True, null=True)
    heading = models.TextField()
    body = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    messageType = models.CharField(max_length=10, choices=[('email', 'email'), ('call', 'call'), ('manual', 'manual'), ('none', 'none')], default='none')
    aiType = models.CharField(max_length=10, choices=[('ai', 'ai'), ('human', 'human'), ('none', 'none')], default='none') # for langgraph AI/ Human
    interestLevel = models.CharField(max_length=10, choices=[('short', 'short'), ('medium', 'medium'), ('long', 'long'), ('none', 'none')], default='none')
    wroteBy = models.CharField(max_length=10, choices=[('agent', 'agent'), ('client', 'client'), ('none', 'none'), ('ai', 'ai')], default='none')
    follow_up_date = models.DateField(blank=True, null=True)
    pid = models.CharField(max_length=100, blank=True, null=True) # Email Message id




    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.lead} - {self.created_at}"