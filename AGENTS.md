# Agent instructions

This repository prepares manuscripts; it does not submit them. Agents may
build, lint, sanitize, audit citations, and produce review artifacts. They may
not select an arXiv category, certify authorship, upload a manuscript, or claim
acceptance without an explicit human gate and authoritative evidence.

Load the paper metadata, manuscript, readiness manifest, and `.agents/skills/`
before editing. Keep claims traceable to provenance and run `make quality`.

`paper/main.tex` is the canonical manuscript. Do not replace it with generated
Markdown, Quarto, notebook, or word-processor output. Keep semantic LaTeX,
standard front matter, accessible figure alt text, portable filenames, and
case-exact relative paths. Compile with errors treated as fatal.

Cleaner and collector outputs are untrusted derived artifacts. An agent must
diff them against canonical source, rebuild them, and report changes before a
human chooses an upload package.
