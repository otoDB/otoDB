import os
import fnmatch
import shutil
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
db_name = os.getenv("OTODB_DB_NAME")  # Default to db.sqlite3 if not set

root_dir = Path('.')

for dirpath, dirnames, filenames in os.walk(root_dir):
    dirnames[:] = [d for d in dirnames if d not in ["venv", ".git"]]

    for filepath in fnmatch.filter([str(Path(dirpath) / f) for f in filenames], ["otodb/migrations/*.py", "otodb/**/migrations/*.py"]):
        if Path(filepath).name != "__init__.py":
            print(f"Removing: {filepath}")
            os.remove(filepath)

# Remove the database file if it exists
if db_name:
    db_path = root_dir / db_name
    if db_path.exists():
        print(f"Removing database file: {db_path}")
        db_path.unlink()
    else:
        print(f"Database file not found: {db_path}")
