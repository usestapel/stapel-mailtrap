# stapel-mailtrap — MODULE.md

Agent-facing map of this module: what it provides, its fork-free extension
points, and the anti-patterns those extension points make unnecessary. Use it
to classify a desired change as **app-layer override** (use an extension point
below, no fork) vs **upstream contribution** (change to this package via the
contribution pipeline). Stapel modules never import each other; all
cross-module interaction goes through `stapel_core.comm` (events + functions).

- pip package: `stapel-mailtrap` (import `stapel_mailtrap`), depends only on `stapel-core`
- Django app label: `mailtrap` (`stapel_mailtrap.apps.MailtrapConfig`)
- Optional host dependency: `celery` (only for the scheduled retention task)

## What this module provides

An **email trap** (mail catcher) for dev/staging, where SMTP is closed
(system-design S4): outbound mail is captured, never sent. It is the sink
behind the Studio `send_email` gateway verb (studio-design §1.3, §7 SN-5).

| Area | Details |
|---|---|
| Capture | `services.trap_email(...)` persists one `TrappedEmail` row (to/from/subject/html+text bodies/attachment **metadata**/headers/scope_key) and emits `mailtrap.email.trapped` in one transaction (outbox) |
| notifications provider | `provider.MailtrapEmailProvider` — a drop-in email provider for stapel-notifications, wired by **dotted path** (no import of that package) |
| Mail API ("Письма") | Read-only DRF: `GET emails/` (paginated, filter `?scope_key=`) + `GET emails/<uuid>/` (full bodies + attachment metadata) |
| Retention | `MAX_EMAILS` + `TTL_DAYS` settings; `services.purge_expired()` sweep exposed as the `purge_trapped_emails` command and the `stapel_mailtrap.tasks.purge_trapped_emails` Celery task |
| Admin | Read-only journal admin (inspect + delete only) |

Public API (`stapel_mailtrap.__all__`, PEP 562 lazy): `mailtrap_settings`,
`MailtrapEmailProvider`, `ScopeProvider`, `DefaultScopeProvider`, `trap_email`,
`purge_expired`.

## Extension points (fork-free)

### 1. Settings — the `STAPEL_MAILTRAP` namespace (`conf.py`)

`mailtrap_settings = AppSettings("STAPEL_MAILTRAP", ...)`. Resolution per key:
`settings.STAPEL_MAILTRAP[key]` → flat Django setting of the same name → env
var → default. Values are read lazily (never frozen at import).

| Key | Default | Semantics | Purpose |
|---|---|---|---|
| `SCOPE_PROVIDER` | `"stapel_mailtrap.scope.DefaultScopeProvider"` | single strategy, **REPLACE** (dotted path) | Multi-tenant seam — filters the Mail API queryset (see §2) |
| `MAX_EMAILS` | `1000` | value | Retention: hard cap on stored rows; `0` disables the count cap |
| `TTL_DAYS` | `30` | value | Retention: delete rows older than N days; `0` disables the age cap |
| `STORE_BODY` | `True` | value | `False` → store the envelope only (bodies empty) for a lighter footprint |

### 2. Scope provider — dotted path (`scope.py`)

The trap is scope-agnostic: `TrappedEmail.scope_key` is an opaque string the
host owns. `STAPEL_MAILTRAP["SCOPE_PROVIDER"]` is a dotted path to a
`ScopeProvider` subclass (single strategy, REPLACE):

```python
class ScopeProvider:
    def filter(self, queryset, request): ...   # restrict to the request's scope
```

The default `DefaultScopeProvider` is a no-op (single global scope). A
multi-tenant host returns e.g. the active `workspace_id`/`project_id` and
filters the queryset — so one tenant never reads another's trapped mail (which
can contain OTPs and magic links). The `?scope_key=` query param on the list
endpoint filters **within** the scope the provider already permits.

Set `scope_key` at capture time by calling `trap_email(..., scope_key=...)`
from a host backend; the notifications provider path leaves it empty (the
notifications email seam carries no scope), so multi-tenant hosts that route
notifications through the trap scope in their `SCOPE_PROVIDER.filter`.

### 3. notifications email provider — duck-typed dotted path (`provider.py`)

stapel-notifications resolves its email provider by short name **or dotted
path** and calls, per send:

```python
provider.send(recipient, subject, html_body, headers: dict | None) -> None
```

That is a **duck-typed contract** (a `send` signature), not an imported base
class — modules never import each other. `MailtrapEmailProvider` implements
exactly it; `provider.EmailProvider` is a `typing.Protocol` mirror that
documents the seam and lets a type checker verify the signature without a
runtime dependency on stapel-notifications. **stapel-notifications is the
contract owner**: if its email seam changes, the Protocol and provider move
with it.

Wire it in the host project (one setting, no code):

```python
STAPEL_NOTIFICATIONS = {
    "EMAIL_PROVIDER": "stapel_mailtrap.provider.MailtrapEmailProvider",
}
```

For a host whose own (non-notifications) mail backend should trap, call
`services.trap_email(...)` directly — it takes the full envelope, both bodies,
attachment metadata, headers and `scope_key`.

### 4. Serializer seams (`views.py`)

Both views carry `response_serializer_class` via `SerializerSeamMixin`
(defaults `TrappedEmailListItemSerializer` / `TrappedEmailDetailSerializer`,
dataclass-DTO backed). Swap by subclassing the view and remounting.

### 5. Permissions

Default `permission_classes = [IsStaffUser | IsServiceRequest]` — conservative,
because trapped mail can contain secrets. Override in a subclass to widen
(e.g. project owners in Studio) or tighten; pair with `SCOPE_PROVIDER` for
per-tenant visibility.

## comm surface

| Kind | Name | Contract |
|---|---|---|
| Event (emit) | `mailtrap.email.trapped` | `{email_id, to, from?, subject, scope_key, attachment_count, trapped_at}` — [schema](schemas/emits/mailtrap.email.trapped.json). Public event; consumers surface a feed/count. Bodies are **not** in the payload — fetch by `email_id` via the Mail API. |

This module registers no comm Functions and consumes no events.

## System checks

- `stapel_mailtrap.W001` — `SCOPE_PROVIDER` dotted path fails to import.
- `stapel_mailtrap.W002` — `SCOPE_PROVIDER` is not a `ScopeProvider` subclass.

W-level on purpose: a bad scope provider degrades the API, it must not block
deploys — the trap keeps capturing mail regardless.

## Anti-patterns (what the seams make unnecessary)

- **Importing stapel-notifications** to register the provider — never; the
  provider is a dotted path resolved on the notifications side.
- **Storing raw attachment bytes** — the trap is a journal; only metadata
  (`filename`/`content_type`/`size`) is stored.
- **Putting bodies in the event payload** — they live on the row, fetched by
  `email_id`; the event stays small and PII-light.
- **A per-tenant fork of the queryset** — use `SCOPE_PROVIDER.filter`.
- **A `os.getenv` at import time** — all config flows through `conf.py`.

## App-layer override vs upstream contribution

Litmus (stdlib-contribution-pipeline): *needs a monkeypatch or an edit inside
this package → upstream; a setting / subclass / dotted-path suffices →
app-layer.*

- New scope rule, custom permissions, alternate serializers, different
  retention numbers, wiring into a non-notifications backend → **app-layer**
  (settings/subclass/`trap_email`).
- A new field on `TrappedEmail`, a change to the emitted schema, a second
  event, a swappable model → **upstream contribution**.
