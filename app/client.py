import json
import httpx
from .config import REDMINE_URL, REDMINE_API_KEY


def _headers() -> dict:
    return {
        "X-Redmine-API-Key": REDMINE_API_KEY,
        "Content-Type": "application/json",
    }


def _get(path: str, params: dict | None = None) -> dict:
    url = f"{REDMINE_URL}{path}"
    with httpx.Client(timeout=15) as client:
        resp = client.get(url, headers=_headers(), params=params or {})
        resp.raise_for_status()
        return resp.json()


def _put(path: str, body: dict) -> dict:
    url = f"{REDMINE_URL}{path}"
    with httpx.Client(timeout=15) as client:
        resp = client.put(url, headers=_headers(), content=json.dumps(body))
        resp.raise_for_status()
        return resp.json() if resp.content else {}


def _post(path: str, body: dict) -> dict:
    url = f"{REDMINE_URL}{path}"
    with httpx.Client(timeout=15) as client:
        resp = client.post(url, headers=_headers(), content=json.dumps(body))
        resp.raise_for_status()
        return resp.json()
