from django.core.management import BaseCommand
from django_q.tasks import schedule
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = "Starts the recursive fetch emails task loop"

    def handle(self, *args, **options):
        # Schedule the first run immediately (or in a few seconds)
        next_run = timezone.now() + timedelta(seconds=1)
        schedule('apps.aiModule.tasks.run_fetch_emails',
                 schedule_type='O',
                 next_run=next_run)
        self.stdout.write(self.style.SUCCESS(f"Started fetch emails loop. First run scheduled at {next_run}"))
