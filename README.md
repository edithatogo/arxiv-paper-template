# arXiv LaTeX template

A reproducible, source-audited template for authoring and preparing scholarly
papers for arXiv. `paper/main.tex` is the canonical source. The default build is
LaTeX to PDFLaTeX and creates the source archive arXiv expects; neither Pandoc
nor Quarto is part of the manuscript path.

The structure follows arXiv's official
[submission guidance](https://info.arxiv.org/help/submit/index.html) and
[LaTeX/HTML best practices](https://info.arxiv.org/help/submit_latex_best_practices.html):
standard front matter, semantic sectioning, portable filenames, accessible
figures, case-sensitive local references, and a top-level file containing
`\documentclass`.

## Start a paper

```console
git clone --recurse-submodules https://github.com/edithatogo/arxiv-paper-template.git
cd arxiv-paper-template
make setup
make quality
```

Edit `paper/main.tex`, the files in `paper/sections/`, `paper/references.bib`,
and `paper/metadata.json`. Add figures beneath `paper/figures/` with portable,
case-exact filenames and meaningful `alt={...}` text on `\includegraphics`.

The canonical outputs are:

- `build/arxiv/main.pdf`, for review only;
- `build/arxiv/arxiv-source.tar.gz`, the source package;
- `build/arxiv/arxiv-source.tar.gz.sha256`, its checksum; and
- `build/arxiv/readiness.json`, the non-submission evidence record; and
- `build/arxiv/readability.json`, review-only Textstat evidence from the
  canonical PDF.

## Independent preparation tools

Pinned optional tooling is isolated in `requirements-arxiv.txt`:

```console
make setup-tools
.venv-arxiv/bin/python scripts/prepare_variants.py
```

This prepares independent outputs from
[arxiv-latex-cleaner](https://github.com/google-research/arxiv-latex-cleaner)
and [arxiv-collector](https://github.com/djsutherland/arxiv-collector). Review
their diffs and compile their results before selecting an upload package:
comment removal, flattening, image rewriting, and dependency collection can
change semantics. The canonical readiness artifact retains the exact cleaner
input/output diff and the validated variant trees for review. [arXivIt](https://github.com/jaateixeira/arXivIt) informs the
built-in filename, figure, `.bbl`, hidden-file, and source checks but is not
vendored: it is a small GPL tool without a packaged release. The
[awesome-arxiv](https://github.com/artnitolog/awesome-arxiv) list is a useful
discovery catalogue, not a build dependency.

## Guardrails

CI compiles the canonical LaTeX, validates the package, rebuilds it to prove
byte-for-byte reproducibility, runs ChkTeX and Lacheck, audits PDF integrity and
font embedding, and independently converts the source to semantic HTML with
LaTeXML. A pinned matrix compiles against both TeX Live 2023 and 2025, the two
versions currently supported by arXiv. CI also scans workflows with Zizmor,
checks links, and uploads review
artifacts. SourceRight and Authentext are pinned submodules for
source-rights and claim/evidence work. Automation never chooses authorship,
license, category, endorsement, or performs the authenticated arXiv upload.

The Python preparation contracts have a dependency-free regression suite:

```console
make test
```

It exercises non-submission invariants, manifest validation, portable-path
rejection, transformed-tree hygiene, and deterministic archive metadata.

## Readability evidence

After `make setup-tools`, generate the canonical PDF and a deterministic
Textstat report with:

```console
make readability
```

The workflow extracts plain text from the review PDF with `pdftotext`, then
records counts, estimated reading time, Flesch, Flesch--Kincaid, Fog,
Coleman--Liau, ARI, Dale--Chall, Linsear Write, and consensus grade metrics.
SMOG is omitted with an explicit warning when the manuscript has fewer than
the 30 sentences required by its documented validation assumptions. These values
are editorial signals, not universal scientific-quality thresholds.
