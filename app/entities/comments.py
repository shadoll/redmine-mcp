import json
from ..mcp import mcp
from ..client import _get, _put, _delete


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
def get_issue_history(issue_id: int) -> str:
    """
    Get the full change history of a Redmine issue with all field changes,
    comments, and a deduplicated participant list.

    Returns:
        - issue:        id, subject, author, created_on, current assignee,
                        current status, watchers
        - history:      chronological list of journal entries, each with:
                          user_id, user (name), created_on, notes (comment),
                          changes (list of field_name, old_value → new_value)
        - participants: deduplicated list of every user who interacted with
                        the issue (author, assignee, watchers, commenters,
                        editors) with their roles
    """
    data = _get(f"/issues/{issue_id}.json", params={"include": "journals,watchers"})
    issue = data["issue"]
    journals = issue.get("journals", [])

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

    history = []
    for j in journals:
        user = j.get("user", {})
        uid = user.get("id")
        uname = user.get("name", "?")
        if uid:
            if j.get("notes"):
                _add(uid, uname, "commenter")
            if j.get("details"):
                _add(uid, uname, "editor")

        entry: dict = {
            "id": j["id"],
            "user_id": uid,
            "user": uname,
            "created_on": j["created_on"],
            "notes": j.get("notes", ""),
            "changes": [
                {
                    "field": d.get("name", ""),
                    "property": d.get("property", ""),
                    "old_value": d.get("old_value"),
                    "new_value": d.get("new_value"),
                }
                for d in j.get("details", [])
            ],
        }
        history.append(entry)

    result = {
        "issue": {
            "id": issue["id"],
            "subject": issue["subject"],
            "author": author,
            "created_on": issue.get("created_on", ""),
            "assigned_to": assignee,
            "status": issue.get("status", {}),
            "watchers": issue.get("watchers", []),
        },
        "history": history,
        "participants": list(participants.values()),
    }
    return json.dumps(result, ensure_ascii=False, indent=2)


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
def delete_issue_comment(journal_id: int) -> str:
    """
    Delete a comment (journal note) from a Redmine issue.

    Args:
        journal_id: The journal entry ID (obtainable from get_issue_comments)
    """
    _delete(f"/journals/{journal_id}.json")
    return f"Comment #{journal_id} deleted."
