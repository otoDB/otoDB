import logging
from datetime import timedelta

from django.tasks import task, default_task_backend
from django.utils import timezone

from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def enqueue_deferred(task_obj, *args, delay: timedelta):
	"""Enqueue a task with run_after, skipping if the backend doesn't support defer."""
	if not default_task_backend.supports_defer:
		return
	task_obj.using(run_after=timezone.now() + delay).enqueue(*args)


@task
def send_email(
	subject: str,
	body: str,
	from_email: str,
	to: list[str],
) -> None:
	try:
		send_mail(
			subject=subject, message=body, from_email=from_email, recipient_list=to
		)
	except Exception:
		logger.exception('Failed to send email to %s', to)
