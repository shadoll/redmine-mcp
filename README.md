# Redmine MCP Server

Exposes Redmine REST API as tools for Claude Code via MCP (Model Context Protocol).

## Available tools

**Issues**

| Tool | Description |
|------|-------------|
| `create_issue` | Create a new issue (supports subtask, watchers, relations) |
| `get_issue` | Get issue details by ID |
| `list_issues` | Query issues with filters (project, status, assignee) |
| `update_issue` | Update title, description, priority, due date, subtask, watchers, relations |
| `update_issue_status` | Change issue status |
| `update_issue_progress` | Set % done (0–100) |

**Comments & members**

| Tool | Description |
|------|-------------|
| `get_issue_comments` | Get all comments and field changes |
| `add_issue_comment` | Post a new comment |
| `assign_issue` | Assign issue to a user |
| `get_project_members` | List project members with user IDs |
| `get_issue_statuses` | List all available statuses (use to find status IDs) |

**Relations & watchers**

| Tool | Description |
|------|-------------|
| `get_issue_relations` | List all relations for an issue |
| `add_issue_relation` | Add a relation between two issues |
| `remove_issue_relation` | Remove a relation by relation ID |
| `add_watcher` | Add a watcher to an issue |
| `remove_watcher` | Remove a watcher from an issue |

**Search**

| Tool | Description |
|------|-------------|
| `search` | Search by keyword across issues, wiki, news, documents, and more |

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

# Optional: enable Bearer token auth for remote access
# MCP_AUTH_TOKEN=your_secret_token_here
```

### 3. Run the container

The image is published automatically to `ghcr.io/shadoll/redmine-mcp:latest` on every push to `main`.

```bash
docker compose up -d
# or with podman:
podman-compose up -d
```

The server will be available at `http://localhost:8765`.

### 4. Register with Claude Code

```bash
# Without auth:
claude mcp add --scope user --transport http redmine http://localhost:8765/mcp

# With Bearer token auth:
claude mcp add --scope user --transport http redmine http://localhost:8765/mcp \
  --header "Authorization: Bearer your_secret_token_here"
```

Verify it was added:
```bash
claude mcp list
```

## Kubernetes / k3s

### Quick start

**1. Install Helm** (if not already installed):
```bash
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

**2. Install the chart:**
```bash
helm install redmine-mcp ./helm \
  --set redmine.url=https://your.redmine.com \
  --set redmine.apiKey=your_api_key \
  --set auth.token=your_secret_token_here  # optional
```

**3. Register with Claude Code** (using port-forward):
```bash
kubectl port-forward svc/redmine-mcp 8000:8000
claude mcp add --scope user --transport http redmine http://localhost:8000/mcp
```

---

### Expose via NodePort (access without port-forward)

```bash
helm install redmine-mcp ./helm \
  --set redmine.url=https://your.redmine.com \
  --set redmine.apiKey=your_api_key \
  --set service.type=NodePort
```

Then find the assigned port:
```bash
kubectl get svc redmine-mcp
```

Register:
```bash
claude mcp add --scope user --transport http redmine http://<node-ip>:<node-port>/mcp
```

---

### Use an existing Kubernetes Secret

```bash
kubectl create secret generic redmine-credentials \
  --from-literal=REDMINE_URL=https://your.redmine.com \
  --from-literal=REDMINE_API_KEY=your_api_key

helm install redmine-mcp ./helm \
  --set redmine.existingSecret=redmine-credentials
```

---

### Upgrade / uninstall

```bash
# Upgrade
helm upgrade redmine-mcp ./helm --reuse-values

# Uninstall
helm uninstall redmine-mcp
```

## Usage examples

Once registered, just ask Claude naturally in any project:

> "Create a new issue in project api-service: Fix login timeout"
> "Get issue #1234"
> "Search for issues related to login bug"
> "Change status of issue #1234 to In Progress"
> "Add a comment to issue #1234: deployment done"
> "Who is assigned to issue #1234?"
> "List open issues in project api-service assigned to me"
