#!/bin/bash

find . -path "*/migrations/*.py" -not -name "__init__.py"
rm db.sqlite3