from rest_framework import serializers
from apps.aiModule.models import ChatMessageHistory

class ChatMessageHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessageHistory
        fields = '__all__'
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        return ChatMessageHistory.objects.create(**validated_data)



