# otoDB

otoDB is a community-driven website consisting of a collaborative user-managed database, forum, and wiki.

## ! NOTICE !
As the model schema is still a very early WIP, migrations are currently not committed as part of this repo. You will need to make these migrations yourself (the command is provided below).

## Dependencies
```
diff_match_patch
Django
django-bitfield
django_simple_history
django-tagulous
dotmap
python-dotenv
PyYAML
yt-dlp
django-model-utils
pypinyin
pykakasi
```

## Setup
Install the required python packages via your preferred means.
```sh
# Copy the base .env file
copy .env.example .env

# Make necessary modifications to .env, e.g. change DB name to "db", add accepted hosts

# Make migrations, migrate changes, load seed data, create admin account
python _setup.py

# Run
python manage.py runserver
```

The script `_clear.py` clears migratinos and deletes the database, at which point you can run `_setup.py` again.

## Project Structure
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
```
