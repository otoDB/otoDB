from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()
db_name = os.getenv("OTODB_DB_NAME") + ".sqlite3"

root_dir = Path(".")

migrations = set()

# migrations = migrations.union(glob("./otodb/migrations/*.py"))
# migrations = migrations.union(glob("./otodb/**/migrations/*.py", recursive=True))

# for p in migrations:
#     if not p.endswith('__init__.py'):
#         print(f"Removing: {p}")
#         os.remove(p)

# Remove the database file if it exists
db_path = root_dir / db_name
if db_path.exists():
    print(f"Removing database file: {db_path}")
    db_path.unlink()
else:
    print(f"Database file not found: {db_path}")
