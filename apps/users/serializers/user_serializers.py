from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import AgentModel

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'email',
            'first_name',
            'last_name',
            'password',
        ]

    def create(self, validated_data):
        password = validated_data.pop('password', '')
        user = User.objects.create_user(**validated_data, password=password)

        return user


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)
    role = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'role']

    def validate(self, data):
        user = authenticate(email=data['email'], password=data['password'])

        if not user:
            raise serializers.ValidationError('Invalid Email or Password or Status inactive')

        user_data = {}
        role = None
        if user.is_superuser:
            role = 'admin'
            user_data = {
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            }

        elif user.role == 'agent':
            role = 'agent'
            user_data = {
                'agent_id': user.agentmodel.id,
                'manager_id': user.agentmodel.assign_manager.id if user.agentmodel.assign_manager else None,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone': user.agentmodel.phone,
                'smtp_email': user.agentmodel.smtp_email
            }
        elif user.role == 'manager':
            role = 'manager'
            user_data = {
                'manager_id': user.managermodel.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'language': user.managermodel.language,
                'offer': user.managermodel.offer,
                'selling_point': user.managermodel.selling_point,
                'faq': user.managermodel.faq,
            }
        else:
            raise serializers.ValidationError('Invalid Role')

        tokens = RefreshToken.for_user(user)
        output_data = {
            'refresh': str(tokens),
            'access': str(tokens.access_token),
            'role': role,
        }
        output_data = output_data | user_data
        return output_data


class VerifyOtpSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField()


class SendOtpSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordWithOtpSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField()
    new_password = serializers.CharField()


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()
