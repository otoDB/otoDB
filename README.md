# otoDB
otoDB is a community-driven website consisting of a collaborative user-managed database and wiki.

<!-- ## ! NOTICE !
As the model schema is still a very early WIP, migrations are currently not committed as part of this repo. You will need to make these migrations yourself (the command is provided below). -->

## Setup
We recommend using `uv`. Project setup is contained in `pyproject.toml`.
```sh
# Copy the base .env file
cp .env.example .env

# Make necessary modifications to .env, e.g. add accepted hosts

# Make migrations if starting from scratch
# uv run manage.py makemigrations

# Migrate changes and create admin account
uv run _setup.py

# Run
uv run manage.py runserver
```

The script `_clear.py` clears migratinos and deletes the database, at which point you can run `_setup.py` again.

When running through `uv`, you may get an SSL error when the server fetches content from the web, because the virtual enviroment cannot find the local certificates. Map the variable `SSL_CERT_FILE` to the correct location:
```sh
# Linux
export SSL_CERT_FILE=/etc/ssl/certs/ca-bundle.crt
```

You should also change the domain of the default site in the admin panel.

<!-- ## Project Structure
Below is an overview of the structure of this project. Application directories contain the usual Django files.

```sh
/
├─ ___/                        # Project directory
│  ├─ settings.py              # Global configuration settings
├─ otodb/                      # Main application
│  ├─ account/                 # Account app
│  ├─ common/                  # Common functionality
│  ├─ fixtures/                # Database seed data
│  ├─ migrations/              # Database migrations
│  ├─ models/                  # Database models
│  │  ├─ enums/                # Shared enums
│  │  ├─ sources/              # Models for sources (i.e. websites)
│  ├─ templates/               # View templates
│  ├─ templatetags/            # Tag templates for views
│  ├─ tests/                   # Tests
│  ├─ views/                   # View logic
│  ├─ context_preprocessors.py # Context for views, currently just a global `G`
├─ .env                        # Environment configuration
``` -->
