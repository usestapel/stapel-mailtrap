"""The stapel-notifications email-provider adapter.

stapel-notifications resolves its email provider by short name **or dotted
path** (``STAPEL_NOTIFICATIONS["EMAIL_PROVIDER"]``) and calls, per send::

    provider.send(recipient, subject, html_body, headers: dict | None) -> None

That is a **duck-typed contract**, not an imported base class — stapel modules
never import each other (invariant I2). ``MailtrapEmailProvider`` implements
exactly that signature, so wiring the trap into notifications is one setting in
the host project and **no import of stapel-notifications here**::

    STAPEL_NOTIFICATIONS = {
        "EMAIL_PROVIDER": "stapel_mailtrap.provider.MailtrapEmailProvider",
    }

``Protocol`` below documents the seam and lets a type checker verify the
signature without a runtime dependency on the notifications package.
"""
from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class EmailProvider(Protocol):
    """The stapel-notifications email-provider duck type (mirror, not import).

    Kept in lockstep with stapel-notifications ``channels/email.py``. If the
    upstream signature changes, this Protocol and ``MailtrapEmailProvider``
    move together — the notifications module is the contract owner.
    """

    def send(
        self, recipient: str, subject: str, html_body: str, headers: dict | None
    ) -> None: ...


class MailtrapEmailProvider:
    """Notifications email provider that traps instead of sending.

    Resolves the sender from ``DEFAULT_FROM_EMAIL``. The notifications email
    seam passes only ``(recipient, subject, html_body, headers)`` — there is
    no separate text body or attachment list on that call — so ``body_text``
    is left empty and ``attachments`` empty for this path. (The richer
    ``services.trap_email`` accepts both for hosts whose own backend traps
    directly.)
    """

    def send(
        self, recipient: str, subject: str, html_body: str, headers: dict | None
    ) -> None:
        from django.conf import settings

        from .services import trap_email

        trap_email(
            to_email=recipient,
            subject=subject,
            body_html=html_body,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", ""),
            headers=headers or {},
        )
