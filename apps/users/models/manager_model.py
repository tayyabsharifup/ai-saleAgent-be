from django.db import models
from .user_model import CustomUser

class ManagerModel(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    language = models.CharField(max_length=20, blank=True, default='English')
    offer = models.CharField(max_length=200, blank=True, default='')
    selling_point = models.CharField(max_length=200, blank=True, default='')
    faq = models.CharField(max_length=200, blank=True, default='')

    def __str__(self):
        return self.user.email

