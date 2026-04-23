import subprocess
import sys

from dotenv import load_dotenv

load_dotenv()

subprocess.run([sys.executable, 'manage.py', 'migrate'], check=True)
subprocess.run(
	[sys.executable, 'manage.py', 'createsuperuser', '--noinput'], check=False
)
