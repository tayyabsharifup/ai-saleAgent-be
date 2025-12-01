from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status

from apps.aiModule.models import ChatMessageHistory, NewLeadCall
from apps.aiModule.serializers import ChatMessageHistorySerializer, NewLeadCallSerializer
from apps.aiModule.utils.follow_up import refreshAI
from apps.aiModule.utils.util_model import save_call_message

from apps.users.models.lead_model import LeadModel
from apps.users.permissions import IsAgent, IsManager, IsAdmin


from apps.users.models import LeadEmailModel
from apps.users.models.lead_model import LeadModel
from apps.aiModule.models import ChatMessageHistory
from apps.emailModule.utils import search_email_by_sender
from apps.aiModule.utils.follow_up import refreshAI
from imap_tools.errors import MailboxLoginError
from apps.emailModule.outlook import OutlookEmail

from django_q.tasks import async_task


# Create your views here.


class chatHistoryView(generics.ListCreateAPIView):
    serializer_class = ChatMessageHistorySerializer
    permission_classes = [IsAgent | IsManager | IsAdmin]

    def get_queryset(self):
        lead_id = self.request.query_params.get('lead_id', None)
        if lead_id is not None:
            return ChatMessageHistory.objects.filter(lead_id=lead_id, wroteBy='ai')
        return ChatMessageHistory.objects.filter(wroteBy='ai')

    def perform_create(self, serializer):
        lead_id = self.request.data.get('lead_id', None)
        if lead_id:
            serializer.save(lead_id=lead_id)
        else:
            serializer.save()


class chatHistoryAgentView(generics.ListAPIView):
    serializer_class = ChatMessageHistorySerializer
    permission_classes = [IsAgent | IsManager | IsAdmin]

    def get_queryset(self):
        agent_id = self.request.query_params.get('agent_id', None)
        if agent_id is not None:
            return ChatMessageHistory.objects.filter(lead__assign_to=agent_id, wroteBy='ai')


class refreshAIFollowUpView(APIView):
    permission_classes = [IsAgent | IsManager | IsAdmin]

    def get(self, request):
        agent_id = request.query_params.get('id', None)
        if agent_id is not None:
            leads = LeadModel.objects.filter(assign_to=agent_id)
            for lead in leads:
                try:
                    refreshAI(lead.id)
                except:
                    return Response({'Error': f'Error in refreshing Lead of id {lead.id}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return Response({'message': f'Agent Lead Refreshed'}, status=status.HTTP_200_OK)
        else:
            return Response({'Error': 'No Agent id provided'}, status=status.HTTP_400_BAD_REQUEST)


class AddLeadInfo(APIView):
    permission_classes = [IsAgent | IsManager | IsAdmin]

    def post(self, request):
        lead_id = request.data.get('lead_id', None)
        info = request.data.get('info', None)
        if not lead_id or not info:
            return Response({'Error': 'No lead_id or info provided'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            lead = LeadModel.objects.get(id=lead_id)
            chat = ChatMessageHistory.objects.create(
                lead=lead, heading='Manual Conversation added between Client and Agent', body=info,
                messageType='manual', aiType='human', interestLevel='none', wroteBy='agent')
            chat.save()
        except:
            return Response({'Error': 'Lead not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'message': 'Lead Info Added'}, status=status.HTTP_200_OK)


class UnmapCallView(APIView):

    permission_classes = [IsAgent]

    def get(self, request):
        agent = request.user.agentmodel
        newLeadCalls = NewLeadCall.objects.filter(agent=agent)
        serializer = NewLeadCallSerializer(newLeadCalls, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        lead_id = request.data.get('lead_id', None)
        newLeadCall_id = request.data.get('newLeadCall_id', None)

        if not lead_id or not newLeadCall_id:
            return Response({'Error': 'No lead_id or newLeadCall_id provided'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            lead = LeadModel.objects.get(id=lead_id)
            # check if the lead is connected to the agent
            if lead.assign_to != request.user.agentmodel:
                return Response({'Error': 'Lead is not assigned to this agent'}, status=status.HTTP_400_BAD_REQUEST)
            newLeadCall = NewLeadCall.objects.get(id=newLeadCall_id)

            save_call_message(lead.id, newLeadCall.transcript)

            refreshAI(lead.id)
            newLeadCall.is_map = True
            newLeadCall.save()
            return Response({'message': 'Lead Mapped'}, status=status.HTTP_200_OK)

        except LeadModel.DoesNotExist:
            return Response({'Error': 'Lead not found'}, status=status.HTTP_404_NOT_FOUND)
        except NewLeadCall.DoesNotExist:
            return Response({'Error': 'NewLeadCall not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            raise e


class RefreshAgentView(APIView):
    permission_classes = [IsAgent]

    def get(self, request):
        agent = request.user.agentmodel

        outlook_email = OutlookEmail()
        email = agent.smtp_email
        password = agent.smtp_password
        email_provider = agent.email_provider

        # Get leads for this specific agent
        leads = LeadEmailModel.objects.filter(lead__assign_to=agent)

        if not leads.exists():
            print(f"No leads found for agent {agent.user.email}")
            return Response({'message': f"No leads found for agent {agent.user.email}"}, status=status.HTTP_200_OK)

        for lead in leads:
            print(f"Checking emails from lead {lead.email}")
            if email_provider == 'gmail':
                try:
                    emails = search_email_by_sender(
                        email, password, lead.email)
                except MailboxLoginError:
                    print(f"Login failed for agent {agent.user.email}")
                    return Response({'Error': f"Login failed for agent {agent.user.email}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            elif email_provider == 'outlook':
                is_true, emails = outlook_email.search_outlook_email(
                    password, lead.email)
                if not is_true:
                    print(
                        f"Failed to fetch emails for agent {agent.user.email} from Outlook")
                    return Response({'Error': f"Failed to fetch emails for agent {agent.user.email} from Outlook"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                print(
                    f"Unsupported email provider {email_provider} for agent {agent.user.email}")
                return Response({'Error': f"Unsupported email provider {email_provider}"}, status=status.HTTP_400_BAD_REQUEST)

            if emails:
                for email_data in emails:
                    message_id = email_data['message-id']
                    if not ChatMessageHistory.objects.filter(pid=message_id).exists():
                        print(
                            f"New email found from {lead.email} with subject: {email_data['subject']}")
                        ChatMessageHistory.objects.create(
                            lead=lead.lead,
                            heading=email_data['subject'],
                            body=email_data['body'],
                            messageType='email',
                            aiType='human',
                            wroteBy='client',
                            pid=message_id
                        )
                        try:
                            print(f"Refreshing AI for lead {lead.lead.id}")
                            refreshAI(lead.lead.id)
                        except Exception as e:
                            return Response(f"Error refreshing AI for lead {lead.lead.id}: {e}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Now refresh AI for all leads assigned to this specific agent with status != converted
        agent_leads = LeadModel.objects.filter(
            assign_to=agent,
            status__in=['in_progress', 'not_initiated', 'over_due']
        )

        if not agent_leads.exists():
            print(
                f"No leads with active status found for agent {agent.user.email}")
        else:
            for lead in agent_leads:
                try:
                    print(f"Refreshing AI for lead {lead.id}")
                    refreshAI(lead.id)
                except Exception as e:
                    return Response(f"Error refreshing AI for lead {lead.id}: {e}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'message': f"Finished fetching emails and refreshing AI for agent {agent.user.email}."}, status=status.HTTP_200_OK)
