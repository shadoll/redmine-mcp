import json
from ..mcp import mcp
from ..client import _get


@mcp.tool()
def search(
    query: str,
    project_id: str = "",
    scope: str = "all",
    issues: bool = True,
    wiki_pages: bool = True,
    news: bool = False,
    documents: bool = False,
    changesets: bool = False,
    messages: bool = False,
    projects: bool = False,
    titles_only: bool = False,
    open_issues: bool = False,
    attachments: bool = False,
    limit: int = 25,
    offset: int = 0,
) -> str:
    """
    Search Redmine by keyword across multiple resource types.

    Args:
        query:        Search keyword(s)
        project_id:   Limit search to a specific project (ID or slug); empty = global
        scope:        "all" (all projects) or "my_projects" (only projects I'm member of)
        issues:       Include issues in results (default True)
        wiki_pages:   Include wiki pages in results (default True)
        news:         Include news in results
        documents:    Include documents in results
        changesets:   Include changesets/commits in results
        messages:     Include forum messages in results
        projects:     Include projects in results
        titles_only:  Search in titles/subjects only (skip descriptions/content)
        open_issues:  Return open issues only
        attachments:  Search inside attachment names/content
        limit:        Max results (1–100, default 25)
        offset:       Pagination offset
    """
    params: dict = {
        "q": query,
        "scope": scope,
        "all_words": 1,
        "titles_only": int(titles_only),
        "open_issues": int(open_issues),
        "attachments": int(attachments),
        "issues": int(issues),
        "wiki_pages": int(wiki_pages),
        "news": int(news),
        "documents": int(documents),
        "changesets": int(changesets),
        "messages": int(messages),
        "projects": int(projects),
        "limit": min(limit, 100),
        "offset": offset,
    }
    if project_id:
        params["project_id"] = project_id

    data = _get("/search.json", params=params)
    results = data.get("results", [])
    total = data.get("total_count", len(results))
    return json.dumps({"total": total, "results": results}, ensure_ascii=False, indent=2)
