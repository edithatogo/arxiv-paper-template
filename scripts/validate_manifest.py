#!/usr/bin/env python3
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
manifest = json.loads((root / "paper/readiness-manifest.json").read_text())
assert manifest["submission_performed"] is False
assert manifest["source_provenance"] == {"sourceright": "submodule", "authentext": "submodule"}
assert all(manifest["human_gates"])
print("readiness manifest: pass")
