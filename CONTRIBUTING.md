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
General
- [x] Model for songs
- [ ] Segregates song authors from actual creators
- [ ] Allows for searching for videos using a song
- [ ] Create base abstract classes for sources
- [ ] Allow tags to be weighted

Tags
- [ ] Force aliases to be replaced by actual tags
- [ ] Order `tag_mirror` field items alphabetically (if possible)
- [ ] History diff system

Models
- [ ] Pools (groups of works)
- [ ] Votes
- [ ] Favorites
- [ ] Favgroups
- [ ] More casual version of pools, might just use a different type for this
- [ ] Comments
- [ ] Notes (?)

Admin
- [ ] Roles
- [ ] Permissions

Low priority
- [ ] Allow description field to have special syntax such as video timestamps

Wiki
- [ ] Page aliases / "other names" (reuse tag aliases for this?)
- [ ] Special pages for certain tag types (creators)
- **This will need abstract source classes for websites figured out first**

Big Picture
- [ ] Forum
- [ ] Private messaging
