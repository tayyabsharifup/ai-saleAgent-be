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

        emails_sent = ChatMessageHistory.objects.filter(lead__assign_to=agent, messageType='email', wroteBy__in=['agent', 'ai']).count()
        emails_replied = ChatMessageHistory.objects.filter(lead__assign_to=agent, messageType='email', wroteBy='client').count()
        avg_reply_rate = (emails_replied / emails_sent * 100) if emails_sent > 0 else 0

        weekly_reply_rates = []
        today = timezone.now().date()
        for i in range(4):
            end_date = today - timedelta(days=i*7)
            start_date = end_date - timedelta(days=6)

            emails_sent_week = ChatMessageHistory.objects.filter(
                lead__assign_to=agent,
                messageType='email',
                wroteBy__in=['agent', 'ai'],
                created_at__date__range=[start_date, end_date]
            ).count()

            emails_replied_week = ChatMessageHistory.objects.filter(
                lead__assign_to=agent,
                messageType='email',
                wroteBy='client',
                created_at__date__range=[start_date, end_date]
            ).count()

            avg_reply_rate_week = (emails_replied_week / emails_sent_week * 100) if emails_sent_week > 0 else 0
            
            weekly_reply_rates.append({
                'week': i + 1,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'avg_reply_rate': avg_reply_rate_week
            })

        today = timezone.now().date()
        daily_analytics = []
        for i in range(7):
            current_day = today - timedelta(days=i)
            
            calls_on_day = ChatMessageHistory.objects.filter(
                lead__assign_to=agent,
                messageType='call',
                created_at__date=current_day
            ).count()

            emails_on_day = ChatMessageHistory.objects.filter(
                lead__assign_to=agent,
                messageType='email',
                created_at__date=current_day
            ).count()

            leads_added_on_day = LeadModel.objects.filter(
                assign_to=agent,
                created_at__date=current_day
            ).count()

            daily_analytics.append({
                'date': current_day.isoformat(),
                'calls': calls_on_day,
                'emails': emails_on_day,
                'leads_added': leads_added_on_day
            })
        daily_analytics.reverse()


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
            'daily_analytics': daily_analytics,
            'avg_reply_rate': avg_reply_rate,
            'weekly_reply_rates': weekly_reply_rates,
            'emails_sent': emails_sent,
            'emails_replied': emails_replied,
        }, status=HTTP_200_OK)

