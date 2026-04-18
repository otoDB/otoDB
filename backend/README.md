# Backend

## Setup

Install [uv](https://github.com/astral-sh/uv).

```shell
# Setup pre-commit
pre-commit

# Copy the base .env file
cp .env.example .env

# Setup middlewares for development
docker compose up -d

# Migrate changes and create admin account
uv run _setup.py

# Add sample data
uv run manage.py seed_data

# Run
uv run manage.py runserver
```

Optionally provide a `cookies.txt` file in Netscape cookies.txt format for use when fetching information from external websites. You can also use browser extensions to extract them from a session (e.g. [cookies.txt](https://addons.mozilla.org/ja/firefox/addon/cookies-txt/)).

### Reset the database

```shell
psql "postgresql://$OTODB_DB_USER:$OTODB_DB_PASSWORD@$OTODB_DB_HOST:$OTODB_DB_PORT/postgres" \
  -c "DROP DATABASE IF EXISTS \"$OTODB_DB_NAME\";" \
  -c "CREATE DATABASE \"$OTODB_DB_NAME\";"
```

### Test

```shell
uv run pytest
```

### Notes

- Default user username specified in .env.example: `admin` and password: `admin`.
