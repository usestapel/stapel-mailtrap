"""Django system checks for stapel-mailtrap configuration.

Policy (docs/library-standard.md §3.7): E-level for configuration the service
cannot run with; W-level for entries that degrade lazily. The scope provider is
W-level on purpose: a broken ``SCOPE_PROVIDER`` degrades the API (it may raise
per request), it must not block deploys — the trap keeps capturing mail either
way. IDs:

- ``stapel_mailtrap.W001`` — ``SCOPE_PROVIDER`` dotted path fails to import.
- ``stapel_mailtrap.W002`` — ``SCOPE_PROVIDER`` resolves to something that is
  not a ``ScopeProvider`` subclass.
"""
from __future__ import annotations

import inspect

from django.core import checks


@checks.register("stapel_mailtrap")
def check_scope_provider(app_configs, **kwargs):
    from .conf import mailtrap_settings
    from .scope import ScopeProvider

    try:
        provider = mailtrap_settings.SCOPE_PROVIDER
    except ImportError as exc:
        return [
            checks.Warning(
                f"STAPEL_MAILTRAP['SCOPE_PROVIDER'] cannot be imported: {exc}",
                hint=(
                    "Fix the dotted path or install the missing dependency; "
                    "the Mail API will fail to scope until it resolves."
                ),
                id="stapel_mailtrap.W001",
            )
        ]
    if not (inspect.isclass(provider) and issubclass(provider, ScopeProvider)):
        return [
            checks.Warning(
                f"STAPEL_MAILTRAP['SCOPE_PROVIDER'] resolves to {provider!r}, "
                "which is not a stapel_mailtrap.scope.ScopeProvider subclass.",
                hint="Implement the ScopeProvider seam (see MODULE.md).",
                id="stapel_mailtrap.W002",
            )
        ]
    return []


__all__ = ["check_scope_provider"]
