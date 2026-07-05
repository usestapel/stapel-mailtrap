"""stapel-mailtrap — an email trap (mail catcher) for the Stapel framework.

In dev/staging, outbound mail must not leave the box (system-design S4: SMTP
is closed). This module is the sink: an email "provider" that, instead of
sending, persists every message as a ``TrappedEmail`` row and emits
``mailtrap.email.trapped``. A read-only DRF API ("Письма" / Mail) lists and
inspects captured mail. It plugs into stapel-notifications' email-provider
seam **by dotted path** — no module imports another (invariant I2).

Public API (lazily exported, PEP 562 — importing this package never pulls in
Django or requires configured settings):

- ``mailtrap_settings`` — resolved app settings (``stapel_mailtrap.conf``).
- ``MailtrapEmailProvider`` — the notifications email-provider adapter
  (dotted path for ``STAPEL_NOTIFICATIONS["EMAIL_PROVIDER"]``).
- ``ScopeProvider`` / ``DefaultScopeProvider`` — the multi-tenant scope seam.
- ``trap_email`` — persist one message + emit ``mailtrap.email.trapped``.
- ``purge_expired`` — retention sweep (TTL + MAX_EMAILS cap).
"""

__all__ = [
    "DefaultScopeProvider",
    "MailtrapEmailProvider",
    "ScopeProvider",
    "mailtrap_settings",
    "purge_expired",
    "trap_email",
]

# name -> submodule that defines it. Resolution is deferred until first
# attribute access so that `import stapel_mailtrap` stays Django-free.
_LAZY_EXPORTS = {
    "mailtrap_settings": ".conf",
    "MailtrapEmailProvider": ".provider",
    "ScopeProvider": ".scope",
    "DefaultScopeProvider": ".scope",
    "trap_email": ".services",
    "purge_expired": ".services",
}


def __getattr__(name):
    if name in _LAZY_EXPORTS:
        from importlib import import_module

        value = getattr(import_module(_LAZY_EXPORTS[name], __name__), name)
        globals()[name] = value  # cache for subsequent lookups
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    return sorted(set(globals()) | set(__all__))
