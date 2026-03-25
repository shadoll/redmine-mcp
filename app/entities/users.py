import json
from ..mcp import mcp
from ..client import _get


@mcp.tool()
def get_current_user() -> str:
    """
    Get information about the currently authenticated Redmine user (API key owner).
    Returns user ID, login, name, email, created_on, last_login_on.
    """
    data = _get("/users/current.json")
    return json.dumps(data.get("user", {}), ensure_ascii=False, indent=2)


@mcp.tool()
def get_user(user_id: int) -> str:
    """
    Get a Redmine user by ID.
    Returns user details: login, name, created_on, last_login_on, groups, memberships.

    Args:
        user_id: Redmine user ID
    """
    data = _get(f"/users/{user_id}.json", params={"include": "groups,memberships"})
    return json.dumps(data.get("user", {}), ensure_ascii=False, indent=2)


@mcp.tool()
def list_users(
    status: int = 1,
    name: str = "",
    group_id: int = 0,
    limit: int = 25,
    offset: int = 0,
) -> str:
    """
    List Redmine users. Requires administrator privileges.

    Args:
        status:   Filter by account status:
                  0 = anonymous, 1 = active (default), 2 = registered,
                  3 = locked, 4 = all
        name:     Filter by login, first/last name, or email (partial match)
        group_id: Filter by group ID
        limit:    Max results (1–100, default 25)
        offset:   Pagination offset
    """
    params: dict = {"status": status, "limit": min(limit, 100), "offset": offset}
    if name:
        params["name"] = name
    if group_id:
        params["group_id"] = group_id

    data = _get("/users.json", params=params)
    users = [
        {
            "id": u["id"],
            "login": u.get("login", ""),
            "name": f"{u.get('firstname', '')} {u.get('lastname', '')}".strip(),
            "mail": u.get("mail", ""),
            "created_on": u.get("created_on", ""),
            "last_login_on": u.get("last_login_on", ""),
        }
        for u in data.get("users", [])
    ]
    total = data.get("total_count", len(users))
    return json.dumps({"total": total, "users": users}, ensure_ascii=False, indent=2)


@mcp.tool()
def search_users(name: str) -> str:
    """
    Search Redmine users by name, login, or email. Requires administrator privileges.

    Args:
        name: Partial name, login, or email to search for
    """
    data = _get("/users.json", params={"name": name, "status": 1, "limit": 50})
    users = [
        {
            "id": u["id"],
            "login": u.get("login", ""),
            "name": f"{u.get('firstname', '')} {u.get('lastname', '')}".strip(),
            "mail": u.get("mail", ""),
        }
        for u in data.get("users", [])
    ]
    return json.dumps(users, ensure_ascii=False, indent=2)
