from apps.emailModule.views import (
    SendEmailView,
    FetchInboxView,
    SearchEmailView,
    CheckNewEmail,
    OutlookAuthTokenURLView,
    OutlookRefreshTokenView,
    EmailTemplatesView,
    EmailTemplateDetailView,
    EmailTemplateWithLead,
    CheckNewEmailAgent,
)

from django.urls import path

urlpatterns = [
    path('send_email/', SendEmailView.as_view(), name='send-email' ),
    path('fetch_email/', FetchInboxView.as_view(), name='fetch-email'),
    path('search_email/', SearchEmailView.as_view(), name='search-email'),
    path('check_new_email/', CheckNewEmail.as_view(), name='check-new-email'),
    path('check_new_email_agent/<int:id>/', CheckNewEmailAgent.as_view(), name='check-new-email-agent'),
    path('outlook_auth_url/', OutlookAuthTokenURLView.as_view(), name='outlook-auth-url'),
    path('outlook_refresh_token/', OutlookRefreshTokenView.as_view(), name='outlook-refresh-token'),
    path('email_templates/', EmailTemplatesView.as_view(), name='email-templates'),
    path('email_templates/<int:template_id>/', EmailTemplateDetailView.as_view(), name='email-template-detail'),
    path('email_template_with_lead/<int:lead_id>/', EmailTemplateWithLead.as_view(), name='email-template-with-lead'),
    ]