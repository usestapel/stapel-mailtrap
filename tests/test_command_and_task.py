"""The purge_trapped_emails command + the Celery task wrapper."""
from datetime import timedelta
from io import StringIO

import pytest
from django.core.management import call_command
from django.utils import timezone

from stapel_mailtrap.models import TrappedEmail
from stapel_mailtrap.services import trap_email


@pytest.mark.django_db
def test_command_purges(settings):
    settings.STAPEL_MAILTRAP = {"TTL_DAYS": 7, "MAX_EMAILS": 0}
    old = trap_email(to_email="old@b.com", subject="old")
    TrappedEmail.objects.filter(id=old.id).update(
        created_at=timezone.now() - timedelta(days=30)
    )
    trap_email(to_email="fresh@b.com", subject="fresh")

    out = StringIO()
    call_command("purge_trapped_emails", stdout=out)

    assert "Removed 1 by ttl" in out.getvalue()
    assert TrappedEmail.objects.count() == 1


@pytest.mark.django_db
def test_command_dry_run_deletes_nothing(settings):
    settings.STAPEL_MAILTRAP = {"TTL_DAYS": 0, "MAX_EMAILS": 1}
    trap_email(to_email="a@b.com", subject="a")
    trap_email(to_email="b@b.com", subject="b")

    out = StringIO()
    call_command("purge_trapped_emails", "--dry-run", stdout=out)

    assert "would remove" in out.getvalue()
    assert TrappedEmail.objects.count() == 2


@pytest.mark.django_db
def test_task_runs_sweep(settings):
    settings.STAPEL_MAILTRAP = {"TTL_DAYS": 0, "MAX_EMAILS": 1}
    trap_email(to_email="a@b.com", subject="a")
    trap_email(to_email="b@b.com", subject="b")

    from stapel_mailtrap.tasks import purge_trapped_emails

    # shared_task-wrapped callables expose the plain function via .run when
    # celery is installed; fall back to a direct call otherwise.
    fn = getattr(purge_trapped_emails, "run", purge_trapped_emails)
    stats = fn()

    assert stats["by_cap"] == 1
    assert TrappedEmail.objects.count() == 1
