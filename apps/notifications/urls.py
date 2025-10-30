from apps.notifications.views import (
    NotificationView,
    FirebaseNotificationView,
)

from django.urls import path

urlpatterns = [
    path('', NotificationView.as_view(), name='notifications'),
    path('firebase/', FirebaseNotificationView.as_view(), name='firebase-notifications'),
]