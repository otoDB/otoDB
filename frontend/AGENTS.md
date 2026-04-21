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
- Update i18n files: `bunx @inlang/paraglide-js compile --project ./project.inlang --outdir ./src/lib/paraglide`

## Workflow

### Before committing or pushing

When making any changes to frontend code, you MUST run the following commands in order and ensure each succeeds before creating a git commit or pushing:

1. format: `bun run format`
2. lint: `bun run lint`
3. check: `bun run check`

All three commands must succeed without errors before committing. Do not skip or bypass these checks.

## Coding

- When importing components or libraries in `lib`, use `$lib` for import path.

## Boundaries

- Do not edit `.env`
