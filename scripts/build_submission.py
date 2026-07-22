#!/usr/bin/env python3
"""Build a non-submitting arXiv source package."""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "build" / "arxiv"
PACKAGE = BUILD / "package"


def run(command: list[str]) -> None:
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> None:
    if "--clean" in sys.argv:
        shutil.rmtree(BUILD, ignore_errors=True)
        return
    BUILD.mkdir(parents=True, exist_ok=True)
    shutil.rmtree(PACKAGE, ignore_errors=True)
    PACKAGE.mkdir()
    for tool in ("pandoc", "pdflatex", "latexmk"):
        if shutil.which(tool) is None:
            raise SystemExit(f"missing required tool: {tool}")
    tex = BUILD / "main.tex"
    pdf = BUILD / "main.pdf"
    run(["pandoc", "paper/main.md", "--from", "markdown", "--to", "latex", "--standalone", "--citeproc", "--bibliography=paper/references.bib", "--output", str(tex)])
    run(["latexmk", "-r", "paper/latexmkrc", "-outdir=" + str(BUILD), str(tex)])
    shutil.copy2(tex, PACKAGE / "main.tex")
    shutil.copy2(pdf, PACKAGE / "main.pdf")
    shutil.copy2(ROOT / "paper/references.bib", PACKAGE / "references.bib")
    shutil.copy2(ROOT / "paper/readiness-manifest.json", PACKAGE / "readiness-manifest.json")
    archive = BUILD / "arxiv-source.tar.gz"
    archive.unlink(missing_ok=True)
    with tarfile.open(archive, "w:gz") as tar:
        for path in sorted(PACKAGE.iterdir()):
            tar.add(path, arcname=path.name)
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    report = {"schema_version": "arxiv-paper-template.readiness.v1", "status": "ready_for_human_review", "archive": str(archive.relative_to(ROOT)), "sha256": digest, "submission_performed": False, "human_gates": json.loads((ROOT / "paper/readiness-manifest.json").read_text())["human_gates"]}
    (BUILD / "readiness.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
