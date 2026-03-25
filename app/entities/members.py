import json
from ..mcp import mcp
from ..client import _get, _put


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
        if "user" in m
    ]
    return json.dumps(members, ensure_ascii=False, indent=2)


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
def unassign_issue(issue_id: int, comment: str = "") -> str:
    """
    Remove the assignee from a Redmine issue (set to unassigned).

    Args:
        issue_id: Redmine issue ID
        comment:  Optional comment to add with the change
    """
    body: dict = {"issue": {"assigned_to_id": ""}}
    if comment:
        body["issue"]["notes"] = comment
    _put(f"/issues/{issue_id}.json", body)
    return f"Issue #{issue_id} unassigned."


@mcp.tool()
def get_issue_participants(issue_id: int) -> str:
    """
    Get all users who have participated in a Redmine issue:
    author, current assignee, watchers, commenters, and editors.

    Useful for understanding who works with a task and who wrote comments.
    Each participant includes their roles (author, assignee, watcher,
    commenter, editor) based on actual actions recorded in the issue history.

    Args:
        issue_id: Redmine issue ID
    """
    data = _get(f"/issues/{issue_id}.json", params={"include": "journals,watchers"})
    issue = data["issue"]

    participants: dict[int, dict] = {}

    def _add(uid: int, uname: str, role: str) -> None:
        if uid not in participants:
            participants[uid] = {"id": uid, "name": uname, "roles": []}
        if role not in participants[uid]["roles"]:
            participants[uid]["roles"].append(role)

    author = issue.get("author", {})
    if author.get("id"):
        _add(author["id"], author["name"], "author")

    assignee = issue.get("assigned_to", {})
    if assignee.get("id"):
        _add(assignee["id"], assignee["name"], "assignee")

    for w in issue.get("watchers", []):
        if w.get("id"):
            _add(w["id"], w["name"], "watcher")

    for j in issue.get("journals", []):
        user = j.get("user", {})
        uid = user.get("id")
        uname = user.get("name", "?")
        if uid:
            if j.get("notes"):
                _add(uid, uname, "commenter")
            if j.get("details"):
                _add(uid, uname, "editor")

    return json.dumps(list(participants.values()), ensure_ascii=False, indent=2)
