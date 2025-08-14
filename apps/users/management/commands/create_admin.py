from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates a new admin user with role="admin" and superuser privileges.'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, required=True, help='Admin\'s email address')
        parser.add_argument('--password', type=str, required=True, help='Admin\'s password')
        parser.add_argument('--first_name', type=str, required=True, help='Admin\'s first name')
        parser.add_argument('--last_name', type=str, required=True, help='Admin\'s last name')

    def handle(self, *args, **options):
        email = options['email']
        password = options['password']
        first_name = options['first_name']
        last_name = options['last_name']

        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.ERROR(f'User with email {email} already exists.'))
            return

        try:
            User.objects.create_superuser(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role='admin'
            )
            self.stdout.write(self.style.SUCCESS(f'Successfully created admin user {email}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating admin user: {e}'))
