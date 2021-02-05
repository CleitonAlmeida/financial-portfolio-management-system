from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.conf import settings

class Command(BaseCommand):

    def handle(self, *args, **options):
        if not User.objects.filter(username=settings.SUPER_USER['username']).exists():
            User.objects.create_superuser(settings.SUPER_USER['username'], settings.SUPER_USER['email'], settings.SUPER_USER['password'])
