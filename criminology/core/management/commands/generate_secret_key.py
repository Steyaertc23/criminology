from django.core.management.base import BaseCommand
from django.core.management.utils import get_random_secret_key

class Command(BaseCommand):
    help = 'Generate a secure Django SECRET_KEY'

    def handle(self, *args, **kwargs):
        key = get_random_secret_key()
        self.stdout.write(self.style.SUCCESS(key))
