PYTHON ?= python3

.PHONY: contract contract-check

# docs/capabilities.json in this module is still HAND-AUTHORED for
# provides/axes/extension_points/requires (no schema/flows/errors triad
# emitter exists — see git log: "author capabilities.json for the
# stapel-catalog sweep"). `--patch` regenerates ONLY the two derivable parts:
# module/version from pyproject, and the `surface` section — the symbols a
# product is meant to CALL (discoverability-design.md §1.2), derived by AST
# from docs/capabilities.meta.json's surface_roots. A selected export with no
# curated intent line fails this target naming it.
#
# Second: emit the fifth contract artifact, docs/llms.txt (stapel_tools.llms_txt
# — the module's own context slice for an agent; badge-canon §3), from the
# capabilities.json the step above produced.
#
# Third: assemble README.md (stapel_tools.readme) from docs/readme.md — the
# human half, the only file a person edits — plus the artifacts above. The
# badge row, the version, the surface counts and every doc link are generated,
# so they cannot lag a release the way a hand-written README always has.
contract:
	$(PYTHON) -m stapel_tools.surface . --patch
	$(PYTHON) -m stapel_tools.llms_txt . --out docs
	$(PYTHON) -m stapel_tools.readme .

# Drift gate: surface --check compares the derivable parts of
# docs/capabilities.json; llms_txt's own --check mode compares a fresh render
# (from the committed docs/capabilities.json) against the committed
# docs/llms.txt.
contract-check:
	$(PYTHON) -m stapel_tools.surface . --patch --check
	$(PYTHON) -m stapel_tools.llms_txt . --check
	$(PYTHON) -m stapel_tools.readme . --check

.PHONY: migration-lint

# Expand/contract gate for Django migrations (release-management.md §3;
# stapel_tools.migration_lint). Requires stapel-tools importable (the
# workspace venv, or `pip install stapel-tools` once published).
migration-lint:
	$(PYTHON) -m stapel_tools.migration_lint . --strict
