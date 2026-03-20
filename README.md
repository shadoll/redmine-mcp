# Redmine MCP Server

Exposes Redmine REST API as tools for Claude Code via MCP (Model Context Protocol).

## Available tools

| Tool | Description |
|------|-------------|
| `get_issue` | Get issue details by ID |
| `get_issue_statuses` | List all available statuses (use to find status IDs) |
| `update_issue_status` | Change issue status |
| `update_issue_progress` | Set % done (0–100) |
| `get_issue_comments` | Get all comments and field changes |
| `add_issue_comment` | Post a new comment |
| `assign_issue` | Assign issue to a user |
| `get_project_members` | List project members with user IDs |
| `list_issues` | Query issues with filters (project, status, assignee) |
| `update_issue` | Update title, description, priority, due date |

## Setup

### 1. Get your Redmine API key

1. Log in to your Redmine instance
2. Go to **My account** (top-right avatar menu)
3. Scroll to **API access key** on the right side
4. Click **Show** — copy the key

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env`:
```
REDMINE_URL=https://your.redmine.com
REDMINE_API_KEY=your_personal_api_key_here
```

### 3. Run the container

```bash
docker compose up -d
# or with podman:
podman-compose up -d
```

The server will be available at `http://localhost:8765`.

### 4. Register with Claude Code

```bash
claude mcp add --scope user --transport http redmine http://localhost:8765/mcp
```

Verify it was added:
```bash
claude mcp list
```

## Usage examples

Once registered, just ask Claude naturally in any project:

> "Get issue #1234"
> "Change status of issue #1234 to In Progress"
> "Add a comment to issue #1234: deployment done"
> "Who is assigned to issue #1234?"
> "List open issues in project api-service assigned to me"
