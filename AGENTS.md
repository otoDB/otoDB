# AGENTS.md

## Commit conventions

- This project does **not** follow Conventional Commits.
- Write commit messages in plain, descriptive English that clearly explains what changed and why.

## Workflow

### Before committing or pushing

When making any changes to backend code, you MUST run the following commands in order and ensure each succeeds before creating a git commit or pushing:

1. Format: `uvx ruff format --check`
2. Lint: `uvx ruff check` 
3. Keep fresh openapi.json: `uv run manage.py openapi_schema > openapi.json`

## Writing tests

### for API

- Name test files after the endpoint they cover: `test_METHOD_endpoint.py` (e.g., `test_GET_tags_needed.py`, `test_PUT_post_close.py`).
