"""Models for stapel-mailtrap.

``TrappedEmail`` is a captured outbound message — an append-only journal row.
House rules (docs/library-standard.md §3.8): the ``id`` is a UUID so
``mailtrap.email.trapped``'s ``email_id`` is a stable cross-service handle;
there is no FK to any user or tenant model — ownership/tenancy is the opaque
``scope_key`` string the host resolves through the scope seam.
"""
import uuid

from django.db import models


class TrappedEmail(models.Model):
    """One outbound email captured instead of sent.

    Attachments are stored as *metadata only* (filename/content_type/size) —
    the trap is a journal, not a mailbox; it never persists raw attachment
    bytes.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    to_email = models.CharField(max_length=998)
    from_email = models.CharField(max_length=998, blank=True, default="")
    subject = models.CharField(max_length=998, blank=True, default="")

    body_html = models.TextField(blank=True, default="")
    body_text = models.TextField(blank=True, default="")

    # List of {"filename", "content_type", "size"} dicts — metadata only.
    attachments = models.JSONField(default=list, blank=True)
    # Opaque headers snapshot (List-Unsubscribe, custom headers, ...).
    headers = models.JSONField(default=dict, blank=True)

    # Opaque host scope (workspace/org/project/tenant). Empty = global.
    scope_key = models.CharField(max_length=255, blank=True, default="", db_index=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            # Names kept <=30 chars (docs/library-standard.md §2).
            models.Index(fields=["scope_key", "created_at"], name="mailtrap_scope_created"),
        ]

    def __str__(self) -> str:
        return f"{self.subject or '(no subject)'} -> {self.to_email}"
