PYTHON ?= python3

.PHONY: contract contract-check

# First: the HTTP contract triad (_codegen.py) — docs/schema.json (profile 1,
# what stapel-react reads), docs/schema.v2.json (contract profile 2, what a
# native client generator reads), docs/flows.json and docs/errors.json, from a
# single-module {mailtrap + core} instance at the canonical /mailtrap/ mount.
#
# docs/capabilities.json stays HAND-AUTHORED for provides/axes/
# extension_points/requires. `--patch` regenerates ONLY the two derivable
# parts: module/version from pyproject, and the `surface` section — the symbols
# a product is meant to CALL (discoverability-design.md §1.2), derived by AST
# from docs/capabilities.meta.json's surface_roots.
#
# Then docs/llms.txt (stapel_tools.llms_txt — the module's own context slice
# for an agent; badge-canon §3), rendered from capabilities.json and the triad,
# and README.md (stapel_tools.readme) from docs/readme.md plus the artifacts.
contract:
	$(PYTHON) -m stapel_mailtrap._codegen --out docs
	$(PYTHON) -m stapel_tools.surface . --patch
	$(PYTHON) -m stapel_tools.llms_txt . --out docs
	$(PYTHON) -m stapel_tools.readme .

# Drift gate: the triad is re-emitted into a temp dir and compared in Python
# (`_codegen --check`); surface --check compares the derivable parts of
# docs/capabilities.json; llms_txt and readme compare a fresh render against
# the committed files.
contract-check:
	$(PYTHON) -m stapel_mailtrap._codegen --out docs --check
	$(PYTHON) -m stapel_tools.surface . --patch --check
	$(PYTHON) -m stapel_tools.llms_txt . --check
	$(PYTHON) -m stapel_tools.readme . --check

.PHONY: migration-lint

# Expand/contract gate for Django migrations (release-management.md §3;
# stapel_tools.migration_lint). Requires stapel-tools importable (the
# workspace venv, or `pip install stapel-tools` once published).
migration-lint:
	$(PYTHON) -m stapel_tools.migration_lint . --strict
