import os

REDMINE_URL = os.environ.get("REDMINE_URL", "").rstrip("/")
REDMINE_API_KEY = os.environ.get("REDMINE_API_KEY", "")


def validate():
    if not REDMINE_URL or not REDMINE_API_KEY:
        raise RuntimeError(
            "REDMINE_URL and REDMINE_API_KEY environment variables must be set."
        )
