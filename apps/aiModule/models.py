from django.db import models
from django.utils import timezone
from apps.users.models import LeadModel
from apps.users.models.agent_model import AgentModel


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
    key_points = models.JSONField(blank=True, null=True) # List of key summary points




    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.lead} - {self.created_at}"

class NewLeadCall(models.Model):
    is_map = models.BooleanField(default=False)
    transcript = models.TextField(blank=True, null=True)
    from_num = models.CharField(max_length=20, blank=True, null=True)
    agent = models.ForeignKey(AgentModel, on_delete=models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Call from {self.from_num} - Mapped: {self.is_map}"