"""Settings namespace for stapel-mailtrap.

All configuration is read through ``mailtrap_settings`` (lazily, at call
time) — never via module-level ``os.getenv`` (values would freeze at import,
docs/library-standard.md §3.1). Resolution order per key:
``settings.STAPEL_MAILTRAP`` dict -> flat Django setting of the same name ->
environment variable -> default below.

Dotted-path keys listed in ``import_strings`` are resolved with
``import_string`` — the fork-free escape hatch for swappable behavior.
"""
from stapel_core.conf import AppSettings

mailtrap_settings = AppSettings(
    "STAPEL_MAILTRAP",
    defaults={
        # Dotted path to a stapel_mailtrap.scope.ScopeProvider subclass —
        # the multi-tenant seam (single strategy, REPLACE semantics). The
        # default is a single global scope (every mail gets scope_key="").
        "SCOPE_PROVIDER": "stapel_mailtrap.scope.DefaultScopeProvider",
        # Retention: hard cap on stored messages. The retention sweep
        # (services.purge_expired / the purge_trapped_emails command / the
        # Celery task) deletes the oldest rows beyond this many. 0 disables
        # the count cap.
        "MAX_EMAILS": 1000,
        # Retention: delete messages older than this many days. 0 disables
        # the age cap.
        "TTL_DAYS": 30,
        # Store rendered HTML/text bodies on the row. A host that only needs
        # the envelope (to/from/subject) for a lighter footprint can set this
        # False; bodies are then stored empty.
        "STORE_BODY": True,
    },
    import_strings=("SCOPE_PROVIDER",),
)

__all__ = ["mailtrap_settings"]
