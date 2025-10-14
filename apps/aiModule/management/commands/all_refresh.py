from django.core.management.base import BaseCommand
from apps.users.models import AgentModel, LeadEmailModel
from apps.users.models.lead_model import LeadModel
from apps.aiModule.models import ChatMessageHistory
from apps.emailModule.utils import search_email_by_sender
from apps.aiModule.utils.follow_up import refreshAI
from imap_tools.errors import MailboxLoginError
from apps.emailModule.outlook import OutlookEmail


class Command(BaseCommand):
    help = "Fetches new emails from leads, updates chat history, and refreshes AI for all leads"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting to fetch new emails and refresh AI..."))
        outlook_email = OutlookEmail()
        agents = AgentModel.objects.all()
        for agent in agents:
            self.stdout.write(self.style.SUCCESS(f"Fetching emails for agent {agent.user.email}"))
            email = agent.smtp_email
            password = agent.smtp_password
            email_provider = agent.email_provider
            leads = LeadEmailModel.objects.filter(lead__assign_to=agent)
            for lead in leads:
                self.stdout.write(f"Checking emails from lead {lead.email}")
                if email_provider == 'gmail':
                    try:
                        emails = search_email_by_sender(email, password, lead.email)
                    except MailboxLoginError:
                        self.stdout.write(self.style.ERROR(f"Login failed for agent {agent.user.email}"))
                        continue
                elif email_provider == 'outlook':
                    is_true, emails = outlook_email.search_outlook_email(password, lead.email)
                    if not is_true:
                        self.stdout.write(self.style.ERROR(f"Failed to fetch emails for agent {agent.user.email} from Outlook"))
                        continue
                else:
                    continue

                if emails:
                    for email_data in emails:
                        message_id = email_data['message-id']
                        if not ChatMessageHistory.objects.filter(pid=message_id).exists():
                            self.stdout.write(self.style.SUCCESS(f"New email found from {lead.email} with subject: {email_data['subject']}"))
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
                                self.stdout.write(f"Refreshing AI for lead {lead.lead.id}")
                                refreshAI(lead.lead.id)
                            except Exception as e:
                                self.stdout.write(self.style.ERROR(f"Error refreshing AI for lead {lead.lead.id}: {e}"))

        # Now refresh AI for all leads with status != converted
        leads = LeadModel.objects.filter(status__in=['in_progress', 'not_initiated', 'over_due'])
        for lead in leads:
            try:
                self.stdout.write(self.style.SUCCESS(f"Refreshing AI for lead {lead.id}"))
                refreshAI(lead.id)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error refreshing AI for lead {lead.id}: {e}"))
        self.stdout.write(self.style.SUCCESS("Finished fetching emails and refreshing AI."))