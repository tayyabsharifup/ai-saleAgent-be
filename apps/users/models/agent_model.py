from django.db import models
from .user_model import CustomUser
from .manager_model import ManagerModel

class AgentModel(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    phone = models.CharField(max_length=100, blank=True, default='')
    smtp_email = models.CharField(max_length=100, blank=True, default='')
    smtp_password = models.CharField(max_length=50, blank=True, default='')
    assign_manager = models.ForeignKey(ManagerModel, on_delete=models.CASCADE, null=True, blank=True)


    def __str__(self):
        return self.user.email