# stapel-mailtrap

[![CI](https://github.com/usestapel/stapel-mailtrap/actions/workflows/ci.yml/badge.svg)](https://github.com/usestapel/stapel-mailtrap/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/usestapel/stapel-mailtrap/graph/badge.svg)](https://codecov.io/gh/usestapel/stapel-mailtrap)

> An email trap (mail catcher) for dev/staging: outbound mail is captured into
> a `TrappedEmail` journal instead of being sent, and browsed through a
> read-only "Mail" API. Plugs into stapel-notifications' email-provider seam by
> dotted path — no module-to-module import.

Part of the [Stapel framework](https://github.com/usestapel) — composable Django apps
that deploy as a monolith or as microservices without changing module code.

## Install

```bash
pip install stapel-mailtrap
```

```python
# settings.py
INSTALLED_APPS = [
    # ...
    "stapel_mailtrap",
]

# urls.py
path("mailtrap/", include("stapel_mailtrap.urls"))
```

```bash
python manage.py migrate
```

## Trapping notifications email

Point stapel-notifications' email provider at the trap — one setting, no code:

```python
STAPEL_NOTIFICATIONS = {
    "EMAIL_PROVIDER": "stapel_mailtrap.provider.MailtrapEmailProvider",
}
```

Every email stapel-notifications would send is now persisted and inspectable
instead. The provider matches the notifications email duck type
(`send(recipient, subject, html_body, headers)`) — see MODULE.md §3.

## Trapping any backend

For a host whose own mail path should trap, call the service directly:

```python
from stapel_mailtrap import trap_email

trap_email(
    to_email="alice@example.com",
    from_email="bot@example.com",
    subject="Your code",
    body_html="<b>123456</b>",
    body_text="123456",
    attachments=[{"filename": "invoice.pdf", "content_type": "application/pdf", "size": 8123}],
    scope_key="workspace-42",   # opaque host scope
)
```

It persists the row and emits `mailtrap.email.trapped` transactionally.
Attachments are **metadata only** — raw bytes are never stored.

## HTTP API ("Письма" / Mail)

Read-only (the trap is filled by the provider / `trap_email`, never via the API):

| Route | Meaning |
|---|---|
| `GET mailtrap/emails/` | Trapped emails, newest first, paginated (anchor); `?scope_key=` filters |
| `GET mailtrap/emails/<uuid>/` | One trapped email — full HTML/text bodies + attachment metadata |

Default permission is staff/service only (trapped mail can contain OTPs and
magic links). Override `permission_classes` and set a `SCOPE_PROVIDER` for
per-tenant visibility — see MODULE.md.

## Retention

```python
STAPEL_MAILTRAP = {
    "MAX_EMAILS": 1000,   # hard cap on stored rows (0 disables)
    "TTL_DAYS": 30,       # delete rows older than N days (0 disables)
}
```

Run the sweep from any scheduler:

```bash
python manage.py purge_trapped_emails            # --dry-run supported
```

Or schedule the Celery task (celery is an optional host dependency):

```python
CELERY_BEAT_SCHEDULE = {
    "purge-trapped-emails": {
        "task": "stapel_mailtrap.tasks.purge_trapped_emails",
        "schedule": crontab(hour=3, minute=0),   # nightly
    },
}
```

## Settings

All configuration lives in the `STAPEL_MAILTRAP` namespace (dict setting, flat
setting, or env var — resolved lazily):

| Key | Default | Meaning |
|---|---|---|
| `SCOPE_PROVIDER` | `"stapel_mailtrap.scope.DefaultScopeProvider"` | Dotted path to a `ScopeProvider` subclass — the multi-tenant seam. |
| `MAX_EMAILS` | `1000` | Retention count cap (0 disables). |
| `TTL_DAYS` | `30` | Retention age cap in days (0 disables). |
| `STORE_BODY` | `True` | `False` stores the envelope only (bodies empty). |

## comm surface

| Kind | Name | Contract |
|---|---|---|
| Event | `mailtrap.email.trapped` | `{email_id, to, from?, subject, scope_key, attachment_count, trapped_at}` — [schema](schemas/emits/mailtrap.email.trapped.json) |

## Extension points

See [MODULE.md](MODULE.md) — the agent-facing map of every fork-free seam
(settings, the `ScopeProvider` seam, the notifications email-provider adapter
with its duck-typed contract, serializer seams, permissions, comm surface,
system checks).

## Development

```bash
pip install -e . && pip install pytest pytest-django pytest-cov ruff jsonschema
./setup-hooks.sh
pytest tests/
```

## License

MIT
