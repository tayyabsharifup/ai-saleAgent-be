from rest_framework import serializers
from apps.users.models import AgentModel, ManagerModel, LeadModel
from apps.aiModule.models import ChatMessageHistory
from apps.aiModule.serializers import ChatMessageHistorySerializer

from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class AgentRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    smtp_email = serializers.CharField(required=False, allow_blank=True)
    smtp_password = serializers.CharField(required=False, allow_blank=True)
    assign_manager = serializers.PrimaryKeyRelatedField(queryset=ManagerModel.objects.all(), required=False, allow_null=True, write_only=True)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password', 'phone', 'smtp_email', 'smtp_password', 'assign_manager']
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        phone = validated_data.pop('phone', '')
        smtp_email = validated_data.pop('smtp_email', '')
        smtp_password = validated_data.pop('smtp_password', '')
        assign_manager = validated_data.pop('assign_manager', None)

        user = User.objects.create_user(**validated_data, password=password, role='agent', is_verified=True)

        agent = AgentModel.objects.create(user=user, phone=phone, smtp_email=smtp_email, smtp_password=smtp_password, assign_manager=assign_manager)
        return agent
    


class AgentLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ['email', 'password']
    
    def validate(self, data):
        user = authenticate(email=data['email'], password=data['password'])

        if not user:
            raise serializers.ValidationError('Invalid Email or Password')
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
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)

    class Meta:
        model = AgentModel
        fields = ['id', 'email', 'first_name', 'last_name', 'phone', 'smtp_email']


class LeadsSerializer(serializers.ModelSerializer):
    last_chat_message = serializers.SerializerMethodField()

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

class AgentDashboardSerializer(serializers.ModelSerializer):
    total_leads = serializers.IntegerField()
    total_messages = serializers.IntegerField()
    leads = LeadsSerializer(many=True)
    class Meta:
        model = AgentModel
        fields = ['total_leads', 'total_messages', 'leads']

