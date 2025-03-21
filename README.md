# otoDB
otoDB is a community-driven website consisting of a collaborative user-managed database and wiki.

## Backend Setup
We recommend using `uv`.
```sh
cd backend

# Copy the base .env file
cp ../.env.example .env

# Make necessary modifications to .env, e.g. add accepted hosts

# Migrate changes and create admin account
uv run _setup.py

# Run
uv run manage.py runserver
```

Be careful: the script `_clear.py` deletes the database.

## Frontend Setup
We recommend using `bun`.
```sh
cd frontend

# Setup for default backend addresses in dev mode
cp .env.example .env

bun install

bun run dev
```

To regenerate API types (on the default dev backend, the schema is served on `http://127.0.0.1:8000/api/openapi.json` behind admin auth):
```sh
cd frontend

bunx openapi-typescript openapi.json -o src/lib/schema.d.ts
```

Whenever you make a request on the server-side of the metaframework through the API client, you have to inject SvelteKit's `fetch` as follows (otherwise cookies will not be passed along):
```ts
export const load: PageServerLoad = async ({ params, fetch }) => {
                                                     ^^^^^       vvvvv
    const { data, error } = await client.GET('/api/work/work', { fetch, params: { query: {
        work_id: +params.work_id
    }}});
```
