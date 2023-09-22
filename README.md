# otoDB

otoDB *(stylistically 音DB)* is a community-driven website consisting of a collaborative user-managed database, forum, and wiki.

## ! NOTICE !

As the model schema is still a very early WIP, migrations are currently not committed as part of this repo. You will need to make these migrations yourself (the command is provided below).

## Setup

```sh
# Setup the initial environment
git clone https://github.com/mmaker-gh/otodb.git
cd otodb
python -m virtualenv venv
python -m pip install -r requirements.txt

# Make migrations and migrate changes
python manage.py makemigrations
python manage.py migrate

# Load seed data
python manage.py loaddata otodb/fixtures/otodb/category.yaml

# Create admin account
python manage.py createsuperuser

# Copy the base .env file (you will need to modify this!)
cp .env.example .env
nano .env

# Run
python manage.py runserver
```
