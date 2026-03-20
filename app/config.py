import os

REDMINE_URL = os.environ.get("REDMINE_URL", "").rstrip("/")
REDMINE_API_KEY = os.environ.get("REDMINE_API_KEY", "")


def validate():
    missing = [name for name, val in [("REDMINE_URL", REDMINE_URL), ("REDMINE_API_KEY", REDMINE_API_KEY)] if not val]
    if missing:
        print(f"ERROR: Required environment variable(s) not set: {', '.join(missing)}")
        print("Set them in your .env file or pass via -e flags. Exiting.")
        raise SystemExit(0)
