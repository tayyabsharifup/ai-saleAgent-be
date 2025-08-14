from django.contrib import admin
from .models import (
    CustomUser,
    AgentModel,
    LeadModel,
    LeadPhoneModel,
    LeadEmailModel,
    ManagerModel,
)

admin.site.register(CustomUser)
admin.site.register(AgentModel)
admin.site.register(LeadModel)
admin.site.register(LeadPhoneModel)
admin.site.register(LeadEmailModel)
admin.site.register(ManagerModel)
