import os
from django.core.management.base import BaseCommand
from usuarios.models import CustomUser

class Command(BaseCommand):
    help = 'Create a superuser for production from environment variables'

    def handle(self, *args, **options):
        username = os.environ.get('ADMIN_USER')
        email = os.environ.get('ADMIN_EMAIL')
        password = os.environ.get('ADMIN_PASS')

        if not all([username, email, password]):
            self.stdout.write(self.style.ERROR(
                'The variables ADMIN_USER, ADMIN_EMAIL, and ADMIN_PASS must be defined.'
            ))
            return

        if not CustomUser.objects.filter(username=username).exists():
            CustomUser.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            self.stdout.write(self.style.SUCCESS(
                f'Superuser "{username}" created successfully.'
            ))
        else:
            self.stdout.write(self.style.WARNING(
                f'Superuser "{username}" already exists.'
            ))