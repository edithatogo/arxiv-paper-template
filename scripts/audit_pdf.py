#!/usr/bin/env python3
"""Audit the review PDF and LaTeX log without treating the PDF as submission input."""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


def capture(command: list[str]) -> str:
    return subprocess.run(command, check=True, capture_output=True, text=True).stdout


def main() -> None:
    pdf = Path(sys.argv[1])
    log = Path(sys.argv[2])
    subprocess.run(["qpdf", "--check", str(pdf)], check=True)
    info = capture(["pdfinfo", str(pdf)])
    fonts = capture(["pdffonts", str(pdf)])
    errors: list[str] = []
    pages = re.search(r"^Pages:\s+(\d+)$", info, re.MULTILINE)
    if not pages or int(pages.group(1)) < 1:
        errors.append("PDF has no pages")
    if not re.search(r"^Encrypted:\s+no$", info, re.MULTILINE):
        errors.append("PDF must not be encrypted")
    font_rows = [line for line in fonts.splitlines()[2:] if line.strip()]
    if not font_rows:
        errors.append("PDF contains no detectable fonts")
    for row in font_rows:
        flags = re.search(r"\s+(yes|no)\s+(yes|no)\s+(yes|no)\s+\d+\s+\d+\s*$", row)
        if not flags or flags.group(1) != "yes":
            errors.append(f"font is not embedded: {row.strip()}")
    log_text = log.read_text(errors="replace")
    forbidden = {
        "LaTeX compilation error": r"^! LaTeX Error:",
        "undefined citation": r"Citation .+ undefined",
        "undefined reference": r"Reference .+ undefined|There were undefined references",
        "overfull box": r"Overfull \\hbox",
    }
    for label, pattern in forbidden.items():
        if re.search(pattern, log_text, re.MULTILINE):
            errors.append(label)
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"PDF audit: pass ({pages.group(1)} page(s), {len(font_rows)} embedded font(s))")


if __name__ == "__main__":
    main()
