# otoDB
otoDB is a community-driven website consisting of a collaborative user-managed database and wiki.

## Backend Setup
We recommend using `uv`.
```sh
cd backend

# Copy the base .env file
cp .env.example .env

# Make necessary modifications to .env, e.g. add accepted hosts

# Migrate changes and create admin account
uv run _setup.py

# Run
uv run manage.py runserver
```

The script `_clear.py` and deletes the database, at which point you can run `_setup.py` again.

When running through `uv`, you may get an SSL error when the server fetches content from the web, because the virtual enviroment cannot find the local certificates. If this is the case, map the variable `SSL_CERT_FILE` to the correct location:
```sh
# Linux
export SSL_CERT_FILE=/etc/ssl/certs/ca-bundle.crt
```

You may also need to change the domain of the default site (example.com) in the admin panel.

## Frontend Setup
We recommend using `bun`. You can replace `bun` with `npm` below.
```sh
cd frontend

# Setup for default backend addresses in dev mode
cp .env.example .env

bun install

bun run dev
# or start the server and open the app in a new browser tab
bun run dev -- --open
```

To regenerate API types (the default dev backend is served on`http://127.0.0.1:8000`.), you can replace `bunx` with `npx`:
```sh
bunx openapi-typescript <server>/api/openapi.json -o src/lib/schema.d.ts
```
