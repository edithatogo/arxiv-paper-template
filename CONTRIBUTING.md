# Contributing to arxiv-paper-template

This repository provides a reproducible LaTeX paper template and source-package preparation tools for arXiv. Contributions can improve template portability, accessibility, build reproducibility, validation and documentation.

## Before you start

Read [README.md](README.md), [AGENTS.md](AGENTS.md) and the relevant paper metadata and readiness rules. Check existing issues and pull requests before substantial changes. `paper/main.tex` is canonical; preserve semantic LaTeX, standard front matter, meaningful figure descriptions and case-exact portable paths.

For bugs, provide the affected version or commit, environment, minimal reproduction, expected result and observed result. For a substantial proposal, describe the use case and compatibility impact before expanding implementation scope. Use existing issue templates when offered.

## Development and validation

Follow the documented recursive-submodule setup and use the repository's existing targets:

```sh
make setup
make quality
```

[The readiness workflow](.github/workflows/readiness.yml) specifies the build matrix and verification tooling. Inspect the rendered PDF and the generated source package when a change affects formatting or packaging. Preserve the source archive, checksum and readiness record as separate outputs. Confirm changed references, figures and included files resolve in the packaged source.

If cleaner or collector tools are involved, follow the README's optional setup, compare their output with canonical source and compile the result. Generated derivatives can change semantics and are not automatically acceptable upload packages. Add focused validation cases for changed preparation scripts and update affected examples.

Template work prepares review artifacts. Authorship, category selection, endorsement, licence selection and authenticated submission retain their existing decision boundaries.

## Pull requests

Create a focused branch from the current `main` branch and submit a pull request to this repository. Link the relevant issue or existing project task, explain the resulting behaviour, and update affected examples and documentation. Keep unrelated changes in separate pull requests.

Report executed commands, outcomes and the commit they validate. Identify unavailable checks and remaining limitations explicitly. Follow the repository's existing review and automated-check requirements; retain required gates and current ownership. Address findings and verify the final head before integration. Repository changes do not themselves authorise a release or external operational action.

## Security, rights and conduct

Follow the [security policy](https://github.com/edithatogo/.github/blob/main/SECURITY.md). Use private vulnerability reporting if available; otherwise request a private contact without publishing vulnerability details. Keep credentials, personal information and restricted source material out of issues, fixtures, logs and artifacts.

Preserve existing attribution and third-party terms. This guide does not grant a licence; clarify any unclear redistribution rights before contributing external material. Follow the [code of conduct](https://github.com/edithatogo/.github/blob/main/CODE_OF_CONDUCT.md) and keep technical discussions respectful.

## Basis for this guide

This guide follows [GitHub's contribution-guideline guidance](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/setting-guidelines-for-repository-contributors) and the contribution-process and testing principles in [OpenSSF Best Practices](https://www.bestpractices.dev/en/criteria). It does not assert certification.
