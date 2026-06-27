from django.core.management.base import BaseCommand
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import User


class Command(BaseCommand):
    help = 'Create a JWT token pair for a test user (only works when DEBUG=True)'

    def handle(self, *args, **options):
        if not settings.DEBUG:
            self.stderr.write('create_test_token only works when DEBUG=True')
            raise SystemExit(1)

        email = 'e2e-test@saaskiller.local'
        user, _ = User.objects.get_or_create(
            email=email,
            defaults={},
        )

        refresh = RefreshToken.for_user(user)
        self.stdout.write(f'ACCESS={str(refresh.access_token)} REFRESH={str(refresh)}')
