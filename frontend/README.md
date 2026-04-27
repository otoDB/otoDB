# Frontend

## Setup

We recommend using `bun`.

```sh
# Setup for default backend addresses in dev mode
cp .env.example .env

bun install

bun run dev
```

On the default dev backend, the schema is served on `http://127.0.0.1:8000/api/openapi.json`. An updated copy should be committed at /backend/openapi.json, to which /frontend/openapi.json is symlinked to. Based on this committed JSON schema, generate the TypeScript schema with:

```sh
bun run sync-schema
```

Whenever you make a request on the server-side of the metaframework through the API client, you have to inject SvelteKit's `fetch` as follows (otherwise cookies will not be passed along):

```ts
export const load: PageServerLoad = async ({ params, fetch }) => {
                                                     ^^^^^       vvvvv
    const { data, error } = await client.GET('/api/work/work', { fetch, params: { query: {
        work_id: +params.work_id
    }}});
```

### Test

```
bun run test
```

### Storybook

Component catalog.

```
bun run storybook
```
