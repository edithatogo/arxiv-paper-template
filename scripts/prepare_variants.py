#!/usr/bin/env python3
"""Prepare optional cleaner/collector variants for explicit human comparison."""
from __future__ import annotations

import shutil
import subprocess
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper"
VARIANTS = ROOT / "build" / "variants"


def run(command: list[str], cwd: Path) -> None:
    subprocess.run(command, cwd=cwd, check=True)


def rebuild_and_validate(source: Path, build: Path) -> None:
    shutil.rmtree(build, ignore_errors=True)
    build.mkdir(parents=True)
    command = ["latexmk"]
    if not (source / "latexmkrc").exists():
        command.extend(["-r", str(PAPER / "latexmkrc")])
    command.extend([f"-outdir={build}", "main.tex"])
    run(command, source)
    run(
        [
            str(ROOT / ".venv" / "bin" / "python"),
            str(ROOT / "scripts" / "audit_pdf.py"),
            str(build / "main.pdf"),
            str(build / "main.log"),
        ],
        ROOT,
    )
    run([str(ROOT / ".venv" / "bin" / "python"), str(ROOT / "scripts" / "validate_arxiv.py"), str(source)], ROOT)


def main() -> None:
    VARIANTS.mkdir(parents=True, exist_ok=True)
    missing: list[str] = []
    cleaner = shutil.which("arxiv_latex_cleaner")
    if cleaner:
        cleaner_input = VARIANTS / "cleaner-input"
        shutil.rmtree(cleaner_input, ignore_errors=True)
        shutil.copytree(PAPER, cleaner_input)
        run([cleaner, str(cleaner_input), "--config", str(PAPER / "cleaner_config.yaml"), "--keep_bib"], ROOT)
        cleaner_output = Path(str(cleaner_input) + "_arXiv")
        rebuild_and_validate(cleaner_output, VARIANTS / "cleaner-build")
        comparison = subprocess.run(
            ["diff", "-ru", "--exclude=metadata.json", "--exclude=readiness-manifest.json", "--exclude=cleaner_config.yaml", str(PAPER), str(cleaner_output)],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        (VARIANTS / "cleaner.diff").write_text(comparison.stdout)
    else:
        missing.append("arxiv_latex_cleaner")
    collector = shutil.which("arxiv-collector")
    if collector:
        collector_input = VARIANTS / "collector-input"
        shutil.rmtree(collector_input, ignore_errors=True)
        shutil.copytree(PAPER, collector_input)
        run([collector, "main.tex"], collector_input)
        collector_output = VARIANTS / "collector-output"
        shutil.rmtree(collector_output, ignore_errors=True)
        collector_output.mkdir()
        with tarfile.open(collector_input / "arxiv.tar.gz", "r:gz") as archive:
            archive.extractall(collector_output, filter="data")
        rebuild_and_validate(collector_output, VARIANTS / "collector-build")
    else:
        missing.append("arxiv-collector")
    if missing:
        raise SystemExit("missing optional tools; run make setup-tools: " + ", ".join(missing))
    print(f"variants prepared under {VARIANTS}")


if __name__ == "__main__":
    main()
