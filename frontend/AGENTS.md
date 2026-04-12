# Frontend AGENTS.md

## Project Structure

- Written in **TypeScript**.
- Meta-framework is **SvelteKit** (Svelte 5).
- Styled with **TailwindCSS v4**.
- JavaScript engine is **Bun**.

## Tooling

- Install: `bun install`
- Format: `bun run format`
- Lint: `bun run lint`
- Type check: `bun run check`

## Workflow

### Before committing or pushing

When making any changes to frontend code, you MUST run the following commands in order and ensure each succeeds before creating a git commit or pushing:

1. format: `bun run format`
2. lint: `bun run lint`
3. check: `bun run check`

All three commands must succeed without errors before committing. Do not skip or bypass these checks.

## Boundaries

- Do not edit `.env`

