from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken


from apps.users.models import AgentModel, ManagerModel, LeadModel
from apps.aiModule.models import ChatMessageHistory
from apps.aiModule.serializers import ChatMessageHistorySerializer
from apps.users.serializers.lead_serializer import LeadPhoneSerializer, LeadEmailSerializer

from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate

import smtplib
from apps.emailModule.outlook import OutlookEmail

User = get_user_model()
outlook = OutlookEmail()




class AgentRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    smtp_email = serializers.CharField(required=False, allow_blank=True)
    smtp_password = serializers.CharField(required=False, allow_blank=True)
    assign_manager = serializers.PrimaryKeyRelatedField(
        queryset=ManagerModel.objects.all(), required=False, allow_null=True, write_only=True)
    email_provider = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password',
                  'phone', 'smtp_email', 'smtp_password', 'assign_manager', 'email_provider']

    def create(self, validated_data):
        password = validated_data.pop('password')
        phone = validated_data.pop('phone', '')
        smtp_email = validated_data.pop('smtp_email', '')
        smtp_password = validated_data.pop('smtp_password', '')
        assign_manager = validated_data.pop('assign_manager', None)
        email_provider = validated_data.pop('email_provider', '')


        user = User.objects.create_user(
            **validated_data, password=password, role='agent', is_verified=True)

        agent = AgentModel.objects.create(
            user=user, phone=phone, smtp_email=smtp_email, smtp_password=smtp_password, assign_manager=assign_manager, email_provider=email_provider)
        return agent
    
    def validate(self, data):
        smtp_email = data.get('smtp_email')
        smtp_password = data.get('smtp_password')
        email_provider = data.get('email_provider')


        if not smtp_email or not smtp_password:
            raise serializers.ValidationError("SMTP email and password are required.")

        if email_provider == 'outlook':
            is_true, token = outlook.get_access_token(smtp_password)
            if not is_true:
                raise serializers.ValidationError("Invalid Outlook token")
        elif email_provider == 'gmail':
            try:
                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                    server.login(smtp_email, smtp_password)
            except smtplib.SMTPAuthenticationError:
                raise serializers.ValidationError("Invalid SMTP email or password.")

        return data
        

class AgentUpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentModel
        fields = '__all__'
        read_only_fields = ['user',]

class AgentLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password']

    def validate(self, data):
        user = authenticate(email=data['email'], password=data['password'])

        if not user:
            raise serializers.ValidationError('Invalid Email or Password or Status inactive')
        if user.role != 'agent':
            raise serializers.ValidationError('User does not have agent Role')


        tokens = RefreshToken.for_user(user)
        return {
            'refresh': str(tokens),
            'access': str(tokens.access_token),
            'agent_id': user.agentmodel.id,
            'manager_id': user.agentmodel.assign_manager.id if user.agentmodel.assign_manager else None,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'phone': user.agentmodel.phone,
            'smtp_email': user.agentmodel.smtp_email
        }


class AgentProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    first_name = serializers.CharField(
        source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)

    class Meta:
        model = AgentModel
        fields = ['id', 'email', 'first_name',
                  'last_name', 'phone', 'smtp_email']


class AgentDashboardSerializer(serializers.ModelSerializer):
    last_chat_message = serializers.SerializerMethodField()
    lead_phone = LeadPhoneSerializer(
        source='leadphonemodel_set', many=True, read_only=True)
    lead_email = LeadEmailSerializer(
        source='leademailmodel_set', many=True, read_only=True)

    class Meta:
        model = LeadModel
        fields = '__all__'

    def get_last_chat_message(self, obj):
        """
        Get the last chat message for this lead
        """
        try:
            last_message = obj.chatmessagehistory_set.last()
            if last_message:
                return ChatMessageHistorySerializer(last_message).data
            return None
        except ChatMessageHistory.DoesNotExist:
            return None

