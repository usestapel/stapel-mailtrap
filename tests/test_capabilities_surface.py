"""Drift gate for the `surface` section of ``docs/capabilities.json``.

``axes`` describes what a host may switch on and ``extension_points`` what it
may replace; neither says "is there already a mechanism for X, and what do I
call?" — the question a host asks when it wants to plug outbound mail into
the trap from its OWN backend, or reuse the same tenant scoping the built-in
Mail API applies. ``surface`` names those entry points — ``trap_email``,
``purge_expired``, ``get_scope_provider`` — so a duplicate capture table, a
hand-written retention query, or an unscoped custom view over ``TrappedEmail``
shows up as "reinvented something that already exists" rather than as three
independent oversights.

The entry set is derived by AST from the roots in
``docs/capabilities.meta.json`` — a new public function in ``services.py`` or
``scope.py`` shows up here by itself and fails emission until somebody
explains it.

Deliberately NOT in this section: ``MailtrapEmailProvider`` (provider.py).
Anything already wired through stapel-notifications' ``EMAIL_PROVIDER`` seam
reaches this module through that class, and the seam is already named as an
extension_point in capabilities.json — restating the class here would be the
same prose twice.
"""
import json
from pathlib import Path

import pytest

try:
    import stapel_tools  # noqa: F401  (probe: the emitter must be importable)
except ImportError as exc:  # pragma: no cover - environment failure, not a branch
    # NOT pytest.importorskip. A drift gate that skips when its emitter is
    # missing reports `1 skipped`, exits 0, and disappears among a hundred
    # green tests — exactly how an entry point could go unadopted with
    # nothing red anywhere to say so. A gate that cannot run has FAILED; it
    # has not passed.
    raise RuntimeError(
        "capabilities surface drift gate cannot run: stapel-tools is not "
        "importable, and it carries the capabilities emitter this gate "
        "measures drift against. Install it (workspace venv, or `pip install "
        "stapel-tools`) and re-run. This is a hard failure on purpose — a "
        "skipped drift gate is silently no gate."
    ) from exc

from stapel_tools.surface import _stable_json, load_meta, patch_capabilities  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
COMMITTED = REPO / "docs" / "capabilities.json"

ENTRY_POINTS = {"trap_email", "purge_expired", "get_scope_provider"}


def _emitted() -> dict:
    try:
        return patch_capabilities(REPO, load_meta(REPO))
    except SystemExit as exc:  # the LOUD rule — report it, don't bury it
        pytest.fail(f"capabilities emission refused: {exc}", pytrace=False)


def test_no_drift():
    assert COMMITTED.read_text() == _stable_json(_emitted()), (
        "docs/capabilities.json is stale — run `make contract` and commit it"
    )


def test_version_tracks_pyproject():
    """The document carries the module version, derived (not hand-copied) so
    it cannot rot the way the rest of the hand-authored file can."""
    import tomllib

    pyproject = tomllib.loads((REPO / "pyproject.toml").read_text())
    assert json.loads(COMMITTED.read_text())["version"] == (
        pyproject["project"]["version"]
    )


def test_every_entry_point_is_named_and_explained():
    surface = json.loads(COMMITTED.read_text())["surface"]
    by_name = {e["name"]: e for e in surface}
    assert ENTRY_POINTS <= set(by_name)
    for name in ENTRY_POINTS:
        entry = by_name[name]
        assert entry["intent"].strip(), entry


def test_a_new_public_function_cannot_slip_in_unexplained():
    """The set is derived, so the gate is not "did somebody remember to list
    it" but "does every public function in the declared roots have a line"."""
    from stapel_tools.surface import scan_functions

    declared = {e["name"] for e in json.loads(COMMITTED.read_text())["surface"]}
    for module in ("services.py", "scope.py"):
        assert set(scan_functions(REPO / module)) <= declared
