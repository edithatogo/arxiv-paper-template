# Bleeding-edge arXiv LaTeX template

A reproducible, source-audited template for preparing research manuscripts for
arXiv and later journal submission. The default path is plain Markdown to
Pandoc to LaTeX to PDFLaTeX; Quarto is deliberately not required.

Included are pinned SourceRight and Authentext submodules, academic agent
skills, citation/provenance checks, LaTeX/PDF/source hygiene, optional arXiv
cleaning and collection stages, readiness manifests, and non-submitting CI.

```console
git clone --recurse-submodules https://github.com/edithatogo/arxiv-paper-template.git
make setup
make arxiv-readiness
```
