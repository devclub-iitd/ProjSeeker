from django.core.management import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.auth import get_user_model
import os


class Command(BaseCommand):

    help = "Create Django dummy prof"

    def handle(self, *args, **options):
        User = get_user_model()
        prof_gp = Group.objects.get(name='prof')
        username = os.environ.get('DUMMY_USERNAME')
        email = os.environ.get('DUMMY_EMAIL')
        password = os.environ.get('DUMMY_PASSWORD')

        existing_user = User.objects.filter(username=username, email=email)
        if existing_user.exists():
            return
        user = User.objects.create(
            username=username, email=email, password=password)
        prof_gp.user_set.add(user)
