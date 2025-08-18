from datetime import timedelta
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import *

from apps.users.serializers.agent_serializer import (
    AgentRegisterSerializer,
    AgentLoginSerializer,
    AgentProfileSerializer,
    AgentDashboardSerializer,
)

from rest_framework.permissions import IsAuthenticated
from apps.users.permissions import IsAgent
from apps.users.models import AgentModel, LeadModel
from apps.aiModule.models import ChatMessageHistory


class RegisterAgentView(APIView):
    serializer_class = AgentRegisterSerializer

    def post(self, request):
        serializer = AgentRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'message': 'Agent created successfully'}, status=HTTP_201_CREATED)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class LoginAgentView(APIView):
    serializer_class = AgentLoginSerializer

    def post(self, request):
        serializer = AgentLoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=HTTP_200_OK)

        return Response(serializer.errors, status=HTTP_401_UNAUTHORIZED)


class AgentProfileView(APIView):
    permission_classes = [IsAuthenticated, IsAgent]
    serializer_class = AgentProfileSerializer

    def get(self, request):
        try:
            agent = AgentModel.objects.get(user=request.user)
            serializer = AgentProfileSerializer(agent)
            return Response(serializer.data, status=HTTP_200_OK)
        except AgentModel.DoesNotExist:
            return Response({'message': 'Agent profile not found'}, status=HTTP_404_NOT_FOUND)


class AgentDashboardView(APIView):
    permission_classes = [IsAgent]
    serializer_class = AgentDashboardSerializer

    def get(self, request):
        try:
            agent = AgentModel.objects.get(user=request.user)
            agent_lead = LeadModel.objects.filter(assign_to=agent)
            serializer = AgentDashboardSerializer(agent_lead, many=True)
            return Response(serializer.data, status=HTTP_200_OK)

        except AgentModel.DoesNotExist:
            return Response({'message': 'Agent not found'}, status=HTTP_404_NOT_FOUND)

class AgentCallAnalytics(APIView):
    permission_classes = [IsAgent]

    def get(self, request):
        try:
            agent = AgentModel.objects.get(user=request.user)
        except AgentModel.DoesNotExist:
            return Response({'message': 'Agent not found'}, status=HTTP_404_NOT_FOUND)
        leads = LeadModel.objects.filter(assign_to=agent).count()
        leads_this_week = LeadModel.objects.filter(
            assign_to=agent, created_at__gte=timezone.now() - timedelta(days=7)).count()
        
        calls = ChatMessageHistory.objects.filter(lead__assign_to=agent, messageType='call').count()
        week_calls = ChatMessageHistory.objects.filter(lead__assign_to=agent,messageType='call', created_at__gte=timezone.now() - timedelta(days=7)).count()

        emails = ChatMessageHistory.objects.filter(lead__assign_to=agent,messageType='email').count()
        week_emails = ChatMessageHistory.objects.filter(lead__assign_to=agent,messageType='email', created_at__gte=timezone.now() - timedelta(days=7)).count()

        follow_ups = ChatMessageHistory.objects.filter(lead__assign_to=agent, wroteBy='ai', follow_up_date__isnull=False).count()
        follow_ups_this_week = ChatMessageHistory.objects.filter(lead__assign_to=agent, wroteBy='ai', follow_up_date__isnull=False,
                                                                        created_at__gte=timezone.now() - timedelta(days=7)).count()
        
        leads_added_this_week = LeadModel.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=7)).count()
        



        return Response({
            'leads': leads,
            'leads_this_week': leads_this_week,
            'calls': calls,
            'week_calls': week_calls,
            'emails': emails,
            'week_emails': week_emails,
            'follow_ups': follow_ups,
            'follow_ups_this_week': follow_ups_this_week,
            'leads_added_this_week': leads_added_this_week,
        }, status=HTTP_200_OK)
