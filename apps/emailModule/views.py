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
from apps.aiModule.models import ChatMessageHistory
from apps.users.models import LeadModel

from apps.emailModule.outlook import OutlookEmail


# Create your models here.

outlookEmail = OutlookEmail()

class SearchEmailView(APIView):
    permission_classes = [ IsAgent]

    def post(self, request):
        try:
            agent = AgentModel.objects.get(user=request.user)
            email = agent.smtp_email
            password = agent.smtp_password
            to_email = request.data['to_email']
            email_provider = agent.email_provider
            # folder = request.data.get('folder', 'INBOX')
            if email_provider == 'gmail':
                
                if not LeadEmailModel.objects.filter(lead__assign_to=agent, email=to_email):
                    return Response({'message': 'You can only search emails to leads assigned to you.'}, status=HTTP_400_BAD_REQUEST)

                results = search_email_by_sender(email, password, to_email)
                return Response(results, status=HTTP_200_OK)
            
            elif email_provider == 'outlook':
                is_true, results = outlookEmail.search_outlook_email(password, to_email)
                if is_true:
                    return Response(results, status=HTTP_200_OK)

            return Response({'message': 'Invalid Request'}, status=HTTP_400_BAD_REQUEST)
        except AgentModel.DoesNotExist:
            return Response({'message': 'Agent profile not found'}, status=HTTP_404_NOT_FOUND)
        except smtplib.SMTPAuthenticationError:
            return Response({'message': 'Authentication failed. Please check your email and app password.'}, status=HTTP_401_UNAUTHORIZED)
        except smtplib.SMTPRecipientsRefused:
            return Response({'message': 'One or more recipient email addresses are invalid.'}, status=HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'message': f'Failed: {e}'}, status=HTTP_400_BAD_REQUEST)


