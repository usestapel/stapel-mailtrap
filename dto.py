"""Dataclass DTOs — the API models of stapel-mailtrap (never ORM instances)."""
from dataclasses import dataclass, field
from typing import List


@dataclass
class TrappedEmailListItem:
    """A trapped email in the list view (envelope, no bodies).

    Attributes:
        id: Message id (UUID). Example: 3f2b8c1e-5a4d-4e6f-9b7a-1c2d3e4f5a6b
        to_email: Recipient address. Example: user@example.com
        from_email: Sender address. Example: noreply@example.com
        subject: Subject line. Example: Your sign-in code
        scope_key: Opaque host scope (workspace/org/project/tenant). Example: acme
        attachment_count: Number of attachments (metadata only). Example: 0
        created_at: Capture time (tz-aware ISO 8601). Example: 2026-11-20T10:30:00+00:00
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
        id: Message id (UUID). Example: 3f2b8c1e-5a4d-4e6f-9b7a-1c2d3e4f5a6b
        to_email: Recipient address. Example: user@example.com
        from_email: Sender address. Example: noreply@example.com
        subject: Subject line. Example: Your sign-in code
        body_html: Rendered HTML body (empty when STORE_BODY is off). Example: <p>Your code is 123456</p>
        body_text: Plain-text body (empty when STORE_BODY is off). Example: Your code is 123456
        attachments: Attachment metadata dicts (filename/content_type/size). Example: [{"filename": "invoice.pdf", "content_type": "application/pdf", "size": 18234}]
        headers: Header snapshot. Example: {"Reply-To": "support@example.com"}
        scope_key: Opaque host scope. Example: acme
        created_at: Capture time (tz-aware ISO 8601). Example: 2026-11-20T10:30:00+00:00
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
