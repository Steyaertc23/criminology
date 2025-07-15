"""
@file user/tasks.py
@brief Celery task definitions for user-related background jobs.
@details
Includes asynchronous tasks such as deleting expired user accounts.
"""

from celery import shared_task
from django.utils.timezone import now
from django.contrib.auth import get_user_model


@shared_task
def delete_expired_users():
    """
    @brief Deletes users whose expiration date/time has passed.

    @details
    Retrieves all user instances whose `expiration_date` is less than or equal
    to the current time, deletes them from the database, and returns a summary
    message.

    @return str: Message indicating the number of users deleted.
    """
    User = get_user_model()
    expired_users = User.objects.filter(expiration_date__lte=now())
    count = expired_users.count()
    if count:
        expired_users.delete()
    return f"Deleted {count} expired users."
