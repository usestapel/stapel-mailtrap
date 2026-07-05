"""Retention sweep for trapped emails — the cron-friendly entry point.

Deletes messages older than ``STAPEL_MAILTRAP['TTL_DAYS']`` and, beyond
``MAX_EMAILS``, the oldest rows over the cap. Run from any scheduler::

    python manage.py purge_trapped_emails
    python manage.py purge_trapped_emails --dry-run
"""
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Delete expired / overflowing trapped emails (TTL_DAYS + MAX_EMAILS)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Report what the current retention settings would remove, delete nothing.",
        )

    def handle(self, *args, **options):
        from stapel_mailtrap.conf import mailtrap_settings

        if options["dry_run"]:
            from datetime import timedelta

            from django.utils import timezone

            from stapel_mailtrap.models import TrappedEmail

            ttl_days = int(mailtrap_settings.TTL_DAYS or 0)
            max_emails = int(mailtrap_settings.MAX_EMAILS or 0)

            by_ttl = 0
            if ttl_days > 0:
                cutoff = timezone.now() - timedelta(days=ttl_days)
                by_ttl = TrappedEmail.objects.filter(created_at__lt=cutoff).count()
            by_cap = 0
            if max_emails > 0:
                by_cap = max(TrappedEmail.objects.count() - max_emails, 0)

            self.stdout.write(
                f"[dry-run] would remove {by_ttl} by ttl (>{ttl_days}d), "
                f"{by_cap} by cap (>{max_emails})"
            )
            return

        from stapel_mailtrap.services import purge_expired

        stats = purge_expired()
        self.stdout.write(
            self.style.SUCCESS(
                f"Removed {stats['by_ttl']} by ttl, {stats['by_cap']} by cap."
            )
        )
