# GitHub Copilot Instructions for otoDB

## Project Overview

otoDB is a full-stack media management application:

- **Backend**: Django 6 + Django Ninja (Python 3.14+)
- **Frontend**: SvelteKit 2 + Svelte 5 + TypeScript + Tailwind CSS 4
- **Browser Extension**: Chrome/Firefox extension

## Backend (Python/Django)

- Use Django Ninja for all new API endpoints; follow the router pattern in `otodb/api/`
- Schema classes go in the same file as their router (or a `schemas.py` sibling)
- Use `psycopg` (not `psycopg2`) for any raw DB access
- Async views are supported via Granian ASGI server
- Task queuing uses `django-tasks-rq`; enqueue via `django_tasks`
- ORM: prefer `select_related`/`prefetch_related` over N+1 queries
- Follow ruff formatting and linting rules (4-space indentation, standard Python style)

## Frontend (TypeScript/Svelte)

- Use **Svelte 5 runes** exclusively: `$state`, `$derived`, `$effect`, `$props`, `$bindable`
- Do NOT use Svelte 4 reactive declarations (`$:`) or stores (`writable`, `readable`)
- API calls on the server side must use the SvelteKit-injected `fetch` (passed from `load` functions)
- API types are generated from the OpenAPI schema — use them from `$lib/api/`
- Tailwind CSS 4 utility classes for all styling; avoid inline styles
- Components go in `src/lib/components/`; utilities in `src/lib/`
- Format with Prettier and lint with ESLint before committing

## General Guidelines

- Indent with **tabs** (displayed as 4 spaces) — see `.editorconfig`
- YAML files use 2-space indentation
- UTF-8 encoding, LF line endings, final newline required
- Write tests for new backend API endpoints using pytest fixtures in `tests/conftest.py`
- Prefer editing existing files over creating new ones
- Keep changes minimal and focused; avoid refactoring unrelated code
