# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); this project adheres
to pre-1.0 semver (**minor = breaking**, patch = compatible).

## [0.1.0] - 2026-07-05

Initial release — an email trap (mail catcher) for the Stapel framework
(studio-design §7 SN-5).

### Added

- `TrappedEmail` model — captured outbound message (to/from/subject/HTML+text
  bodies/attachment metadata/headers/`scope_key`/`created_at`); journal row,
  no raw attachment bytes.
- `services.trap_email(...)` — persist one message and emit
  `mailtrap.email.trapped` transactionally (outbox pattern).
- `provider.MailtrapEmailProvider` — drop-in email provider for
  stapel-notifications, wired by dotted path
  (`STAPEL_NOTIFICATIONS["EMAIL_PROVIDER"]`), no module-to-module import;
  duck-typed `send(recipient, subject, html_body, headers)` with a
  `typing.Protocol` mirror (`provider.EmailProvider`).
- Read-only "Mail" DRF API: `GET emails/` (anchor pagination, `?scope_key=`
  filter) + `GET emails/<uuid>/` (full bodies + attachment metadata).
- `mailtrap.email.trapped` event + JSON Schema in `schemas/emits/`.
- `ScopeProvider` seam (`STAPEL_MAILTRAP["SCOPE_PROVIDER"]`) — multi-tenant
  queryset filtering; default single global scope.
- Retention: `MAX_EMAILS` + `TTL_DAYS` settings, `services.purge_expired()`,
  the `purge_trapped_emails` management command (`--dry-run`), and the
  `stapel_mailtrap.tasks.purge_trapped_emails` Celery task.
- Read-only admin, system checks (`W001`/`W002` on `SCOPE_PROVIDER`), MIT
  license, CI + PyPI trusted-publishing workflows.

[0.1.0]: https://github.com/usestapel/stapel-mailtrap/releases/tag/v0.1.0
