from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import *
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
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
            return Response({'message': 'OTP verified successfully'}, status=HTTP_200_OK)
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
        
        if user.generate_otp():
            return Response({'message': 'OTP sent'}, status=HTTP_200_OK)
        else:
            return Response({'message': 'Error, OTP not sent'}, status=HTTP_503_SERVICE_UNAVAILABLE)


class ResetPasswordWithOtpView(APIView):
    serializer_class = ResetPasswordWithOtpSerializer
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        new_password = request.data.get('new_password')

        if not all([email, otp, new_password]):
            return Response({'message': 'Email, OTP and New Password are required'}, status=HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'message': 'User not found'}, status=HTTP_404_NOT_FOUND)
        
        if not user.verify_otp(otp):
            return Response({'message': 'Invalid or expired OTP'}, status=HTTP_400_BAD_REQUEST)
        
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
        
