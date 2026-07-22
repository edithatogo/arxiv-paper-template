#!/usr/bin/env python3
"""Validate manuscript metadata and non-submission gates."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_MANIFEST_KEYS = {
    "schema_version",
    "canonical_source",
    "required_tools",
    "optional_tools",
    "source_provenance",
    "human_gates",
    "submission_performed",
}
REQUIRED_METADATA_KEYS = {
    "title",
    "authors",
    "abstract",
    "categories",
    "license",
    "comments",
}


def validate(manifest: Any, metadata: Any) -> list[str]:
    """Return actionable errors without relying on optimizable assertions."""
    errors: list[str] = []
    if not isinstance(manifest, dict):
        return ["readiness manifest must be a JSON object"]
    if not isinstance(metadata, dict):
        return ["metadata must be a JSON object"]

    missing_manifest = sorted(REQUIRED_MANIFEST_KEYS - manifest.keys())
    missing_metadata = sorted(REQUIRED_METADATA_KEYS - metadata.keys())
    if missing_manifest:
        errors.append(f"readiness manifest missing keys: {', '.join(missing_manifest)}")
    if missing_metadata:
        errors.append(f"metadata missing keys: {', '.join(missing_metadata)}")

    if manifest.get("submission_performed") is not False:
        errors.append("submission_performed must be false")
    if not str(manifest.get("schema_version", "")).startswith(
        "arxiv-paper-template.readiness."
    ):
        errors.append("unexpected readiness schema_version")
    if manifest.get("canonical_source") != "paper/main.tex":
        errors.append("canonical_source must be paper/main.tex")
    expected_provenance = {
        "sourceright": "submodule",
        "authentext": "submodule",
    }
    if manifest.get("source_provenance") != expected_provenance:
        errors.append("SourceRight and Authentext must remain pinned submodules")
    human_gates = manifest.get("human_gates")
    if (
        not isinstance(human_gates, list)
        or not human_gates
        or not all(isinstance(gate, str) and gate.strip() for gate in human_gates)
    ):
        errors.append("human_gates must be a non-empty list of descriptions")
    authors = metadata.get("authors")
    if not isinstance(authors, list) or not authors:
        errors.append("metadata authors must be a non-empty list")
    categories = metadata.get("categories")
    if not isinstance(categories, list) or not categories:
        errors.append("metadata categories must be a non-empty list")
    return errors


def main() -> None:
    """Load and validate the repository readiness records."""
    manifest = json.loads((ROOT / "paper/readiness-manifest.json").read_text())
    metadata = json.loads((ROOT / "paper/metadata.json").read_text())
    errors = validate(manifest, metadata)
    if errors:
        raise SystemExit("\n".join(errors))
    print("readiness manifest: pass")


if __name__ == "__main__":
    main()
