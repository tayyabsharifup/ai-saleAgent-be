
#include router
from django.urls import path, include

from apps.aiModule.views import chatHistoryView, chatHistoryAgentView, refreshAIFollowUpView
# Create a router and register our viewset with it.

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('chatHistory/', chatHistoryView.as_view(), name='chatHistory'),
    path('chatHistoryAgent/', chatHistoryAgentView.as_view(), name='chatHistoryAgent'),
    path('refresh_ai_lead/', refreshAIFollowUpView.as_view(), name='refresh-ai-lead'),
]