class SendEmailView(APIView):
    permission_classes = [ IsAgent]

    def post(self, request):
        try:
            agent = AgentModel.objects.get(user=request.user)
            email = agent.smtp_email
            password = agent.smtp_password
            to_email = request.data['to_email']
            subject = request.data['subject']
            body = request.data['body']
            email_provider = agent.email_provider
            # check if the to_email belong to the lead of the agent

            if not LeadEmailModel.objects.filter(lead__assign_to=agent, email=to_email):
                return Response({'message': 'You can only send emails to leads assigned to you.'}, status=HTTP_400_BAD_REQUEST)

            if email_provider == 'gmail':
                send_email(
                    from_email=email,
                    app_password=password,
                    to_email=to_email,
                    subject=request.data['subject'],
                    body=request.data['body']
                )
            elif email_provider == 'outlook':
                is_true, message = outlookEmail.send_outlook_email(password, to_email, subject, body)
                if not is_true:
                    return Response({'message': message}, status=HTTP_400_BAD_REQUEST)

            chat_message = ChatMessageHistory.objects.create(
                lead = LeadEmailModel.objects.get(lead__assign_to=agent, email=to_email).lead,
                heading=subject,
                body=body,
                messageType='email',
                aiType='human',
                wroteBy='agent'
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
    permission_classes = [IsAgent]

    def post(self, request):
        # get user email and password from request.user
        try:
            agent = AgentModel.objects.get(user=request.user)
            if agent.email_provider == 'gmail':
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
            
            elif agent.email_provider == 'outlook':
                email = agent.smtp_email
                password = agent.smtp_password
                is_return, results = outlookEmail.get_outlook_all_email(password)
                if not is_return:
                    return Response({'message': results}, status=HTTP_400_BAD_REQUEST)
                return Response(results, status=HTTP_200_OK)
            
            return Response({'message': 'Invalid Request'}, status=HTTP_400_BAD_REQUEST)


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
            email_provider = agent.email_provider
            leads = LeadEmailModel.objects.filter(lead__assign_to=agent)
            # All the leads of the agent
            for lead in leads:
                if email_provider == 'gmail':
                    try:
                        emails = search_email_by_sender(
                            email, password, lead.email)
                    except MailboxLoginError:
                        continue
                elif email_provider == 'outlook':
                    is_true, emails = outlookEmail.search_outlook_email(password, lead.email)
                    if not is_true:
                        continue
                else:
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

class CheckNewEmailAgent(APIView):

    def get(self, request, id):
        try:
            agent = AgentModel.objects.get(id=id)
            email = agent.smtp_email
            password = agent.smtp_password
            email_provider = agent.email_provider
            leads = LeadEmailModel.objects.filter(lead__assign_to=agent)
            emails_found = False
            # All the leads of the agent
            for lead in leads:
                if email_provider == 'gmail':
                    try:
                        emails = search_email_by_sender(
                            email, password, lead.email)
                    except MailboxLoginError:
                        continue
                elif email_provider == 'outlook':
                    is_true, emails = outlookEmail.search_outlook_email(password, lead.email)
                    if not is_true:
                        continue
                else:
                    continue

                if emails:
                    emails_found = True
                    for email in emails:
                        id = email['message-id']
                        if not ChatMessageHistory.objects.filter(pid=id).exists():
                            obj, is_created = ChatMessageHistory.objects.get_or_create(
                                lead=lead.lead,heading=email['subject'], body=email['body'], messageType='email', aiType='human', wroteBy='client', pid=id)
                            try:
                                refreshAI(lead.id)
                            except Exception as e:
                                return Response({'Error': f'Error in refreshing Lead of id {lead.id}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            if not emails_found:
                return Response({'message': 'No new emails found'}, status=HTTP_200_OK)
            return Response({'message': 'New emails found'}, status=HTTP_200_OK)

        except AgentModel.DoesNotExist:
            return Response({'message': 'Agent profile not found'}, status=HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': f'Failed: {e}'}, status=HTTP_400_BAD_REQUEST)

class OutlookAuthTokenURLView(APIView):

    def get(self, request):
        url = outlookEmail.get_authroization_url()
        return Response({'url': url}, status=HTTP_200_OK)

class OutlookRefreshTokenView(APIView):
    def post(self, request):
        authorization_code = request.data.get('authorization_code')
        is_true, refresh_token = outlookEmail.get_refresh_token(authorization_code)
        if is_true:
            return Response({'refresh_token': refresh_token}, status=HTTP_200_OK)
        else:
            return Response({'error': 'Invalid authorization code'}, status=HTTP_400_BAD_REQUEST)


from apps.emailModule.templates.template import get_templates, get_template_by_id


class EmailTemplatesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Retrieve all email templates"""
        try:
            templates = get_templates()
            return Response({
                'templates': templates,
                'count': len(templates)
            }, status=HTTP_200_OK)
        except Exception as e:
            return Response({'message': f'Failed to retrieve templates: {e}'}, status=HTTP_400_BAD_REQUEST)


class EmailTemplateDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, template_id):
        """Retrieve a specific email template by ID"""
        try:
            template = get_template_by_id(template_id)
            if template:
                return Response(template, status=HTTP_200_OK)
            else:
                return Response({'message': 'Template not found'}, status=HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': f'Failed to retrieve template: {e}'}, status=HTTP_400_BAD_REQUEST)
class EmailTemplateWithLead(APIView):
    permission_classes = [IsAgent]

    def get(self, request, lead_id):
        """Retrieve all personalized email templates for a specific lead"""
        try:
            agent = AgentModel.objects.get(user=request.user)
            lead = LeadModel.objects.get(id=lead_id, assign_to=agent)
            templates = get_templates()

            # Personalize all templates
            lead_name = lead.name
            your_name = f"{agent.user.first_name} {agent.user.last_name}".strip()
            your_position = ""  # Not available in models
            your_company = ""  # Not available in models
            contact_info = agent.phone or agent.smtp_email

            personalized_templates = []
            for template in templates:
                personalized_subject = template['subject'].replace('[Lead Name]', lead_name).replace('[Your Name]', your_name)
                personalized_body = template['body'].replace('[Lead Name]', lead_name).replace('[Your Name]', your_name).replace('[Your Position]', your_position).replace('[Your Company]', your_company).replace('[Contact Information]', contact_info)

                personalized_template = {
                    'id': template['id'],
                    'name': template['name'],
                    'subject': personalized_subject,
                    'body': personalized_body
                }
                personalized_templates.append(personalized_template)

            return Response({
                'templates': personalized_templates,
                'count': len(personalized_templates)
            }, status=HTTP_200_OK)

        except AgentModel.DoesNotExist:
            return Response({'message': 'Agent profile not found'}, status=HTTP_404_NOT_FOUND)
        except LeadModel.DoesNotExist:
            return Response({'message': 'Lead not found or not assigned to you'}, status=HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': f'Failed to retrieve personalized templates: {e}'}, status=HTTP_400_BAD_REQUEST)
        