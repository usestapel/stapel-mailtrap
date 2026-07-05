"""Dataclass DTOs — the API models of stapel-mailtrap (never ORM instances)."""
from dataclasses import dataclass, field
from typing import List


@dataclass
class TrappedEmailListItem:
    """A trapped email in the list view (envelope, no bodies).

    Attributes:
        id: Message id (UUID).
        to_email: Recipient address.
        from_email: Sender address.
        subject: Subject line.
        scope_key: Opaque host scope (workspace/org/project/tenant).
        attachment_count: Number of attachments (metadata only).
        created_at: Capture time (tz-aware ISO 8601).
    """

    id: str
    to_email: str
    from_email: str
    subject: str
    scope_key: str
    attachment_count: int
    created_at: str


@dataclass
class TrappedEmailDetail:
    """A trapped email in the detail view (full bodies + attachment metadata).

    Attributes:
        id: Message id (UUID).
        to_email: Recipient address.
        from_email: Sender address.
        subject: Subject line.
        body_html: Rendered HTML body (empty when STORE_BODY is off).
        body_text: Plain-text body (empty when STORE_BODY is off).
        attachments: Attachment metadata dicts (filename/content_type/size).
        headers: Header snapshot.
        scope_key: Opaque host scope.
        created_at: Capture time (tz-aware ISO 8601).
    """

    id: str
    to_email: str
    from_email: str
    subject: str
    body_html: str
    body_text: str
    attachments: List[dict] = field(default_factory=list)
    headers: dict = field(default_factory=dict)
    scope_key: str = ""
    created_at: str = ""
