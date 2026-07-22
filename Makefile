.PHONY: setup arxiv-readiness quality lint clean

setup:
	git submodule update --init --recursive

arxiv-readiness:
	python3 scripts/build_submission.py

quality:
	python3 -m compileall -q scripts
	python3 scripts/validate_manifest.py
	$(MAKE) lint
	$(MAKE) arxiv-readiness

lint:
	@if command -v vale >/dev/null 2>&1; then vale README.md AGENTS.md paper/main.md; else echo "vale not installed; CI installs it when configured"; fi

clean:
	python3 scripts/build_submission.py --clean
