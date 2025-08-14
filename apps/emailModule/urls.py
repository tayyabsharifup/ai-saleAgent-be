from apps.emailModule.views import (
    SendEmailView,
    FetchInboxView,
    SearchEmailView,
    CheckNewEmail
)

from django.urls import path

urlpatterns = [
    path('send_email/', SendEmailView.as_view(), name='send-email' ),
    path('fetch_email/', FetchInboxView.as_view(), name='fetch-email'),
    path('search_email/', SearchEmailView.as_view(), name='search-email'),
    path('check_new_email/', CheckNewEmail.as_view(), name='check-new-email'),
]