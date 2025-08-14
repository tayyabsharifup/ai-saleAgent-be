from django.db import models
from .agent_model import AgentModel


class LeadModel(models.Model):
    name = models.CharField(max_length=100, blank=True, default='')
    company = models.CharField(max_length=100, blank=True, default='')
    destination = models.CharField(max_length=100, blank=True, default='')
    assign_to = models.ForeignKey(
        AgentModel, on_delete=models.SET_NULL, null=True, blank=True)
    city = models.CharField(max_length=20, blank=True, default='')
    state = models.CharField(max_length=20, blank=True, default='')
    zip_code = models.CharField(max_length=10, blank=True, default='')
    address = models.CharField(max_length=100, blank=True, default='')
    status = models.CharField(
        max_length=20,
        choices=[('in_progress', 'in_progress'), ('not_initiated', 'not_initiated'), ('over_due', 'over_due'), ('converted', 'converted')],
        default='not_initiated'
        )
    assign_date = models.DateField(auto_now=True)
    info = models.TextField(blank=True ,default='')

    def __str__(self):
        return self.name


class LeadPhoneModel(models.Model):
    lead = models.ForeignKey(
        LeadModel, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20, blank=True, default='')
    type = models.CharField(max_length=10, blank=True, default='')

    def __str__(self):
        return self.phone_number


class LeadEmailModel(models.Model):
    lead = models.ForeignKey(
        LeadModel, on_delete=models.CASCADE)
    email = models.CharField(max_length=100, blank=True, default='')
    type = models.CharField(max_length=10, blank=True, default='')

    def __str__(self):
        return self.email
