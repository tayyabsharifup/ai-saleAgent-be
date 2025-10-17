from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import *

from django.utils import timezone
from datetime import timedelta


from apps.users.serializers.manager_serializer import (
    ManagerLoginSerializer,
    ManagerRegisterSerializer,
    ManagerProfileSerializer,
)
from apps.users.serializers.manager_serializer import ManagerLeadListSerializer
from apps.users.serializers.agent_serializer import AgentProfileSerializer
from apps.users.permissions import IsAdmin, IsManager
from apps.users.models import ManagerModel, LeadModel
from apps.users.models.agent_model import AgentModel
from apps.aiModule.models import ChatMessageHistory


class ManagerRegisterView(APIView):
    serializer_class = ManagerRegisterSerializer
    permission_classes = [IsAdmin]

    def post(self, request):
        serializer = ManagerRegisterSerializer(data=request.data)

        if serializer.is_valid():
            manager = serializer.save()
            return Response({'message': 'Manager register successfully'}, status=HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class ManagerLoginView(APIView):
    serializer_class = ManagerLoginSerializer

    def post(self, request):
        serializer = ManagerLoginSerializer(data=request.data)

        if serializer.is_valid():
            return Response(serializer.validated_data, status=HTTP_200_OK)
        else:
            return Response(serializer.errors, status=HTTP_401_UNAUTHORIZED)


class ManagerDashboardView(APIView):
    permission_classes = [IsManager]

    def get(self, request):
        user = request.user
        manager = ManagerModel.objects.get(user=user)
        agents = AgentModel.objects.filter(assign_manager=manager)
        total_calls = ChatMessageHistory.objects.filter(
            lead__assign_to__in=agents, messageType='call').count()
        total_follow_ups = ChatMessageHistory.objects.filter(
            lead__assign_to__in=agents, wroteBy='ai', follow_up_date__isnull=False).count()
        # make sure that LeadModel query count do not equal to 0 so that we don't have the ZeroDivisionError
        if LeadModel.objects.filter(assign_to__in=agents).count() == 0:
            average_lead_onboard = 0
        else:
            average_lead_onboard = LeadModel.objects.filter(assign_to__in=agents, status='converted').count(
            ) / LeadModel.objects.filter(assign_to__in=agents).count() * 100

        # Agent with the conversted Lead Number

        agents_stat = []
        for agent in agents:
            agent_stat = {
                'agent': f"{agent.user.first_name} {agent.user.last_name}",
                'total_calls': ChatMessageHistory.objects.filter(
                    lead__assign_to=agent, messageType='call').count(),
                'total_follow_ups': ChatMessageHistory.objects.filter(
                    lead__assign_to=agent, wroteBy='ai', follow_up_date__isnull=False).count(),
                'average_lead_onboard': LeadModel.objects.filter(
                    assign_to=agent, status='converted').count() / LeadModel.objects.filter(assign_to=agent).count() * 100
            
            }
            agents_stat.append(agent_stat)

        return Response({
            'total_calls': total_calls,
            'total_follow_ups': total_follow_ups,
            'average_lead_onboard': average_lead_onboard,
            'agents_stat': agents_stat
        }, status=HTTP_200_OK)

class ManagerLeadListView(APIView):
    permission_classes = [IsManager]

    def get(self, request):
        manager = ManagerModel.objects.get(user=request.user)
        agents = AgentModel.objects.filter(assign_manager=manager)
        leads = LeadModel.objects.filter(assign_to__in=agents)
        serializer = ManagerLeadListSerializer(leads, many=True)
        return Response(serializer.data, status=HTTP_200_OK)

class ManagerAgentListView(APIView):
    permission_classes = [IsManager]

    def get(self, request):
        manager = ManagerModel.objects.get(user=request.user)
        agents = AgentModel.objects.filter(assign_manager=manager)
        serializer = AgentProfileSerializer(agents, many=True)
        return Response(serializer.data, status=HTTP_200_OK)


class ManagerShortSurveyView(APIView):
    permission_classes = [IsManager]

    def post(self, request):
        manager = ManagerModel.objects.get(user=request.user)
        language = request.data.get('language')
        offer = request.data.get('offer')
        selling_point = request.data.get('selling_point')
        faq = request.data.get('faq')

        if language:
            manager.language = language
        if offer:
            manager.offer = offer
        if selling_point:
            manager.selling_point = selling_point
        if faq:
            manager.faq = faq

        manager.save()

        return Response({'message': 'Short survey updated successfully'}, status=HTTP_200_OK)

class GetAllManagerView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        managers = ManagerModel.objects.all()
        serializer = ManagerProfileSerializer(managers, many=True)
        return Response(serializer.data, status=HTTP_200_OK)


class ManagerCallAnalytics(APIView):
    permission_classes = [IsManager]

    def get(self, request):
        manager = ManagerModel.objects.get(user=request.user)
        agents = AgentModel.objects.filter(assign_manager=manager)

        leads = LeadModel.objects.filter(assign_to__in=agents).count()
        leads_this_week = LeadModel.objects.filter(
            assign_to__in=agents, created_at__gte=timezone.now() - timedelta(days=7)).count()
        
        calls = ChatMessageHistory.objects.filter(lead__assign_to__in=agents, messageType='call').count()
        week_calls = ChatMessageHistory.objects.filter(lead__assign_to__in=agents,messageType='call', created_at__gte=timezone.now() - timedelta(days=7)).count()

        emails = ChatMessageHistory.objects.filter(lead__assign_to__in=agents,messageType='email').count()
        week_emails = ChatMessageHistory.objects.filter(lead__assign_to__in=agents,messageType='email', created_at__gte=timezone.now() - timedelta(days=7)).count()

        follow_ups = ChatMessageHistory.objects.filter(lead__assign_to__in=agents, wroteBy='ai', follow_up_date__isnull=False).count()
        follow_ups_this_week = ChatMessageHistory.objects.filter(lead__assign_to__in=agents, wroteBy='ai', follow_up_date__isnull=False,
                                                                        created_at__gte=timezone.now() - timedelta(days=7)).count()
        
        emails_sent = ChatMessageHistory.objects.filter(lead__assign_to__in=agents, messageType='email', wroteBy__in=['agent', 'ai']).count()
        emails_replied = ChatMessageHistory.objects.filter(lead__assign_to__in=agents, messageType='email', wroteBy='client').count()
        avg_reply_rate = (emails_replied / emails_sent * 100) if emails_sent > 0 else 0

        weekly_reply_rates = []
        today = timezone.now().date()
        for i in range(4):
            end_date = today - timedelta(days=i*7)
            start_date = end_date - timedelta(days=6)

            emails_sent_week = ChatMessageHistory.objects.filter(
                lead__assign_to__in=agents,
                messageType='email',
                wroteBy__in=['agent', 'ai'],
                created_at__date__range=[start_date, end_date]
            ).count()

            emails_replied_week = ChatMessageHistory.objects.filter(
                lead__assign_to__in=agents,
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
                lead__assign_to__in=agents,
                messageType='call',
                created_at__date=current_day
            ).count()

            emails_on_day = ChatMessageHistory.objects.filter(
                lead__assign_to__in=agents,
                messageType='email',
                created_at__date=current_day
            ).count()

            leads_added_on_day = LeadModel.objects.filter(
                assign_to__in=agents,
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
            'daily_analytics': daily_analytics,
            'avg_reply_rate': avg_reply_rate,
            'weekly_reply_rates': weekly_reply_rates,
            'emails_sent': emails_sent,
            'emails_replied': emails_replied,
        }, status=HTTP_200_OK)


