import os
from dotenv import load_dotenv

load_dotenv()

os.system("python manage.py migrate")
os.system("python manage.py createsuperuser --noinput")
