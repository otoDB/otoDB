from os import system

system('python manage.py makemigrations')
system('python manage.py migrate')
system('DJANGO_SUPERUSER_PASSWORD=admin python manage.py createsuperuser --noinput --username admin --email admin@otodb.net')

