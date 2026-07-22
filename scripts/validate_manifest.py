#!/usr/bin/env python3
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
manifest = json.loads((root / "paper/readiness-manifest.json").read_text())
assert manifest["submission_performed"] is False
assert manifest["source_provenance"] == {"sourceright": "submodule", "authentext": "submodule"}
assert all(manifest["human_gates"])
assert manifest["schema_version"].startswith("arxiv-paper-template.readiness.")
assert {"required_tools", "optional_tools", "source_provenance", "human_gates"} <= manifest.keys()
print("readiness manifest: pass")
