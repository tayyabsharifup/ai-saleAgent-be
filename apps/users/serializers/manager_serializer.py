from rest_framework import serializers
from apps.users.models.manager_model import ManagerModel
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models.lead_model import LeadModel
from apps.users.serializers.lead_serializer import LeadPhoneSerializer, LeadEmailSerializer

from apps.aiModule.models import ChatMessageHistory



User = get_user_model()


class ManagerRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    language = serializers.CharField(required=False, allow_blank=True)
    offer = serializers.CharField(required=False, allow_blank=True)
    selling_point = serializers.CharField(required=False, allow_blank=True)
    faq = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            'email',
            'first_name',
            'last_name',
            'password',
            'language',
            'offer',
            'selling_point',
            'faq'
        ]

    def create(self, validated_data):
        password = validated_data.pop('password', '')
        language = validated_data.pop('language', '')
        offer = validated_data.pop('offer', '')
        selling_point = validated_data.pop('selling_point', '')
        faq = validated_data.pop('faq', '')

        user = User.objects.create_user(
            **validated_data, password=password, role='manager', is_verified=True)
        manager = ManagerModel.objects.create(
            user=user, language=language, offer=offer, selling_point=selling_point, faq=faq)
        return manager


class ManagerLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password']

    def validate(self, data):
        user = authenticate(email=data['email'], password=data['password'])

        if not user:
            raise serializers.ValidationError('Invalid Email or Password or Status inactive')
        if user.role != 'manager':
            raise serializers.ValidationError(
                'User does not have manager Role')

        tokens = RefreshToken.for_user(user)
        return {
            'refresh': str(tokens),
            'access': str(tokens.access_token),
            'manager_id': user.managermodel.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'language': user.managermodel.language,
            'offer': user.managermodel.offer,
            'selling_point': user.managermodel.selling_point,
            'faq': user.managermodel.faq,
        }

class ManagerLeadListSerializer(serializers.ModelSerializer):
    agent = serializers.SerializerMethodField()
    lead_phone = LeadPhoneSerializer(
        source='leadphonemodel_set', many=True, read_only=True)
    lead_email = LeadEmailSerializer(
        source='leademailmodel_set', many=True, read_only=True)
    total_follow_ups = serializers.SerializerMethodField()

    def get_total_follow_ups(self, obj):
        return ChatMessageHistory.objects.filter(lead=obj, wroteBy='ai', follow_up_date__isnull=False).count()

    class Meta:
        model = LeadModel
        fields = ('id', 'name',  'status', 'created_at', 'agent', 'lead_phone', 'lead_email', 'total_follow_ups')

    def get_agent(self, obj):
        return f"{obj.assign_to.user.first_name} {obj.assign_to.user.last_name}"
