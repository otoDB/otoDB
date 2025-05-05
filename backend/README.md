# Backend

## Setup

We recommend using `uv`.

```sh
# Copy the base .env file
cp .env.example .env

# Make necessary modifications to .env, e.g. add accepted hosts

# Migrate changes and create admin account
uv run _setup.py

# Run
uv run manage.py runserver
```

Be careful: the script `_clear.py` deletes the database.
