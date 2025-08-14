from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND
from rest_framework import status
from rest_framework.permissions import IsAuthenticated


from apps.emailModule.utils import search_email_by_sender, send_email, fetch_emails
import smtplib
from apps.users.permissions import IsAgent
from apps.users.models import AgentModel
from imap_tools.errors import MailboxLoginError
from apps.users.models import LeadEmailModel
from apps.aiModule.models import ChatMessageHistory
from apps.aiModule.utils.follow_up import refreshAI



# Create your models here.


class SearchEmailView(APIView):
    permission_classes = [IsAuthenticated, IsAgent]

    def post(self, request):
        try:
            agent = AgentModel.objects.get(user=request.user)
            email = agent.smtp_email
            password = agent.smtp_password
            to_email = request.data['to_email']
            # folder = request.data.get('folder', 'INBOX')
            if not LeadEmailModel.objects.filter(lead__assign_to=agent, email=to_email):
                return Response({'message': 'You can only search emails to leads assigned to you.'}, status=HTTP_400_BAD_REQUEST)

            results = search_email_by_sender(email, password, to_email)

            return Response(results, status=HTTP_200_OK)
        except AgentModel.DoesNotExist:
            return Response({'message': 'Agent profile not found'}, status=HTTP_404_NOT_FOUND)
        except smtplib.SMTPAuthenticationError:
            return Response({'message': 'Authentication failed. Please check your email and app password.'}, status=HTTP_401_UNAUTHORIZED)
        except smtplib.SMTPRecipientsRefused:
            return Response({'message': 'One or more recipient email addresses are invalid.'}, status=HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'message': f'Failed: {e}'}, status=HTTP_400_BAD_REQUEST)


class SendEmailView(APIView):
    permission_classes = [IsAuthenticated, IsAgent]

    def post(self, request):
        try:
            agent = AgentModel.objects.get(user=request.user)
            email = agent.smtp_email
            password = agent.smtp_password
            to_email = request.data['to_email']
            # check if the to_email belong to the lead of the agent

            if not LeadEmailModel.objects.filter(lead__assign_to=agent, email=to_email):
                return Response({'message': 'You can only send emails to leads assigned to you.'}, status=HTTP_400_BAD_REQUEST)

            send_email(
                from_email=email,
                app_password=password,
                to_email=to_email,
                subject=request.data['subject'],
                body=request.data['body']
            )
            return Response({'message': 'Email sent successfully'}, status=HTTP_200_OK)
        except AgentModel.DoesNotExist:
            return Response({'message': 'Agent profile not found'}, status=HTTP_404_NOT_FOUND)
        except smtplib.SMTPAuthenticationError:
            return Response({'message': 'Authentication failed. Please check your email and app password.'}, status=HTTP_401_UNAUTHORIZED)
        except smtplib.SMTPRecipientsRefused:
            return Response({'message': 'One or more recipient email addresses are invalid.'}, status=HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'message': f'Failed to send email: {e}'}, status=HTTP_400_BAD_REQUEST)


class FetchInboxView(APIView):
    permission_classes = [IsAuthenticated, IsAgent]

    def post(self, request):
        # get user email and password from request.user
        try:
            agent = AgentModel.objects.get(user=request.user)
            email = agent.smtp_email
            password = agent.smtp_password
            emails = fetch_emails(
                from_email=email,
                app_password=password,
            )
            print(
                f'Messageid :-> {emails[0].headers.get('message-id', [''])[0]}')

            results = [{
                'subject': msg.subject,
                'from': msg.from_,
                'date': msg.date,
                'body': msg.text or msg.html
            } for msg in emails]

            return Response(results, status=HTTP_200_OK)
        except AgentModel.DoesNotExist:
            return Response({'message': 'Agent profile not found'}, status=HTTP_404_NOT_FOUND)


class CheckNewEmail(APIView):
    # permission_classes = [IsAuthenticated, IsAgent]

    def get(self, request):
        # Get all of the Agent
        agents = AgentModel.objects.all()
        for agent in agents:
            email = agent.smtp_email
            password = agent.smtp_password
            # All the leads of the agent
            leads = LeadEmailModel.objects.filter(lead__assign_to=agent)
            for lead in leads:
                try:
                    emails = search_email_by_sender(
                        email, password, lead.email)
                except MailboxLoginError:
                    continue

                if emails:
                    for email in emails:
                        id = email['message-id']
                        if not ChatMessageHistory.objects.filter(pid=id).exists():
                            obj, is_created = ChatMessageHistory.objects.get_or_create(
                                lead=lead.lead,heading=email['subject'], body=email['body'], messageType='email', aiType='human', wroteBy='client', pid=id)
                            try:
                                refreshAI(lead.id)
                            except Exception as e:
                                return Response({'Error': f'Error in refreshing Lead of id {lead.id}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'message': 'No new emails found'}, status=HTTP_200_OK)
