from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from bughunter_site.accounts.models import User

class Command(BaseCommand):
    help = 'Clean up unverified users older than 24 hours'

    def handle(self, *args, **options):
        cutoff_time = timezone.now() - timedelta(hours=24)
        unverified_users = User.objects.filter(
            is_verified=False,
            date_joined__lt=cutoff_time
        )
        
        count = unverified_users.count()
        unverified_users.delete()
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully deleted {count} unverified users')
        )