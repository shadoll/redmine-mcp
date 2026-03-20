import json
from ..mcp import mcp
from ..client import _get


@mcp.tool()
def get_issue_statuses() -> str:
    """
    Get all available issue statuses in Redmine.
    Use this to find the correct status_id before calling update_issue_status.
    """
    data = _get("/issue_statuses.json")
    return json.dumps(data["issue_statuses"], ensure_ascii=False, indent=2)
