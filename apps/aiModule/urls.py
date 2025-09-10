
#include router
from django.urls import path, include

from apps.aiModule.views import (
    chatHistoryView, 
    chatHistoryAgentView, 
    refreshAIFollowUpView,
    AddLeadInfo,
    UnmapCallView,
    )
# Create a router and register our viewset with it.

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('chatHistory/', chatHistoryView.as_view(), name='chatHistory'),
    path('chatHistoryAgent/', chatHistoryAgentView.as_view(), name='chatHistoryAgent'),
    path('refresh_ai_lead/', refreshAIFollowUpView.as_view(), name='refresh-ai-lead'),
    path('add_lead_info/', AddLeadInfo.as_view(), name='add-lead-info'),
    path('unmap_call/', UnmapCallView.as_view(), name='unmap-call'),
]
