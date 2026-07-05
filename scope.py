"""scope_key provider — the multi-tenant extension seam.

The library is scope-agnostic: ``TrappedEmail.scope_key`` is an opaque string
the host owns. A ``ScopeProvider`` (dotted path in
``STAPEL_MAILTRAP["SCOPE_PROVIDER"]``) filters the "Mail" API querysets to the
scope visible to the current request. The default is a no-op single global
scope; a multi-tenant host returns e.g. the active ``workspace_id`` /
``project_id`` and restricts the queryset to it, so one tenant never reads
another's trapped mail (which may contain OTPs and magic links).
"""
from __future__ import annotations


class ScopeProvider:
    """Contract for scope filtering. Subclass and point
    ``STAPEL_MAILTRAP["SCOPE_PROVIDER"]`` at it to scope the trap."""

    def filter(self, queryset, request):
        """Restrict ``queryset`` to the scope visible to ``request``."""
        raise NotImplementedError


class DefaultScopeProvider(ScopeProvider):
    """Single global scope: no queryset is filtered by scope. Suitable for
    single-tenant hosts and tests."""

    def filter(self, queryset, request):
        return queryset


def get_scope_provider() -> ScopeProvider:
    """Resolve the configured provider (already import_string'd by conf)."""
    from .conf import mailtrap_settings

    provider = mailtrap_settings.SCOPE_PROVIDER
    return provider() if isinstance(provider, type) else provider
