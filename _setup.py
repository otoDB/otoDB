from os import system

system('python manage.py migrate')
system('python manage.py shell -c "from otodb.account.models import Account; Account.objects.create_superuser(\'admin\', \'admin@example.com\', \'admin\')"')

