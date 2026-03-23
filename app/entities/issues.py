import json
from ..mcp import mcp
from ..client import _get, _put, _post, _delete


def _apply_relations(issue_id: int, relations: list[dict]) -> None:
    """Create issue relations. Each item: {"issue_id": int, "relation_type": str}."""
    for rel in relations:
        _post(f"/issues/{issue_id}/relations.json", {
            "relation": {
                "issue_to_id": rel["issue_id"],
                "relation_type": rel.get("relation_type", "relates"),
            }
        })


@mcp.tool()
def create_issue(
    project_id: str,
    subject: str,
    description: str = "",
    assigned_to_id: int = 0,
    priority_id: int = 0,
    due_date: str = "",
    parent_issue_id: int = 0,
    watcher_user_ids: list[int] | None = None,
    relations: list[dict] | None = None,
) -> str:
    """
    Create a new Redmine issue.

    Args:
        project_id:       Project ID or slug
        subject:          Issue title
        description:      Issue description
        assigned_to_id:   User ID to assign (use get_project_members to find IDs)
        priority_id:      Priority ID (leave 0 for default)
        due_date:         Due date in YYYY-MM-DD format
        parent_issue_id:  Parent issue ID (makes this a subtask)
        watcher_user_ids: List of user IDs to add as watchers
        relations:        List of related issues, e.g.
                          [{"issue_id": 42, "relation_type": "relates"}]
                          Types: relates, duplicates, duplicated,
                                 blocks, blocked, precedes, follows
    """
    payload: dict = {"project_id": project_id, "subject": subject}
    if description:
        payload["description"] = description
    if assigned_to_id:
        payload["assigned_to_id"] = assigned_to_id
    if priority_id:
        payload["priority_id"] = priority_id
    if due_date:
        payload["due_date"] = due_date
    if parent_issue_id:
        payload["parent_issue_id"] = parent_issue_id
    if watcher_user_ids:
        payload["watcher_user_ids"] = watcher_user_ids

    data = _post("/issues.json", {"issue": payload})
    issue = data["issue"]

    if relations:
        _apply_relations(issue["id"], relations)

    return json.dumps({"id": issue["id"], "subject": issue["subject"]}, ensure_ascii=False, indent=2)


@mcp.tool()
def get_issue(issue_id: int) -> str:
    """
    Get a Redmine issue by ID.
    Returns full issue details: title, description, status, priority,
    assignee, progress, dates, custom fields, watchers.
    """
    data = _get(f"/issues/{issue_id}.json", params={"include": "watchers"})
    return json.dumps(data["issue"], ensure_ascii=False, indent=2)


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
    parent_issue_id: int = 0,
    watcher_user_ids: list[int] | None = None,
    relations: list[dict] | None = None,
) -> str:
    """
    Update general fields of a Redmine issue.

    Args:
        issue_id:         Redmine issue ID
        subject:          New title (leave empty to keep current)
        description:      New description (leave empty to keep current)
        priority_id:      Priority ID (leave 0 to keep current)
        due_date:         Due date in YYYY-MM-DD format (leave empty to keep current)
        comment:          Optional journal note
        parent_issue_id:  Parent issue ID (makes this a subtask; 0 = no change)
        watcher_user_ids: List of user IDs to add as watchers
        relations:        List of relations to add, e.g.
                          [{"issue_id": 42, "relation_type": "blocks"}]
                          Types: relates, duplicates, duplicated,
                                 blocks, blocked, precedes, follows
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
    if parent_issue_id:
        payload["parent_issue_id"] = parent_issue_id

    if not payload and not watcher_user_ids and not relations:
        return "Nothing to update — all fields are empty."

    if payload:
        _put(f"/issues/{issue_id}.json", {"issue": payload})

    for user_id in (watcher_user_ids or []):
        _post(f"/issues/{issue_id}/watchers.json", {"user_id": user_id})

    if relations:
        _apply_relations(issue_id, relations)

    updated = list(payload.keys())
    if watcher_user_ids:
        updated.append("watchers")
    if relations:
        updated.append("relations")
    return f"Issue #{issue_id} updated: {updated}."


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
