from django.contrib import admin
from apps.aiModule.models import ChatMessageHistory, NewLeadCall

# Register your models here.
admin.site.register(ChatMessageHistory)
admin.site.register(NewLeadCall)


