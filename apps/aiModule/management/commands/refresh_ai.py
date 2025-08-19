from django.core.management.base import BaseCommand
from apps.users.models.lead_model import LeadModel
from apps.aiModule.utils.follow_up import refreshAI

class Command(BaseCommand):
    help = "Refreshes the AI for all leads"

    def handle(self, *args, **options):
        # leads = LeadModel.objects.all()
        # Those leads who's status != converted
        leads = LeadModel.objects.filter(status__in=['in_progress', 'not_initiated', 'over_due'])
        for lead in leads:
            try:
                self.stdout.write(self.style.SUCCESS(f"Refreshing AI for lead {lead.id}"))
                refreshAI(lead.id)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error refreshing AI for lead {lead.id}: {e}"))
