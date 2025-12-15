import logging
from django.core.management import call_command
from django_q.tasks import schedule
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)


def run_fetch_emails():
    logger.info("Starting run_fetch_emails task")
    try:
        call_command('fetch_emails')
        logger.info("run_fetch_emails task completed successfully")
    except Exception as e:
        logger.error(f"Error in run_fetch_emails: {e}")
    finally:
        # Schedule the next run in 5 minutes
        next_run = timezone.now() + timedelta(minutes=5)
        schedule('apps.aiModule.tasks.run_fetch_emails',
                 schedule_type='O',
                 next_run=next_run)
        logger.info(f"Scheduled next run_fetch_emails at {next_run}")
