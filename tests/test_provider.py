"""The notifications email-provider seam: dotted-path adapter + duck type."""
import pytest

from stapel_mailtrap.models import TrappedEmail
from stapel_mailtrap.provider import EmailProvider, MailtrapEmailProvider


def test_provider_matches_notifications_duck_type():
    # Structural check: MailtrapEmailProvider satisfies the notifications
    # email-provider Protocol (send(recipient, subject, html_body, headers)).
    assert isinstance(MailtrapEmailProvider(), EmailProvider)


@pytest.mark.django_db
def test_send_traps_instead_of_sending(settings):
    settings.DEFAULT_FROM_EMAIL = "bot@example.com"

    MailtrapEmailProvider().send(
        "alice@example.com",
        "Your code",
        "<b>123456</b>",
        {"List-Unsubscribe": "<mailto:x>"},
    )

    row = TrappedEmail.objects.get()
    assert row.to_email == "alice@example.com"
    assert row.from_email == "bot@example.com"
    assert row.subject == "Your code"
    assert row.body_html == "<b>123456</b>"
    assert row.headers == {"List-Unsubscribe": "<mailto:x>"}
    assert row.attachments == []


@pytest.mark.django_db
def test_send_resolves_provider_by_dotted_path():
    # The exact wiring stapel-notifications performs: import a provider by the
    # dotted path a host would put in STAPEL_NOTIFICATIONS["EMAIL_PROVIDER"],
    # instantiate, call .send. No import of stapel_notifications anywhere.
    from django.utils.module_loading import import_string

    provider_cls = import_string("stapel_mailtrap.provider.MailtrapEmailProvider")
    provider_cls().send("bob@example.com", "Hi", "<p>hi</p>", None)

    assert TrappedEmail.objects.filter(to_email="bob@example.com").exists()
