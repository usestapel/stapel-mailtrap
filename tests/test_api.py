"""The "Mail" API: list (pagination + scope filter), detail, permissions."""
import pytest

from stapel_mailtrap.services import trap_email


@pytest.fixture
def staff(db):
    from django.contrib.auth import get_user_model

    return get_user_model().objects.create(
        username="staff", email="s@example.com", is_staff=True
    )


@pytest.mark.django_db
def test_list_requires_staff(api_client):
    resp = api_client.get("/mailtrap/api/v1/emails/")
    assert resp.status_code in (401, 403)


@pytest.mark.django_db
def test_list_returns_trapped_emails(api_client, staff):
    trap_email(to_email="a@b.com", subject="one")
    trap_email(to_email="c@d.com", subject="two")

    api_client.force_authenticate(staff)
    resp = api_client.get("/mailtrap/api/v1/emails/")

    assert resp.status_code == 200
    subjects = {i["subject"] for i in resp.data["items"]}
    assert subjects == {"one", "two"}


@pytest.mark.django_db
def test_list_filters_by_scope_key(api_client, staff):
    trap_email(to_email="a@b.com", subject="ws1", scope_key="ws-1")
    trap_email(to_email="c@d.com", subject="ws2", scope_key="ws-2")

    api_client.force_authenticate(staff)
    resp = api_client.get("/mailtrap/api/v1/emails/", {"scope_key": "ws-1"})

    assert resp.status_code == 200
    assert [i["subject"] for i in resp.data["items"]] == ["ws1"]


@pytest.mark.django_db
def test_detail_returns_bodies(api_client, staff):
    email = trap_email(
        to_email="a@b.com",
        subject="hi",
        body_html="<p>hello</p>",
        body_text="hello",
        attachments=[{"filename": "x.pdf", "content_type": "application/pdf", "size": 3}],
    )

    api_client.force_authenticate(staff)
    resp = api_client.get(f"/mailtrap/api/v1/emails/{email.id}/")

    assert resp.status_code == 200
    assert resp.data["body_html"] == "<p>hello</p>"
    assert resp.data["body_text"] == "hello"
    assert resp.data["attachments"][0]["filename"] == "x.pdf"


@pytest.mark.django_db
def test_detail_404(api_client, staff):
    import uuid

    api_client.force_authenticate(staff)
    resp = api_client.get(f"/mailtrap/api/v1/emails/{uuid.uuid4()}/")

    assert resp.status_code == 404
    assert resp.data["localizable_error"] == "error.404.mailtrap_email_not_found"
