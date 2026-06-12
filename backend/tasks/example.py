# === FEATURE: tasks ===
"""
Example background tasks using django-q2.

Enqueue an async task from anywhere in the codebase:

    from django_q.tasks import async_task
    async_task('tasks.example.send_welcome_email_task', user.id)

Schedule a recurring task via the Django admin (ORM scheduler) or in code:

    from django_q.models import Schedule
    Schedule.objects.create(
        func='tasks.example.daily_cleanup',
        schedule_type=Schedule.DAILY,
        name='Daily cleanup',
    )

Start the worker process:

    python manage.py qcluster
"""

import logging

logger = logging.getLogger(__name__)


def send_welcome_email_task(user_id: int) -> None:
    """
    Async task: send a welcome email to a newly registered user.

    Enqueue it right after user creation:

        from django_q.tasks import async_task
        async_task('tasks.example.send_welcome_email_task', user.id)
    """
    from django.contrib.auth import get_user_model

    User = get_user_model()
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        logger.warning("send_welcome_email_task: user %s not found", user_id)
        return

    # Replace with your actual email logic, e.g. using django.core.mail.send_mail
    logger.info("Sending welcome email to %s", user.email)


def daily_cleanup() -> None:
    """
    Scheduled task: run housekeeping jobs once per day.

    Register via Django admin > Q Schedules, or programmatically:

        from django_q.models import Schedule
        Schedule.objects.get_or_create(
            func='tasks.example.daily_cleanup',
            defaults={'schedule_type': Schedule.DAILY, 'name': 'Daily cleanup'},
        )
    """
    logger.info("Running daily cleanup")
    # Add your cleanup logic here, e.g. deleting expired tokens, old records, etc.
# === END FEATURE: tasks ===
