# import setting for debug
from django.conf import settings
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import *
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.hashers import check_password
from apps.users.serializers.user_serializers import (
    SendOtpSerializer,
    VerifyOtpSerializer,
    ResetPasswordWithOtpSerializer,
    ChangePasswordSerializer,
    LoginSerializer,
    RegisterSerializer,

)
from apps.users.models import AgentModel, ManagerModel

from apps.users.permissions import IsAgent, IsManager, IsAdmin

# Create your views here.

User = get_user_model()

class VerifyOtpView(APIView):
    serializer_class = VerifyOtpSerializer
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')

        if not email or not otp:
            return Response({'message': 'Email and OTP required'}, status=HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
        except:
            return Response({'message': 'User not Found'}, status=HTTP_404_NOT_FOUND)
        
        if user.verify_otp(otp):
            tokens = RefreshToken.for_user(user)
            role = None
            user_data = {}
            if user.is_superuser:
                role = 'admin'
                user_data = {
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                }
            elif user.role == 'agent':
                role = 'agent'
                try:
                    agent = user.agentmodel
                    user_data = {
                        'agent_id': agent.id,
                        'manager_id': agent.assign_manager.id if agent.assign_manager else None,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'phone': agent.phone,
                        'smtp_email': agent.smtp_email
                    }
                except AgentModel.DoesNotExist:
                    return Response({'message': 'Agent profile not found'}, status=HTTP_404_NOT_FOUND)
            elif user.role == 'manager':
                role = 'manager'
                try:
                    manager = user.managermodel
                    user_data = {
                        'manager_id': manager.id,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'language': manager.language,
                        'offer': manager.offer,
                        'selling_point': manager.selling_point,
                        'faq': manager.faq,
                    }
                except ManagerModel.DoesNotExist:
                    return Response({'message': 'Manager profile not found'}, status=HTTP_404_NOT_FOUND)
            else:
                return Response({'message': 'Invalid Role'}, status=HTTP_400_BAD_REQUEST)

            output_data = {
                'refresh': str(tokens),
                'access': str(tokens.access_token),
                'role': role,
            }
            output_data.update(user_data)
            return Response(output_data, status=HTTP_200_OK)
        else:
            return Response({'message': 'Invalid or Expired OTP'}, status=HTTP_400_BAD_REQUEST)
        

class SendOtpView(APIView):
    serializer_class = SendOtpSerializer
    def post(self, request):
        email = request.data.get('email')

        if not email:
            return Response({'message': 'Email is required'}, status=HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
        except:
            return Response({'message': 'User not found'}, status=HTTP_404_NOT_FOUND)
        
        # if the debug is true in setting then return OTP sent 
        if settings.DEBUG:
            print(f"OTP for {email}: {user.otp}")
            return Response({'message': 'OTP sent (DEBUG)'}, status=HTTP_200_OK)

        try:

            if user.generate_otp():
                return Response({'message': 'OTP sent'}, status=HTTP_200_OK)
        except:
            return Response({'message': 'Error sending OTP'}, status=HTTP_500_INTERNAL_SERVER_ERROR)
            
        else:
            return Response({'message': 'Error, OTP not sent'}, status=HTTP_503_SERVICE_UNAVAILABLE)


class ResetPasswordWithOtpView(APIView):
    permission_classes = [IsManager | IsAdmin | IsAgent]
    def post(self, request):
        new_password = request.data.get('new_password')
        user = request.user

        user.set_password(new_password)
        user.save()

        return Response({'message': 'Password reset successfully'}, status=HTTP_200_OK)

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer
    def post(self, request):
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        if not old_password or not new_password:
            return Response({'message': 'Both old and new passwords are required'}, status=HTTP_400_BAD_REQUEST)
        
        if not user.check_password(old_password):
            return Response({'message': 'Old password is incorrect'}, status=HTTP_403_FORBIDDEN)
        
        user.set_password(new_password)
        user.save()

        return Response({'message': 'Password changed successfully'}, status=HTTP_200_OK)
        

class LoginUserView(APIView):
    serializer_class = LoginSerializer
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=HTTP_200_OK)
        else:
            return Response(serializer.errors, status=HTTP_401_UNAUTHORIZED)
        
