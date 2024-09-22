from django.core.management.base import BaseCommand
import secrets

class Command(BaseCommand):
    help = 'Seeds the database with initial reference data.'

    def handle(self, *args, **options):
        print("New secret key is:", secrets.token_hex(24))