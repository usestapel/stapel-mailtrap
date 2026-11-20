def pytest_configure(config):
    from django.conf import settings

    if not settings.configured:
        from stapel_mailtrap._codegen_settings import settings_kwargs

        settings.configure(**settings_kwargs())
        import django

        django.setup()

        from stapel_core.comm.schemas import autoload_schemas

        autoload_schemas()


import pytest  # noqa: E402


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient

    return APIClient()
