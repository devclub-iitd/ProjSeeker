from django.core.management import BaseCommand
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):

    help = "Creates Student and Professor groups and adds respective permissions"

    def handle(self, *args, **options):
        stud_perm = Permission.objects.get(codename="is_student")
        prof_perm = Permission.objects.get(codename="is_prof")
        stud_gp, _ = Group.objects.get_or_create(name="student")
        prof_gp, _ = Group.objects.get_or_create(name="prof")

        stud_gp.permissions.add(stud_perm)
        prof_gp.permissions.add(prof_perm)
