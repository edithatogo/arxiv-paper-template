.PHONY: setup arxiv-readiness quality clean

setup:
	git submodule update --init --recursive

arxiv-readiness:
	python3 scripts/build_submission.py

quality:
	python3 -m compileall -q scripts
	python3 scripts/validate_manifest.py
	$(MAKE) arxiv-readiness

clean:
	python3 scripts/build_submission.py --clean
