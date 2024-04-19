#!/bin/bash

find . -type d \( -path ./venv -o -path ./.git \) -prune -o \( -path "./otodb/migrations/*.py" -o -path "./otodb/**/migrations/*.py" \) -not -name "__init__.py" -print -exec rm -- '{}' +
rm db.sqlite3 || true
