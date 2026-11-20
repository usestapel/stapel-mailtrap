"""The committed contracts are facts a generated client can lean on.

* ``docs/schema.v2.json`` is contract profile 2 (stapel_tools.codegen): the
  document a native client generator reads — bearer scheme, error codes bound
  per response (``x-stapel-errors``), ``info.x-stapel-contract == 2``.
* Every example in ``docs/schema.json`` and ``docs/schema.v2.json`` validates
  against the schema it illustrates (``stapel_tools.contract_gates``).
* No ``@action`` declares a permission, authenticator or throttle its mount
  never runs (a viewset mounted with ``as_view({...})`` ignores them).
"""
import json
from pathlib import Path

import pytest

from stapel_tools.contract_gates import dead_action_declarations, invalid_examples, viewset_routes

DOCS = Path(__file__).resolve().parent.parent / "docs"
PREFIX = "/mailtrap/api/"
#: Examples the walk must find in each document (the list item and the
#: detail) — a walk that finds fewer has lost its subject.
MIN_EXAMPLES = 2
#: The viewsets mounted here, exactly: both views are plain APIViews.
VIEWSETS: set = set()


def _doc(name):
    return json.loads((DOCS / name).read_text())


def _operations(schema):
    for path, item in schema["paths"].items():
        for method, op in item.items():
            if isinstance(op, dict):
                yield method, path, op


def test_schema_v2_is_profile_2_of_the_same_surface():
    v1, v2 = _doc("schema.json"), _doc("schema.v2.json")
    assert v2["info"]["x-stapel-contract"] == 2
    assert "x-stapel-contract" not in v1["info"]
    assert set(v2["paths"]) == set(v1["paths"])
    assert all(p.startswith(PREFIX) for p in v2["paths"])
    assert "JWTBearerAuth" in v2["components"]["securitySchemes"]


def test_schema_v2_binds_error_codes_to_operations():
    v2 = _doc("schema.v2.json")
    registry = {e["code"] for e in _doc("errors.json")}
    bound = set()
    for _m, _p, op in _operations(v2):
        for response in op.get("responses", {}).values():
            bound.update(response.get("x-stapel-errors", ()))
    assert "error.404.mailtrap_email_not_found" in bound
    assert bound <= registry, sorted(bound - registry)


def test_the_list_names_its_pagination_style():
    page = _doc("schema.v2.json")["components"]["schemas"]["PaginatedTrappedEmailListItemList"]
    assert page["x-stapel-pagination"] == {"style": "anchor", "items": "items"}


@pytest.mark.parametrize("artifact", ["schema.json", "schema.v2.json"])
def test_every_example_validates_against_its_schema(artifact):
    bad, checked = invalid_examples(_doc(artifact))
    assert checked >= MIN_EXAMPLES, f"checked {checked} examples — the walk lost the subject"
    assert bad == {}, json.dumps({" ".join(k): v for k, v in bad.items()}, indent=1)


def test_inversion_an_invalid_example_is_caught():
    schema = _doc("schema.v2.json")
    op = schema["paths"]["/mailtrap/api/v1/emails/{email_id}/"]["get"]
    media = op["responses"]["200"]["content"]["application/json"]
    media["examples"] = {"Broken": {"value": "not an object"}}
    bad, _ = invalid_examples(schema)
    assert ("get", "/mailtrap/api/v1/emails/{email_id}/", "200", "Broken") in bad


def test_no_action_declares_what_its_mount_ignores():
    seen = {cls.__name__ for _r, _c, cls, _a in viewset_routes()}
    assert seen == VIEWSETS, f"roster saw {sorted(seen)}"
    assert dead_action_declarations() == []
