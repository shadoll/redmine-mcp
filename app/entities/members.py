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
