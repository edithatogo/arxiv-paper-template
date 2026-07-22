.PHONY: setup setup-tools pdf arxiv-readiness arxiv-variants latex-lint pdf-audit quality lint clean

setup:
	git submodule update --init --recursive

setup-tools:
	uv venv --allow-existing
	uv pip sync requirements-arxiv.txt

pdf:
	cd paper && latexmk -outdir=../build/arxiv main.tex

arxiv-readiness:
	python3 scripts/build_submission.py

arxiv-variants:
	PATH="$(CURDIR)/.venv/bin:$$PATH" .venv/bin/python scripts/prepare_variants.py

latex-lint:
	cd paper && chktex -q -v0 main.tex sections/*.tex
	cd paper && lacheck main.tex

pdf-audit: arxiv-readiness
	python3 scripts/audit_pdf.py build/arxiv/main.pdf build/arxiv/main.log

quality:
	python3 -m compileall -q scripts
	python3 scripts/validate_manifest.py
	$(MAKE) lint
	$(MAKE) arxiv-readiness
	@if command -v chktex >/dev/null 2>&1 && command -v lacheck >/dev/null 2>&1; then $(MAKE) latex-lint; else echo "LaTeX linters not installed; skipping local lint"; fi
	@if command -v qpdf >/dev/null 2>&1 && command -v pdffonts >/dev/null 2>&1; then python3 scripts/audit_pdf.py build/arxiv/main.pdf build/arxiv/main.log; else echo "PDF audit tools not installed; skipping local audit"; fi

lint:
	@if command -v vale >/dev/null 2>&1; then vale README.md AGENTS.md; else echo "vale not installed; skipping prose lint"; fi
	python3 scripts/validate_arxiv.py paper

clean:
	python3 scripts/build_submission.py --clean
