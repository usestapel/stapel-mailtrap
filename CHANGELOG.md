# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); this project adheres
to pre-1.0 semver (**minor = breaking**, patch = compatible).

## [Unreleased]

## [0.1.4] — 2026-07-17

### Changed
- `stapel-core` ceiling raised `>=0.10,<0.11` → `>=0.10,<0.12` (core 0.11
  fleet re-pin: default bus, nav, config-checks, error params/language —
  additive for modules). Suite green as-is.

## [0.1.3] — 2026-07-16

### Changed
- **v1 canon sweep §60** (api-versioning.md §2, §6): URL set moved to
  `urls_v1.py` (paths inside unchanged, `mailtrap` namespace preserved); the
  new root `urls.py` mounts it under `api/v1/`. Host mount `mailtrap/`
  unchanged: endpoints now serve at `/mailtrap/api/v1/emails/...` (the module
  previously had no `api/` segment at all — the canon adds `api/v1/`). No
  contract artifacts in this repo yet — nothing to regenerate.
- Lint hygiene to a clean `stapel-verify`: explicit `# noqa` on pre-existing
  findings.

### Changed
- Admin-suite AS-5: decorated `TrappedEmail` `@access.ops` (a delivery-log-shaped
  journal written exclusively by `services.trap_email` — no staff add/change
  workflow through the admin) and swapped `TrappedEmailAdmin`'s base class to
  `stapel_core.django.admin.base.StapelModelAdmin`, which now enforces the
  read-only contract instead of the two hand-rolled `has_*_permission`
  overrides. This also forbids admin-layer delete (previously allowed for
  manual cleanup) for everyone including the superuser; the retention sweep
  (`services.purge_expired()`, the management command / Celery task) is
  unaffected. No model in this repo carries credential material, so no
  `@access.secret` classification applies.

## [0.1.1] - 2026-07-06

### Changed
- Pinned `stapel-core` to the `>=0.8,<0.9` window (library-standard §7.1: one
  minor window; floor `0.8.0` is published on PyPI — no pin into the void).
- CI: added the release-track job (library-standard §7.4) — installs the package
  the way an end user does (`pip install .`, dependencies resolved from PyPI
  strictly by the declared pins, no git-main core, no editable siblings), asserts
  `stapel-core` resolves inside the `0.8` window, and runs an import smoke.
  Advisory (continue-on-error) until the whole stapel graph is on PyPI; becomes
  the blocking precondition for a `vX.Y.Z` tag once it is.


## [0.1.0] - 2026-07-05

Initial release — an email trap (mail catcher) for the Stapel framework
(studio-design §7 SN-5).

### Packaging
- Tests excluded from the built wheel/sdist (the `stapel_mailtrap.tests`
  subpackage is no longer listed in `[tool.setuptools] packages`). Added
  `[project.urls]`, completed the trove classifiers (MIT/OSI, Python 3.13,
  `Typing :: Typed`, OS Independent, `3 :: Only`, Development Status) and a
  `[tool.ruff]` lint section (single source shared with the git hooks/CI).

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

[0.1.1]: https://github.com/usestapel/stapel-mailtrap/releases/tag/v0.1.1
[0.1.0]: https://github.com/usestapel/stapel-mailtrap/releases/tag/v0.1.0
