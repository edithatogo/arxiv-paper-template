.PHONY: setup setup-tools pdf arxiv-readiness arxiv-variants quality lint clean

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

quality:
	python3 -m compileall -q scripts
	python3 scripts/validate_manifest.py
	$(MAKE) lint
	$(MAKE) arxiv-readiness

lint:
	@if command -v vale >/dev/null 2>&1; then vale README.md AGENTS.md; else echo "vale not installed; skipping prose lint"; fi
	python3 scripts/validate_arxiv.py paper

clean:
	python3 scripts/build_submission.py --clean
