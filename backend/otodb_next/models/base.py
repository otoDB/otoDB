"""Declarative base for otodb_next's SQLAlchemy models.

These models MIRROR the existing database schema, which is owned by Django
migrations until the Django cutoff -- never `create_all()` and never point
alembic at this metadata. Columns/constraints were scaffolded with sqlacodegen
against the real schema and then hand-curated:

- Python-side Django defaults (`default=`, `auto_now_add`) do not exist in the
  DDL, so they are re-declared here on the models that otodb_next writes.
- Plain performance indexes are omitted (the DB has them; Django migrations
  own them). Unique/check constraints are kept for their documentation value
  and for ON CONFLICT targets.

Deliberately-unported surface is marked with `TODO(port):` -- grep for that tag
before treating any model here as fully usable. A TODO(port) on a model or
column means the Django side is still the owner of that behavior.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase): ...
