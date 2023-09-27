# Contributing to otoDB

Below is an overview of the structure of this project.
Application directories contain the usual Django files.

```sh
otodb/
├─ ___/                        # Project directory
│  ├─ settings.py              # Initial configuration settings
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

## TODO

*TBD*