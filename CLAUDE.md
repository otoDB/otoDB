# otoDB - Claude Code Instructions

## Project Overview

otoDB is a full-stack application for managing media works. It consists of:

- **Backend**: Django 6 + Django Ninja REST API (Python 3.14+, managed by `uv`)
- **Frontend**: SvelteKit 2 + Svelte 5 + TypeScript + Tailwind CSS 4 (managed by `bun`)
- **Browser Extension**: Chrome/Firefox extension (managed by `bun`/`npm`)

## Architecture

- Backend exposes a REST API at `/api/` documented as OpenAPI at `/api/openapi.json`
- Frontend uses generated TypeScript types from the OpenAPI schema (`bunx openapi-typescript`)
- Server-side SvelteKit fetch must use the injected `fetch` to maintain session cookies
- PostgreSQL 17 in production, SQLite supported for development/testing

## Development Commands

### Backend (`backend/`)

```bash
uv sync                        # Install dependencies
uv run manage.py runserver     # Dev server
uv run pytest -v --tb=short    # Run tests
uvx ruff format .              # Format code
uvx ruff check .               # Lint code
uv run _setup.py               # Initialize DB and create admin user
```

### Frontend (`frontend/`)

```bash
bun install                    # Install dependencies
bun run dev                    # Dev server
bun run build                  # Production build
bun run check                  # Type check
bun run lint                   # Check formatting + lint (Prettier + ESLint)
bun run format                 # Auto-format
bun run storybook              # Storybook dev server
```

### Browser Extension (`browser-extension/`)

```bash
bun run build:chrome           # Build Chrome extension
bun run build:firefox          # Build Firefox extension
```

## Code Style

### Python (Backend)

- Formatter/linter: **ruff** (configured in `pyproject.toml`)
- Pre-commit hooks run ruff format and ruff check automatically
- Follow existing patterns in `otodb/api/` for new API endpoints using Django Ninja routers

### TypeScript/Svelte (Frontend)

- Formatter: **Prettier** (`.prettierrc`)
- Linter: **ESLint** (`eslint.config.js`)
- Use Svelte 5 runes syntax (`$state`, `$derived`, `$effect`, `$props`)
- Tailwind CSS 4 for styling

## Testing

### Backend

- Framework: pytest + pytest-django
- Fixtures in `tests/conftest.py` (use `work_client`, `tag_client`, `auth_client` for authenticated API tests)
- Run against SQLite locally; CI also runs against PostgreSQL 17

### Frontend

- Unit tests: Vitest
- E2E tests: Playwright

## Environment Setup

- Backend: copy `backend/.env.example` to `backend/.env` and fill in values
- Frontend: copy `frontend/.env.example` to `frontend/.env` and fill in values
- Docker: `docker-compose up` to start all services

## Key Patterns

- API endpoints live in `backend/otodb/api/` as Django Ninja routers
- SvelteKit routes in `frontend/src/routes/`
- Reusable components in `frontend/src/lib/`
- Never skip pre-commit hooks (`--no-verify`)
- When modifying the backend API, regenerate frontend types: `bunx openapi-typescript <url> -o src/lib/api/schema.d.ts`
