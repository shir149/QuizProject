from django.core.management.base import BaseCommand
from synaptic.models import User
from .demo_users import DEMO_USERS

class Command(BaseCommand):
    help = 'Creates generic demo users in the database.'

    def handle(self, *args, **options):
        try:
            for user in DEMO_USERS:
                User.objects.create_user(**user)
            self.stdout.write(self.style.SUCCESS('Successfully created demo users in the database.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An error occurred creating the users: {str(e)}'))

