## Backend AGENTS.md

## Tooling

- Format: `uvx ruff format`
- Lint: `uvx ruff check`
- Test: `uv run pytest`
- Test for specific file: `uv run pytest foo.py`

## Workflow

### Before committing

When making any changes to backend code, you MUST run the following commands in order and ensure each succeeds before creating a git commit or pushing:

- format: `uvx ruff format`
- lint: `uvx ruff check`
- Update openapi.json: `uv run manage.py openapi_schema > openapi.json`

All these commands must succeed without errors before committing. Do not skip or bypass these checks.

### Before pushing

Before push, you MUST test.

## Boundaries

- Do not edit `.env`
