from django.core.management import BaseCommand
from django.contrib.auth import get_user_model
import os


class Command(BaseCommand):

    help = "Create Django superuser"

    def handle(self, *args, **options):
        User = get_user_model()
        username = os.environ.get('DJANGO_USERNAME')
        email = os.environ.get('DJANGO_EMAIL')
        password = os.environ.get('DJANGO_PASSWORD')

        existing_users = User.objects.filter(username=username, email=email)
        if existing_users.exists() and existing_users[0].is_superuser:
            return
        User.objects.create_superuser(username, email, password)
