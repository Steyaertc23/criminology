# users/management/commands/setup_periodic_tasks.py

from django.core.management.base import BaseCommand
from django_celery_beat.models import CrontabSchedule, PeriodicTask
import json


class Command(BaseCommand):
    """
    @brief Management command to create a monthly periodic task for deleting expired users.
    """

    help = "Creates periodic task for deleting expired users monthly"

    def handle(self, *args, **kwargs):
        # Define the monthly schedule at midnight on the 1st day of each month
        schedule, _ = CrontabSchedule.objects.get_or_create(
            minute="0",
            hour="0",
            day_of_month="1",
            month_of_year="*",
            day_of_week="*",
        )

        # Create the periodic task if it does not exist
        periodic_task, created = PeriodicTask.objects.get_or_create(
            name="Monthly Delete Expired Users",
            task="users.tasks.delete_expired_users",
            defaults={"crontab": schedule, "args": json.dumps([])},
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS("Periodic task created successfully.")
            )
        else:
            self.stdout.write(
                self.style.WARNING("Periodic task already exists.")
            )
