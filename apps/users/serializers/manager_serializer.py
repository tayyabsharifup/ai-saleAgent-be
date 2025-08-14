from rest_framework import serializers
from apps.users.models.manager_model import ManagerModel
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class ManagerRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only = True)
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

        user = User.objects.create_user(**validated_data, password=password, role='manager', is_verified=True)
        manager = ManagerModel.objects.create(user=user, language = language, offer = offer, selling_point = selling_point, faq=faq)
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
            raise serializers.ValidationError('Invalid Email or Password')
        if user.role != 'manager':
            raise serializers.ValidationError('User does not have manager Role')
        
        tokens = RefreshToken.for_user(user)
        return {
            'refresh': str(tokens),
            'access': str(tokens.access_token),
            'manager_id': user.managermodel.id
        }


