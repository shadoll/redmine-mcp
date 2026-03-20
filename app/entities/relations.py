import json
from ..mcp import mcp
from ..client import _get, _post, _delete


@mcp.tool()
def get_issue_relations(issue_id: int) -> str:
    """
    Get all relations for a Redmine issue.
    Returns relation IDs needed for remove_issue_relation.
    """
    data = _get(f"/issues/{issue_id}/relations.json")
    return json.dumps(data.get("relations", []), ensure_ascii=False, indent=2)


@mcp.tool()
def add_issue_relation(
    issue_id: int,
    related_issue_id: int,
    relation_type: str = "relates",
    delay: int = 0,
) -> str:
    """
    Add a relation between two Redmine issues.

    Args:
        issue_id:         Source issue ID
        related_issue_id: Target issue ID
        relation_type:    Type of relation:
                          - relates       — generic relation
                          - duplicates    — this issue duplicates the target
                          - duplicated    — this issue is duplicated by the target
                          - blocks        — this issue blocks the target
                          - blocked       — this issue is blocked by the target
                          - precedes      — this issue must precede the target
                          - follows       — this issue must follow the target
                          - copied_to     — this issue was copied to the target
                          - copied_from   — this issue was copied from the target
        delay:            Delay in days (used with precedes/follows)
    """
    body: dict = {"issue_to_id": related_issue_id, "relation_type": relation_type}
    if delay:
        body["delay"] = delay
    data = _post(f"/issues/{issue_id}/relations.json", {"relation": body})
    return json.dumps(data.get("relation", {}), ensure_ascii=False, indent=2)


@mcp.tool()
def remove_issue_relation(relation_id: int) -> str:
    """
    Remove a relation between issues by relation ID.
    Use get_issue_relations to find the relation ID.

    Args:
        relation_id: Relation ID (from get_issue_relations)
    """
    _delete(f"/relations/{relation_id}.json")
    return f"Relation #{relation_id} removed."


@mcp.tool()
def add_watcher(issue_id: int, user_id: int) -> str:
    """
    Add a watcher to a Redmine issue.

    Args:
        issue_id: Redmine issue ID
        user_id:  User ID to add as watcher (use get_project_members to find IDs)
    """
    _post(f"/issues/{issue_id}/watchers.json", {"user_id": user_id})
    return f"User #{user_id} added as watcher to issue #{issue_id}."


@mcp.tool()
def remove_watcher(issue_id: int, user_id: int) -> str:
    """
    Remove a watcher from a Redmine issue.

    Args:
        issue_id: Redmine issue ID
        user_id:  User ID to remove from watchers
    """
    _delete(f"/issues/{issue_id}/watchers/{user_id}.json")
    return f"User #{user_id} removed from watchers of issue #{issue_id}."
