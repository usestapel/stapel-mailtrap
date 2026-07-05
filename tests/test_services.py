"""trap_email (emit + schema) and the retention sweep."""
import pytest

from stapel_mailtrap.models import TrappedEmail
from stapel_mailtrap.services import purge_expired, trap_email


@pytest.mark.django_db
def test_trap_email_emits_valid_event():
    from stapel_core.comm import on_action

    received = []

    @on_action("mailtrap.email.trapped")
    def _capture(event):
        received.append(event.payload)

    email = trap_email(
        to_email="a@b.com",
        subject="Hello",
        body_html="<p>hi</p>",
        body_text="hi",
        from_email="from@b.com",
        attachments=[{"filename": "x.pdf", "content_type": "application/pdf", "size": 10}],
        scope_key="ws-1",
    )

    # Event fired with the committed contract (VALIDATE_SCHEMAS is on in
    # conftest, so an off-schema payload would have raised).
    assert received, "mailtrap.email.trapped was not delivered"
    payload = received[0]
    assert payload["email_id"] == str(email.id)
    assert payload["to"] == "a@b.com"
    assert payload["scope_key"] == "ws-1"
    assert payload["attachment_count"] == 1
    assert "trapped_at" in payload


@pytest.mark.django_db
def test_store_body_off_drops_bodies(settings):
    settings.STAPEL_MAILTRAP = {"STORE_BODY": False}

    email = trap_email(to_email="a@b.com", subject="s", body_html="<p>x</p>", body_text="x")

    assert email.body_html == ""
    assert email.body_text == ""


@pytest.mark.django_db
def test_purge_by_ttl(settings):
    from datetime import timedelta

    from django.utils import timezone

    settings.STAPEL_MAILTRAP = {"TTL_DAYS": 7, "MAX_EMAILS": 0}

    old = trap_email(to_email="old@b.com", subject="old")
    TrappedEmail.objects.filter(id=old.id).update(
        created_at=timezone.now() - timedelta(days=30)
    )
    trap_email(to_email="fresh@b.com", subject="fresh")

    stats = purge_expired()

    assert stats["by_ttl"] == 1
    assert list(TrappedEmail.objects.values_list("to_email", flat=True)) == ["fresh@b.com"]


@pytest.mark.django_db
def test_purge_by_cap_keeps_newest(settings):
    settings.STAPEL_MAILTRAP = {"TTL_DAYS": 0, "MAX_EMAILS": 2}

    for i in range(5):
        trap_email(to_email=f"u{i}@b.com", subject=str(i))

    stats = purge_expired()

    assert stats["by_cap"] == 3
    assert TrappedEmail.objects.count() == 2
    # The two newest survive (u4, u3).
    remaining = set(TrappedEmail.objects.values_list("subject", flat=True))
    assert remaining == {"3", "4"}


@pytest.mark.django_db
def test_purge_noop_when_disabled(settings):
    settings.STAPEL_MAILTRAP = {"TTL_DAYS": 0, "MAX_EMAILS": 0}
    trap_email(to_email="a@b.com", subject="s")

    stats = purge_expired()

    assert stats == {"by_ttl": 0, "by_cap": 0}
    assert TrappedEmail.objects.count() == 1
