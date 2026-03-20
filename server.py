#!/usr/bin/env python3
"""
Redmine MCP Server
Exposes Redmine REST API as MCP tools for Claude Code.

Environment variables:
  REDMINE_URL     — base URL, e.g. https://redmine.example.com
  REDMINE_API_KEY — your personal API key (My account → API access key)
"""

import os
import json
import httpx
from mcp.server.fastmcp import FastMCP

REDMINE_URL = os.environ.get("REDMINE_URL", "").rstrip("/")
REDMINE_API_KEY = os.environ.get("REDMINE_API_KEY", "")

mcp = FastMCP("redmine")

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

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
        # Redmine returns 200 with body or 204 with no body
        return resp.json() if resp.content else {}


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@mcp.tool()
def get_issue(issue_id: int) -> str:
    """
    Get a Redmine issue by ID.
    Returns full issue details: title, description, status, priority,
    assignee, progress, dates, custom fields.
    """
    data = _get(f"/issues/{issue_id}.json")
    issue = data["issue"]
    return json.dumps(issue, ensure_ascii=False, indent=2)


@mcp.tool()
def get_issue_statuses() -> str:
    """
    Get all available issue statuses in Redmine.
    Use this to find the correct status_id before calling update_issue_status.
    """
    data = _get("/issue_statuses.json")
    return json.dumps(data["issue_statuses"], ensure_ascii=False, indent=2)


@mcp.tool()
def update_issue_status(issue_id: int, status_id: int, comment: str = "") -> str:
    """
    Change the status of a Redmine issue.

    Args:
        issue_id:  Redmine issue ID
        status_id: Target status ID (use get_issue_statuses to find IDs)
        comment:   Optional comment to add with the status change
    """
    body: dict = {"issue": {"status_id": status_id}}
    if comment:
        body["issue"]["notes"] = comment
    _put(f"/issues/{issue_id}.json", body)
    return f"Issue #{issue_id} status updated to status_id={status_id}."


@mcp.tool()
def update_issue_progress(issue_id: int, done_ratio: int, comment: str = "") -> str:
    """
    Update the % done (progress) of a Redmine issue.

    Args:
        issue_id:   Redmine issue ID
        done_ratio: Progress value 0–100 (percent done)
        comment:    Optional comment to add with the update
    """
    if not 0 <= done_ratio <= 100:
        return "Error: done_ratio must be between 0 and 100."
    body: dict = {"issue": {"done_ratio": done_ratio}}
    if comment:
        body["issue"]["notes"] = comment
    _put(f"/issues/{issue_id}.json", body)
    return f"Issue #{issue_id} progress updated to {done_ratio}%."


@mcp.tool()
def get_issue_comments(issue_id: int) -> str:
    """
    Get all comments (journal notes) for a Redmine issue.
    Returns list of comments with author, date, and text.
    """
    data = _get(f"/issues/{issue_id}.json", params={"include": "journals"})
    journals = data["issue"].get("journals", [])
    comments = [
        {
            "id": j["id"],
            "author": j["user"]["name"],
            "created_on": j["created_on"],
            "notes": j.get("notes", ""),
            "details": j.get("details", []),  # field changes
        }
        for j in journals
    ]
    return json.dumps(comments, ensure_ascii=False, indent=2)


@mcp.tool()
def add_issue_comment(issue_id: int, comment: str) -> str:
    """
    Add a comment (journal note) to a Redmine issue.

    Args:
        issue_id: Redmine issue ID
        comment:  Text of the comment to add
    """
    _put(f"/issues/{issue_id}.json", {"issue": {"notes": comment}})
    return f"Comment added to issue #{issue_id}."


