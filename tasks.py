"""Celery task of stapel-mailtrap.

Schedule the retention sweep in the host project::

    CELERY_BEAT_SCHEDULE = {
        "purge-trapped-emails": {
            "task": "stapel_mailtrap.tasks.purge_trapped_emails",
            "schedule": crontab(hour=3, minute=0),  # nightly
        },
    }

The task goes through the same ``services.purge_expired`` sweep as the
``purge_trapped_emails`` management command (``MAX_EMAILS`` + ``TTL_DAYS``).
``celery`` is not a hard dependency of this package — if it is not installed
the module still works (trap + API); only this scheduled entry point is
unavailable, and hosts can call the command from any cron instead.
"""
import logging

logger = logging.getLogger(__name__)

try:
    from celery import shared_task
except ImportError:  # pragma: no cover - celery is an optional host dependency
    shared_task = None


def _purge() -> dict:
    from .services import purge_expired

    stats = purge_expired()
    logger.info(
        "purge_trapped_emails: removed %d by ttl, %d by cap",
        stats["by_ttl"],
        stats["by_cap"],
    )
    return stats


if shared_task is not None:

    @shared_task(name="stapel_mailtrap.tasks.purge_trapped_emails")
    def purge_trapped_emails() -> dict:
        """Delete expired/overflowing trapped emails. Returns the sweep stats."""
        return _purge()

else:  # pragma: no cover

    def purge_trapped_emails() -> dict:
        """Delete expired/overflowing trapped emails. Returns the sweep stats."""
        return _purge()
