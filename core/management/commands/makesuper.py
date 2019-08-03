from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        User = get_user_model()
        qs = User.objects.filter(username='admin')
        if not qs.exists():
            User.objects.create_superuser(
                'admin',
                'admin@domain.com',
                'admin'
            )
