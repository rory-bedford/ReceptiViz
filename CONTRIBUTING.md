# Contributing Guide

Thanks for contributing! This project uses `uv` for dependency management, `pre-commit` for code quality enforcement, and `pytest` for testing. Follow the steps below to get set up.

## Setup

1. **Clone the repository:**

   ```bash
   git clone git@github.com:rory-bedford/Receptual.git
   cd Receptual
   ```

2. **Check development environment:**

   ```bash
   uv sync
   uv run receptual
   ```

3. **Install pre-commit hooks:**

   ```bash
   uv run pre-commit install
   ```

## What Gets Linted/Formatted Automatically

On every commit, `pre-commit` will run:

- `ruff check --fix` — static analysis / linting
- `ruff format` — formats code
- `pytest` — runs unit tests

We then have a GitHub action that runs:

- `ruff check` 
- `ruff format --check`
- `pytest`

Any pull request will be blocked if any of these fail.

## Run Checks Manually

You can also run the formatting and checks manually anytime:

```bash
uv run ruff check --fix         # Lint
uv run ruff format              # Format check
uv run pytest                   # Run tests
```

## Guidelines

- Code must be formatted (`ruff format`)
- Code must pass linting (`ruff check`)
- Code must be tested (`pytest`)
- All CI checks must pass before merging

## Publishing

Git tags pushed to main get built into a Github release, get pushed to PyPI, and have docs built and published by ReadtheDocs. This can only be done by administrators of the package.

Prior to do so, make sure you:

- Update the version in pyproject.toml
- Update the version in docs/source/conf.py
- Add an entry to the changelog
- Commit these changes

Then you can run:

```bash
git tag v*.*.*
git push origin v*.*.*
```
