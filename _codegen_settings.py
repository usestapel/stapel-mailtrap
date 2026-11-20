"""Single-module Django settings for stapel-mailtrap.

One ``settings.configure(...)`` block serves the test suite and the contract
emission harness (``_codegen.py``), so the two cannot drift apart.
"""
from __future__ import annotations


def settings_kwargs(*, root_urlconf: str = "stapel_mailtrap.tests.urls") -> dict:
    """The ``settings.configure(**kwargs)`` for a single-module instance."""
    # The fleet error envelope for refusals no view code raises (401/403/404/
    # 405); read off core's preset, which reads no settings at import.
    from stapel_core.testing import BASE_REST_FRAMEWORK

    return dict(
        SECRET_KEY="test-secret-key-not-for-production-0123456789abcdef",
        INSTALLED_APPS=[
            "django.contrib.contenttypes",
            "django.contrib.auth",
            "django.contrib.sessions",
            "django.contrib.admin",
            "django.contrib.messages",
            # Core's management commands (generate_flow_docs,
            # generate_error_keys) that the contract emission calls.
            "stapel_core.django.apps.CommonDjangoConfig",
            "stapel_core.django.users",
            "rest_framework",
            "drf_spectacular",
            "stapel_mailtrap",
        ],
        AUTH_USER_MODEL="users.User",
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            }
        },
        DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
        DEFAULT_FROM_EMAIL="noreply@example.com",
        USE_TZ=True,
        ROOT_URLCONF=root_urlconf,
        CACHES={
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            }
        },
        # Synchronous in-process comm with schema validation ON, so the
        # committed contract in schemas/emits/ is enforced by the tests.
        STAPEL_BUS_BACKEND="stapel_core.bus.backends.memory.MemoryBus",
        STAPEL_COMM={
            "OUTBOX_ENABLED": False,
            "ACTION_TRANSPORT": "inprocess",
            "VALIDATE_SCHEMAS": True,
        },
        MIGRATION_MODULES={
            "users": None,
        },
        REST_FRAMEWORK={
            "EXCEPTION_HANDLER": BASE_REST_FRAMEWORK["EXCEPTION_HANDLER"],
        },
    )
