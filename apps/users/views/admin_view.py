from datetime import date, timedelta
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_200_OK, HTTP_401_UNAUTHORIZED


from apps.users.serializers.admin_serializer import (
    AdminLoginSerializer,
    TeamListSerializer,
)

from apps.users.serializers.manager_serializer import ManagerLeadListSerializer

from apps.users.permissions import IsAdmin
from apps.users.models import AgentModel, ManagerModel, CustomUser, LeadModel
from apps.aiModule.models import ChatMessageHistory



class AdminLoginView(APIView):
    serializer_class = AdminLoginSerializer

    def post(self, request):
        serializer = AdminLoginSerializer(data=request.data)

        if serializer.is_valid():
            return Response(serializer.validated_data, status=HTTP_200_OK)
        else:
            return Response(serializer.errors, status=HTTP_401_UNAUTHORIZED)


class ChangeStatusView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request):
        user_id = request.data.get('user_id')
        status = request.data.get('status')

        if not user_id or not status:
            return Response({'message': 'User ID and Status are required'}, status=HTTP_400_BAD_REQUEST)
        # Check if the user_id is of agent or manager

        try:
            if not type(bool(status)) == bool:
                return Response({'message': 'Status should be a boolean value'}, status=HTTP_400_BAD_REQUEST)
            agent = AgentModel.objects.get(id=user_id)
            agent.user.is_active = status
            agent.user.save()
            return Response({'message': 'Status changed successfully'}, status=HTTP_200_OK)
        except AgentModel.DoesNotExist:
            try:
                manager = ManagerModel.objects.get(id=user_id)
                manager.user.is_active = status
                manager.user.save()
                return Response({'message': 'Status changed successfully'}, status=HTTP_200_OK)
            except ManagerModel.DoesNotExist:
                return Response({'message': 'Agent or Manager not found'}, status=HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': 'An error occurred', 'error': str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)

class AdminLeadListView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        leads = LeadModel.objects.all()
        serializre = ManagerLeadListSerializer(leads, many=True)
        return Response(serializre.data, status=HTTP_200_OK)

class AdminTeamListView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        # all_users_except_admin = CustomUser.objects.exclude(role='admin')
        all_users_except_admin = CustomUser.objects.exclude(is_superuser=True)
        serializer = TeamListSerializer(all_users_except_admin, many=True)
        return Response(serializer.data, status=HTTP_200_OK)


        



class AdminCallAnalyticsView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        leads = LeadModel.objects.all().count()
        leads_this_week = LeadModel.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=7)).count()

        calls = ChatMessageHistory.objects.filter(
            messageType='call').count()
        week_calls = ChatMessageHistory.objects.filter(
            messageType='call', created_at__gte=timezone.now() - timedelta(days=7)).count()

        emails = ChatMessageHistory.objects.filter(
            messageType='email').count()
        week_emails = ChatMessageHistory.objects.filter(
            messageType='email', created_at__gte=timezone.now() - timedelta(days=7)).count()

        follow_ups = ChatMessageHistory.objects.filter(
            wroteBy='ai', follow_up_date__isnull=False).count()
        follow_ups_this_week = ChatMessageHistory.objects.filter(
            wroteBy='ai', follow_up_date__isnull=False,
            created_at__gte=timezone.now() - timedelta(days=7)).count()

        emails_sent = ChatMessageHistory.objects.filter(
            messageType='email', wroteBy__in=['agent', 'ai']).count()
        emails_replied = ChatMessageHistory.objects.filter(
            messageType='email', wroteBy='client').count()
        avg_reply_rate = (emails_replied / emails_sent *
                          100) if emails_sent > 0 else 0

        weekly_reply_rates = []
        today = timezone.now().date()
        for i in range(4):
            end_date = today - timedelta(days=i*7)
            start_date = end_date - timedelta(days=6)

            emails_sent_week = ChatMessageHistory.objects.filter(
                messageType='email',
                wroteBy__in=['agent', 'ai'],
                created_at__date__range=[start_date, end_date]
            ).count()

            emails_replied_week = ChatMessageHistory.objects.filter(
                messageType='email',
                wroteBy='client',
                created_at__date__range=[start_date, end_date]
            ).count()

            avg_reply_rate_week = (
                emails_replied_week / emails_sent_week * 100) if emails_sent_week > 0 else 0

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
                messageType='call',
                created_at__date=current_day
            ).count()

            emails_on_day = ChatMessageHistory.objects.filter(
                messageType='email',
                created_at__date=current_day
            ).count()

            leads_added_on_day = LeadModel.objects.filter(
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



class AdminDashboardView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        agents = AgentModel.objects.all()
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
            converted_count = LeadModel.objects.filter(
                assign_to=agent, status='converted').count()
            total_leads_count = LeadModel.objects.filter(assign_to=agent).count()
            agent_stat = {
                'agent': f"{agent.user.first_name} {agent.user.last_name}",
                'total_calls': ChatMessageHistory.objects.filter(
                    lead__assign_to=agent, messageType='call').count(),
                'total_follow_ups': ChatMessageHistory.objects.filter(
                    lead__assign_to=agent, wroteBy='ai', follow_up_date__isnull=False).count(),
                'average_lead_onboard': converted_count / total_leads_count * 100 if total_leads_count > 0 else 0

            }
            agents_stat.append(agent_stat)

        return Response({
            'total_calls': total_calls,
            'total_follow_ups': total_follow_ups,
            'average_lead_onboard': average_lead_onboard,
            'agents_stat': agents_stat
        }, status=HTTP_200_OK)
