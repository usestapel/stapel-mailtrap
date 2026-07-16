"""Extension-point tests: scope seam swap + system checks (library-standard §4)."""
import pytest


class _WorkspaceScopeProvider:
    """A host scope provider: only 'ws-1' is visible to any request here."""

    def filter(self, queryset, request):
        return queryset.filter(scope_key="ws-1")


@pytest.mark.django_db
def test_scope_provider_swap_narrows_list(api_client, settings):
    from django.contrib.auth import get_user_model

    from stapel_mailtrap.services import trap_email

    settings.STAPEL_MAILTRAP = {
        "SCOPE_PROVIDER": "stapel_mailtrap.tests.test_seams._WorkspaceScopeProvider",
    }
    trap_email(to_email="a@b.com", subject="visible", scope_key="ws-1")
    trap_email(to_email="c@d.com", subject="hidden", scope_key="ws-2")

    staff = get_user_model().objects.create(username="s", is_staff=True)
    api_client.force_authenticate(staff)
    resp = api_client.get("/mailtrap/api/v1/emails/")

    assert [i["subject"] for i in resp.data["items"]] == ["visible"]


def test_check_flags_non_scopeprovider(settings):
    from stapel_mailtrap.checks import check_scope_provider

    settings.STAPEL_MAILTRAP = {"SCOPE_PROVIDER": "django.http.HttpResponse"}
    errors = check_scope_provider(None)

    assert [e.id for e in errors] == ["stapel_mailtrap.W002"]


def test_check_flags_unimportable(settings):
    from stapel_mailtrap.checks import check_scope_provider

    settings.STAPEL_MAILTRAP = {"SCOPE_PROVIDER": "nope.NotAModule"}
    errors = check_scope_provider(None)

    assert [e.id for e in errors] == ["stapel_mailtrap.W001"]


def test_check_clean_on_default(settings):
    from stapel_mailtrap.checks import check_scope_provider

    settings.STAPEL_MAILTRAP = {}
    assert check_scope_provider(None) == []


def test_import_is_django_free():
    # `import stapel_mailtrap` must not import Django nor require settings (§3.10).
    import os
    import subprocess
    import sys

    env = {k: v for k, v in os.environ.items() if k != "DJANGO_SETTINGS_MODULE"}
    code = (
        "import sys\n"
        "import stapel_mailtrap\n"
        'polluted = [m for m in sys.modules if m == "django" or m.startswith("django.")]\n'
        'assert not polluted, f"django imported at package import time: {polluted}"\n'
        'assert "MailtrapEmailProvider" in stapel_mailtrap.__all__\n'
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        env=env,
        cwd=os.path.dirname(sys.executable),
    )
    assert result.returncode == 0, result.stderr
