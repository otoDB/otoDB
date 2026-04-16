## Backend AGENTS.md

## Tooling

- Format: `uvx ruff format`
- Lint: `uvx ruff check`
- Test: `uv run pytest`

## Workflow

### Before committing

When making any changes to backend code, you MUST run the following commands in order and ensure each succeeds before creating a git commit or pushing:

1. format: `uvx ruff format`
2. lint: `uvx ruff check`

All three commands must succeed without errors before committing. Do not skip or bypass these checks.

### Before pushing

Before push, you MUST test.

## Boundaries

- Do not edit `.env`
