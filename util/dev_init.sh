#!/bin/bash

find . -path "./otodb/migrations/*.py" -not -name "__init__.py" -not -path "./venv/*"
rm db.sqlite3 || true