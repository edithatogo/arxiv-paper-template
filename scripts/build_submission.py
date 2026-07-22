#!/usr/bin/env python3
"""Build a non-submitting arXiv source package."""
from __future__ import annotations

import hashlib
import gzip
import json
import shutil
import subprocess
import sys
import tarfile
import os
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
    os.environ.setdefault("SOURCE_DATE_EPOCH", "0")
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
    with archive.open("wb") as raw:
        with gzip.GzipFile(fileobj=raw, mode="wb", compresslevel=9, mtime=int(os.environ["SOURCE_DATE_EPOCH"])) as compressed:
            with tarfile.open(fileobj=compressed, mode="w") as tar:
                for path in sorted(PACKAGE.iterdir()):
                    info = tar.gettarinfo(path, arcname=path.name)
                    info.mtime = int(os.environ["SOURCE_DATE_EPOCH"])
                    if path.is_file():
                        with path.open("rb") as source:
                            tar.addfile(info, source)
                    else:
                        tar.addfile(info)
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    (BUILD / "arxiv-source.tar.gz.sha256").write_text(f"{digest}  {archive.name}\n")
    report = {"schema_version": "arxiv-paper-template.readiness.v1", "status": "ready_for_human_review", "archive": str(archive.relative_to(ROOT)), "sha256": digest, "submission_performed": False, "human_gates": json.loads((ROOT / "paper/readiness-manifest.json").read_text())["human_gates"]}
    (BUILD / "readiness.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
