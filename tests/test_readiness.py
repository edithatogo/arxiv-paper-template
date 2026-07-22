"""Regression tests for reusable manuscript-readiness contracts."""

from __future__ import annotations

import gzip
import importlib.util
import io
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]


def load_script(name: str):
    """Load a repository script as a testable module."""
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ReadinessContractTests(unittest.TestCase):
    def test_pipeline_is_latex_first_non_submitting_and_hermetic(self) -> None:
        workflow = (ROOT / ".github/workflows/readiness.yml").read_text()
        makefile = (ROOT / "Makefile").read_text()
        manifest = (ROOT / "paper/readiness-manifest.json").read_text()
        builder = (ROOT / "scripts/build_submission.py").read_text()
        readability = (ROOT / "scripts/audit_readability.py").read_text()
        requirements = (ROOT / "requirements-arxiv.txt").read_text()
        main_tex = (ROOT / "paper/main.tex").read_text()

        self.assertIn("\\documentclass", main_tex)
        self.assertIn('"canonical_source": "paper/main.tex"', manifest)
        self.assertIn('"submission_performed": false', manifest)
        self.assertIn("permissions: {}", workflow)
        self.assertIn("texlive: [2023, 2025]", workflow)
        self.assertIn('version: "0.11.29"', workflow)
        self.assertIn(".venv-arxiv", makefile)
        self.assertIn("make setup-tools", workflow)
        self.assertIn("build/variants/", workflow)
        self.assertIn("make readability", workflow)
        self.assertIn("audit_readability.py", makefile)
        self.assertIn("textstat==0.7.13", requirements)
        self.assertIn("nltk==3.10.0", requirements)
        self.assertIn("pyphen==0.17.2", requirements)
        self.assertIn("defusedxml==0.7.1", requirements)
        self.assertIn('"status": "review_only"', readability)
        self.assertIn("fewer than 30 sentences", readability)
        self.assertIn("nltk.data.find", readability)
        self.assertNotIn("nltk.download", readability)
        self.assertIn("nltk.downloader", makefile)
        self.assertIn("submission_performed", builder)
        self.assertNotIn("pandoc", builder)
        self.assertNotIn("arxiv.org", builder)

    def test_readability_normalization_joins_line_break_hyphenation(self) -> None:
        readability = load_script("audit_readability")
        normalized = readability.normalize_text(
            "A reproducible inter-\nnational manuscript.\n\nSecond sentence."
        )
        self.assertEqual(
            normalized,
            "A reproducible international manuscript. Second sentence.",
        )

    def test_manifest_validation_cannot_be_optimized_away(self) -> None:
        validator = load_script("validate_manifest")
        errors = validator.validate(
            {"submission_performed": True},
            {"authors": [], "categories": []},
        )
        self.assertIn("submission_performed must be false", errors)
        self.assertTrue(any("missing keys" in error for error in errors))

    def test_source_validator_rejects_external_volume_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "main.tex").write_text(
                "\\documentclass{article}\n\\input{/Volumes/private/notes.tex}\n"
            )
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts/validate_arxiv.py"), str(root)],
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("local absolute path", result.stderr)

    def test_variant_copy_excludes_generated_and_legacy_state(self) -> None:
        variants = load_script("prepare_variants")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "paper"
            destination = root / "copy"
            source.mkdir()
            (source / "main.tex").write_text("canonical")
            (source / "draft.qmd").write_text("legacy")
            (source / "paper.tex").write_text("generated")
            (source / ".quarto").mkdir()
            (source / ".quarto" / "state").write_text("cache")
            (source / "__pycache__").mkdir()
            (source / "__pycache__" / "state.pyc").write_bytes(b"cache")
            with mock.patch.object(variants, "PAPER", source):
                variants.copy_manuscript_tree(destination)

            self.assertTrue((destination / "main.tex").is_file())
            self.assertFalse((destination / "draft.qmd").exists())
            self.assertFalse((destination / "paper.tex").exists())
            self.assertFalse((destination / ".quarto").exists())
            self.assertFalse((destination / "__pycache__").exists())

    def test_variant_diff_is_stable_and_does_not_disclose_paths(self) -> None:
        variants = load_script("prepare_variants")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            canonical = root / "canonical-input"
            cleaner = root / "cleaner-output"
            canonical.mkdir()
            cleaner.mkdir()
            (canonical / "main.tex").write_text("before\n")
            (cleaner / "main.tex").write_text("after\n")
            comparison = variants.compare_trees(canonical, cleaner)

        self.assertIn("--- canonical", comparison)
        self.assertIn("+++ cleaner", comparison)
        self.assertNotIn(str(root), comparison)
        self.assertNotRegex(comparison, r"\d{4}-\d{2}-\d{2}")

    def test_archive_is_byte_identical_and_metadata_normalized(self) -> None:
        builder = load_script("build_submission")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            build = root / "build"
            package = build / "package"
            (package / "sections").mkdir(parents=True)
            (package / "main.tex").write_text("canonical\n")
            (package / "sections" / "body.tex").write_text("body\n")
            (package / "main.tex").chmod(0o600)
            with (
                mock.patch.object(builder, "BUILD", build),
                mock.patch.object(builder, "PACKAGE", package),
            ):
                first, first_digest = builder.deterministic_archive(42)
                first_bytes = first.read_bytes()
                second, second_digest = builder.deterministic_archive(42)
                second_bytes = second.read_bytes()

            self.assertEqual(first_digest, second_digest)
            self.assertEqual(first_bytes, second_bytes)
            with gzip.GzipFile(fileobj=io.BytesIO(second_bytes)) as compressed:
                with tarfile.open(fileobj=compressed, mode="r:") as archive:
                    members = archive.getmembers()
            self.assertTrue(members)
            for member in members:
                self.assertEqual(member.mtime, 42)
                self.assertEqual(member.uid, 0)
                self.assertEqual(member.gid, 0)
                self.assertEqual(member.uname, "")
                self.assertEqual(member.gname, "")
                self.assertEqual(member.mode, 0o755 if member.isdir() else 0o644)


if __name__ == "__main__":
    unittest.main()
