"""The JSON bodies the committed schema declares are the bodies the views send.

An ``@extend_schema`` annotation is a claim the generator cannot check. This
gate performs each JSON operation of ``docs/schema.v2.json`` and validates the
body against the schema it promised. A JSON operation with no recipe below
fails rather than being skipped.
"""
import copy
import json
from pathlib import Path

import jsonschema
import pytest

from stapel_mailtrap.services import trap_email

pytestmark = pytest.mark.django_db

SCHEMA = json.loads(
    (Path(__file__).resolve().parent.parent / "docs" / "schema.v2.json").read_text()
)
V1 = "/mailtrap/api/v1"


@pytest.fixture
def staff_client(api_client):
    from django.contrib.auth import get_user_model

    staff = get_user_model().objects.create(
        username="staff", email="s@example.com", is_staff=True
    )
    api_client.force_authenticate(staff)
    return api_client


def _trapped():
    return trap_email(
        to_email="user@example.com",
        from_email="noreply@example.com",
        subject="Your sign-in code",
        body_html="<p>123456</p>",
        body_text="123456",
        attachments=[{"filename": "x.pdf", "content_type": "application/pdf", "size": 3}],
        headers={"Reply-To": "support@example.com"},
        scope_key="acme",
    )


#: ``(METHOD, path) -> recipe(staff_client) -> response``.
RECIPES = {
    ("GET", f"{V1}/emails/"): lambda staff: (_trapped(), staff.get(f"{V1}/emails/"))[1],
    ("GET", f"{V1}/emails/{{email_id}}/"): lambda staff: staff.get(
        f"{V1}/emails/{_trapped().id}/"
    ),
}


def _json_schema(node):
    if isinstance(node, list):
        return [_json_schema(item) for item in node]
    if not isinstance(node, dict):
        return node
    rebuilt = {k: _json_schema(v) for k, v in node.items() if k != "nullable"}
    if node.get("nullable"):
        return {"anyOf": [rebuilt, {"type": "null"}]}
    return rebuilt


def _operations():
    for path, item in SCHEMA["paths"].items():
        for method, op in item.items():
            if not isinstance(op, dict):
                continue
            for code, response in op.get("responses", {}).items():
                body = response.get("content", {}).get("application/json", {}).get("schema")
                if code.startswith("2") and body is not None:
                    yield method.upper(), path, int(code), body


OPERATIONS = list(_operations())


def test_the_gate_sees_its_subject():
    assert {(m, p) for m, p, _c, _b in OPERATIONS} == set(RECIPES)


@pytest.mark.parametrize(
    "method,path,code,body_schema", OPERATIONS, ids=[f"{m} {p}" for m, p, _c, _b in OPERATIONS]
)
def test_the_wire_matches_the_declared_response(staff_client, method, path, code, body_schema):
    response = RECIPES[(method, path)](staff_client)
    assert response.status_code == code, response.content
    root = copy.deepcopy(body_schema)
    root["components"] = copy.deepcopy(SCHEMA["components"])
    validator = jsonschema.Draft202012Validator(_json_schema(root))
    body = response.json()
    errors = sorted(validator.iter_errors(body), key=lambda e: list(e.path))
    assert not errors, "\n".join(f"at {list(e.path)}: {e.message}" for e in errors[:10])
    if isinstance(body, dict) and "items" in body:
        assert body["items"], f"{method} {path}: an empty page validates against any item schema"


def test_inversion_a_wrong_declaration_is_caught(staff_client):
    """Declaring the list as one detail object must fail against the wire."""
    root = {"$ref": "#/components/schemas/TrappedEmailDetail"}
    root["components"] = copy.deepcopy(SCHEMA["components"])
    validator = jsonschema.Draft202012Validator(_json_schema(root))
    body = RECIPES[("GET", f"{V1}/emails/")](staff_client).json()
    assert list(validator.iter_errors(body))
