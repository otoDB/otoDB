@echo off

set DJANGO_SUPERUSER_PASSWORD=admin
set DJANGO_SUPERUSER_USERNAME=admin
set DJANGO_SUPERUSER_EMAIL=admin@otodb.net

python manage.py makemigrations
python manage.py migrate
python manage.py loaddata otodb/fixtures/otodb/category.yaml
python manage.py createsuperuser --noinput