@mcp.tool()
def assign_issue(issue_id: int, assigned_to_id: int, comment: str = "") -> str:
    """
    Assign a Redmine issue to a user.

    Args:
        issue_id:       Redmine issue ID
        assigned_to_id: User ID to assign to (use get_project_members to find IDs)
        comment:        Optional comment to add with the assignment
    """
    body: dict = {"issue": {"assigned_to_id": assigned_to_id}}
    if comment:
        body["issue"]["notes"] = comment
    _put(f"/issues/{issue_id}.json", body)
    return f"Issue #{issue_id} assigned to user_id={assigned_to_id}."


@mcp.tool()
def get_project_members(project_id: str) -> str:
    """
    Get members of a Redmine project (useful for finding user IDs for assignment).

    Args:
        project_id: Project ID or identifier (slug)
    """
    data = _get(f"/projects/{project_id}/memberships.json")
    members = [
        {
            "id": m.get("user", {}).get("id"),
            "name": m.get("user", {}).get("name"),
            "roles": [r["name"] for r in m.get("roles", [])],
        }
        for m in data.get("memberships", [])
        if "user" in m  # skip group memberships
    ]
    return json.dumps(members, ensure_ascii=False, indent=2)


@mcp.tool()
def list_issues(
    project_id: str = "",
    status_id: str = "open",
    assigned_to_id: str = "",
    limit: int = 25,
    offset: int = 0,
) -> str:
    """
    List Redmine issues with optional filters.

    Args:
        project_id:      Filter by project ID or slug (empty = all projects)
        status_id:       "open", "closed", "*" (all), or a numeric status ID
        assigned_to_id:  Numeric user ID, or "me" for the API key owner
        limit:           Max results (1–100, default 25)
        offset:          Pagination offset
    """
    params: dict = {
        "status_id": status_id,
        "limit": min(limit, 100),
        "offset": offset,
    }
    if assigned_to_id:
        params["assigned_to_id"] = assigned_to_id

    path = f"/projects/{project_id}/issues.json" if project_id else "/issues.json"
    data = _get(path, params=params)

    issues = [
        {
            "id": i["id"],
            "subject": i["subject"],
            "status": i["status"]["name"],
            "priority": i["priority"]["name"],
            "assigned_to": i.get("assigned_to", {}).get("name", "—"),
            "done_ratio": i.get("done_ratio", 0),
            "updated_on": i.get("updated_on", ""),
        }
        for i in data.get("issues", [])
    ]
    total = data.get("total_count", len(issues))
    return json.dumps({"total": total, "issues": issues}, ensure_ascii=False, indent=2)


@mcp.tool()
def update_issue(
    issue_id: int,
    subject: str = "",
    description: str = "",
    priority_id: int = 0,
    due_date: str = "",
    comment: str = "",
) -> str:
    """
    Update general fields of a Redmine issue.

    Args:
        issue_id:    Redmine issue ID
        subject:     New title (leave empty to keep current)
        description: New description (leave empty to keep current)
        priority_id: Priority ID (leave 0 to keep current)
        due_date:    Due date in YYYY-MM-DD format (leave empty to keep current)
        comment:     Optional journal note
    """
    payload: dict = {}
    if subject:
        payload["subject"] = subject
    if description:
        payload["description"] = description
    if priority_id:
        payload["priority_id"] = priority_id
    if due_date:
        payload["due_date"] = due_date
    if comment:
        payload["notes"] = comment

    if not payload:
        return "Nothing to update — all fields are empty."

    _put(f"/issues/{issue_id}.json", {"issue": payload})
    return f"Issue #{issue_id} updated: {list(payload.keys())}."


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if not REDMINE_URL or not REDMINE_API_KEY:
        raise RuntimeError(
            "REDMINE_URL and REDMINE_API_KEY environment variables must be set."
        )
    transport = os.environ.get("MCP_TRANSPORT", "stdio")
    if transport == "http":
        mcp.settings.host = os.environ.get("MCP_HOST", "0.0.0.0")
        mcp.settings.port = int(os.environ.get("MCP_PORT", "8000"))
        mcp.run(transport="streamable-http")
    else:
        mcp.run(transport="stdio")
