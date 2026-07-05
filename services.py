"""Trap + retention services.

``trap_email`` is the single write path: it persists one ``TrappedEmail`` and
emits ``mailtrap.email.trapped`` in one transaction (the outbox pattern —
``mutate_and_emit``, so the event leaves iff the row commits).

``purge_expired`` is the retention sweep, shared by the management command and
the Celery task.
"""
from __future__ import annotations

import logging
from datetime import timedelta

from stapel_core.comm import mutate_and_emit

logger = logging.getLogger(__name__)


def trap_email(
    *,
    to_email: str,
    subject: str,
    body_html: str = "",
    body_text: str = "",
    from_email: str = "",
    attachments: list[dict] | None = None,
    headers: dict | None = None,
    scope_key: str = "",
):
    """Capture one outbound email and return the persisted ``TrappedEmail``.

    Emits ``mailtrap.email.trapped`` transactionally. ``attachments`` is
    metadata only (``{"filename", "content_type", "size"}`` dicts); raw bytes
    are never stored. Bodies are dropped when ``STORE_BODY`` is False.
    """
    from .conf import mailtrap_settings
    from .models import TrappedEmail

    attachments = attachments or []
    store_body = mailtrap_settings.STORE_BODY

    with mutate_and_emit() as emit:
        email = TrappedEmail.objects.create(
            to_email=to_email,
            from_email=from_email or "",
            subject=subject or "",
            body_html=body_html if store_body else "",
            body_text=body_text if store_body else "",
            attachments=attachments,
            headers=headers or {},
            scope_key=scope_key or "",
        )
        emit(
            "mailtrap.email.trapped",
            {
                "email_id": str(email.id),
                "to": email.to_email,
                "from": email.from_email,
                "subject": email.subject,
                "scope_key": email.scope_key,
                "attachment_count": len(attachments),
                "trapped_at": email.created_at.isoformat(),
            },
            key=str(email.id),
        )
    logger.info("[mailtrap] trapped email %s to=%s", email.id, _mask(to_email))
    return email


def purge_expired() -> dict:
    """Enforce retention: delete messages older than ``TTL_DAYS`` and, beyond
    ``MAX_EMAILS``, the oldest rows over the cap. Either limit set to 0
    disables that half. Returns ``{"by_ttl": int, "by_cap": int}``.
    """
    from django.utils import timezone

    from .conf import mailtrap_settings
    from .models import TrappedEmail

    ttl_days = int(mailtrap_settings.TTL_DAYS or 0)
    max_emails = int(mailtrap_settings.MAX_EMAILS or 0)

    by_ttl = 0
    if ttl_days > 0:
        cutoff = timezone.now() - timedelta(days=ttl_days)
        by_ttl, _ = TrappedEmail.objects.filter(created_at__lt=cutoff).delete()

    by_cap = 0
    if max_emails > 0:
        total = TrappedEmail.objects.count()
        overflow = total - max_emails
        if overflow > 0:
            # Oldest first: the ids past the newest MAX_EMAILS rows.
            stale_ids = list(
                TrappedEmail.objects.order_by("-created_at")
                .values_list("id", flat=True)[max_emails:]
            )
            by_cap, _ = TrappedEmail.objects.filter(id__in=stale_ids).delete()

    if by_ttl or by_cap:
        logger.info("[mailtrap] purge removed %d (ttl) + %d (cap)", by_ttl, by_cap)
    return {"by_ttl": by_ttl, "by_cap": by_cap}


def _mask(email: str) -> str:
    if "@" not in email:
        return "***"
    local, domain = email.split("@", 1)
    return f"{local[0]}***@{domain}" if local else f"***@{domain}"
