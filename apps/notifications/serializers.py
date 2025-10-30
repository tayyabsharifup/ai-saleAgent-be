from rest_framework import serializers
from .models import NotificationModel, FirebaseNotifiationModel

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationModel
        fields = '__all__'

class FirebaseNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = FirebaseNotifiationModel
        fields = '__all__'