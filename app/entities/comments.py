import json
from ..mcp import mcp
from ..client import _get, _put


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
            "details": j.get("details", []),
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
