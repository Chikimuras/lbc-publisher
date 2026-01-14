# Git Hooks

This directory contains Git hooks to maintain code quality.

## Available Hooks

### pre-commit
Runs on every commit to ensure code quality:
- **Ruff**: Lints Python code with auto-fix
- **Black**: Formats Python code with auto-fix

If auto-fix modifies files, you'll need to re-stage and commit again.

### pre-push
Runs before pushing to ensure code stability:
- **Ruff**: Quick lint check (no auto-fix)
- **Black**: Quick format check (no auto-fix)
- **Pytest**: Runs all unit tests

If any check fails, the push is blocked.

## Installation

Install hooks for your local repository:

```bash
bash .githooks/install.sh
```

This will copy the hooks to `.git/hooks/` and make them executable.

## Uninstallation

To remove the hooks:

```bash
bash .githooks/uninstall.sh
```

## Bypassing Hooks

In rare cases where you need to bypass hooks (not recommended):

```bash
# Skip pre-commit hook
git commit --no-verify

# Skip pre-push hook
git push --no-verify
```

## Manual Testing

You can manually run the same checks the hooks perform:

```bash
# Pre-commit checks
uv run ruff check src/ tests/ --fix
uv run black src/ tests/

# Pre-push checks
uv run ruff check src/ tests/
uv run black src/ tests/ --check
uv run pytest -v
```