from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "redmine",
    instructions=(
        "You are connected to a Redmine project management server. "
        "Redmine renders text fields (descriptions, comments, wiki pages) as Markdown. "
        "Always use Markdown syntax for formatting — headings (#), bold (**text**), "
        "italic (*text*), code (`code`), code blocks (```), lists (- item), "
        "and links ([text](url)). Never use HTML tags."
    ),
)
