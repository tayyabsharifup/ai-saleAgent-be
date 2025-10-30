from apps.notifications.views import (
    NotificationView,
    FirebaseNotificationView,
)

from django.urls import path

urlpatterns = [
    path('async/', NotificationView.as_view(), name='notifications'),
    path('firebase/', FirebaseNotificationView.as_view(), name='firebase-notifications'),
]