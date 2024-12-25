# otoDB

otoDB *(stylistically 音DB)* is a community-driven website consisting of a collaborative user-managed database, forum, and wiki.

## ! NOTICE !

As the model schema is still a very early WIP, migrations are currently not committed as part of this repo. You will need to make these migrations yourself (the command is provided below).

## Setup
Install the required python packages via your preferred means.
```sh
# Make migrations, migrate changes, load seed data, create admin account
.\util\dev_setup.bat

# Copy the base .env file (you will need to modify this!)
copy .env.example .env
notepad .env

# Run
python manage.py runserver
```
