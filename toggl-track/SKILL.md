---
name: toggl-track
description: Complete Toggl Track time tracking integration. Use when the user wants to retrieve, create, update, or manage time entries, projects, clients, workspaces, tags, or reports from Toggl Track. Handles authentication via API token, email/password, or session cookie. Fetches all data types including running timers, and supports both personal and workspace-level queries.
---

# Toggl Track Skill

This skill provides comprehensive access to the Toggl Track API v9 for time tracking data retrieval and management.

## Authentication

The Toggl Track API supports multiple authentication methods:

### Method 1: API Token (Recommended for Scripts)

Get your API token at: https://track.toggl.com/profile

```bash
curl -u <api_token>:api_token https://api.track.toggl.com/api/v9/me
```

Environment variable: `TOGGL_API_TOKEN`

### Method 2: Email + Password

```bash
curl -u <email>:<password> https://api.track.toggl.com/api/v9/me
```

Environment variables: `TOGGL_EMAIL` and `TOGGL_PASSWORD`

### Method 3: Session Cookie

Create a session first:

```bash
curl -i 'https://accounts.toggl.com/api/sessions' \
  -X POST \
  -d '{"email":"<your-email>","password":"<your-password>"}' \
  -H 'Content-Type: application/json'
```

Use the `__Secure-accounts-session` cookie in subsequent requests.

### Python Client Usage

```python
from toggl_client import TogglClient

# Method 1: API Token
client = TogglClient(api_token="your_token_here")

# Method 2: Email/Password
client = TogglClient(email="user@example.com", password="secret")

# Method 3: Create session from credentials
session_cookie = TogglClient.create_session("user@example.com", "password")
client = TogglClient(session_cookie=session_cookie)
```

## Base URL

```
https://api.track.toggl.com/api/v9
```

## Core Endpoints

### User & Session

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/me` | GET | Current user details |
| `/me?with_related_data=true` | GET | User + all related data (workspaces, projects, clients, tags, tasks, time_entries) |
| `/me/logged` | GET | Check if authenticated |
| `/me/reset_token` | POST | Reset API token |

### Workspaces

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/workspaces` | GET | List all workspaces |
| `/workspaces/{workspace_id}` | GET | Workspace details |
| `/workspaces/{workspace_id}/users` | GET | Workspace users |
| `/workspaces/{workspace_id}/groups` | GET | Workspace groups |
| `/workspaces/{workspace_id}/tasks` | GET | Workspace tasks |

### Projects

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/workspaces/{workspace_id}/projects` | GET | List projects |
| `/workspaces/{workspace_id}/projects/{project_id}` | GET | Project details |
| `/workspaces/{workspace_id}/project_users` | GET | Project users |

### Clients

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/workspaces/{workspace_id}/clients` | GET | List clients |
| `/workspaces/{workspace_id}/clients/{client_id}` | GET | Client details |

### Tags

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/workspaces/{workspace_id}/tags` | GET | List tags |

### Time Entries

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/me/time_entries` | GET | Current user's time entries (returns `{items: [...]}`) |
| `/me/time_entries/{id}` | GET | Get time entry by ID |
| `/me/time_entries/current` | GET | Currently running timer |
| `/workspaces/{workspace_id}/time_entries` | POST | Create time entry |
| `/workspaces/{workspace_id}/time_entries/{id}` | PUT | Update time entry |
| `/workspaces/{workspace_id}/time_entries/{ids}` | PATCH | Bulk patch time entries |
| `/workspaces/{workspace_id}/time_entries/{id}` | DELETE | Delete time entry |

### Reports

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/reports/api/v3/workspace/{workspace_id}/summary/time_entries` | POST | Summary report |
| `/reports/api/v3/workspace/{workspace_id}/details/time_entries` | POST | Detailed report |
| `/reports/api/v3/workspace/{workspace_id}/weekly/time_entries` | POST | Weekly report |

## Query Parameters

### GET /me

- `with_related_data`: Include all related entities (clients, projects, tags, tasks, workspaces, time_entries)

### GET /me/time_entries

Returns a **list** of time entries directly (not wrapped in a dict).

- `start_date`: Start date (YYYY-MM-DD or RFC3339)
- `end_date`: End date (YYYY-MM-DD or RFC3339)
- `since`: Unix timestamp to get entries modified since (includes deleted)
- `before`: Get entries before this date
- `meta`: Include meta entity data (client_name, project_name, etc.)
- `include_sharing`: Include sharing details

### GET /workspaces/{id}/projects

- `active`: Filter by status (`true`, `false`)
- `since`: Unix timestamp to get projects modified since

### POST /workspaces/{id}/time_entries (Create)

**Important fields:**
- `workspace_id`: Required
- `description`: Time entry description
- `duration`: Duration in seconds. **For running entries: `-1 * (Unix timestamp)`**
- `start`: Start time (ISO 8601)
- `stop`: Stop time (ISO 8601), omit for running entries
- `project_id`: Project ID
- `task_id`: Task ID
- `tags`: List of tag names
- `tag_ids`: List of tag IDs
- `billable`: Whether billable
- `created_with`: Client identifier (required)

**Legacy fields (still supported):**
- `pid`: project_id
- `tid`: task_id  
- `wid`: workspace_id
- `uid`: user_id
- `duronly`: Deprecated but still used

## Response Formats

### Time Entries Response

```json
{
  "items": [
    {
      "id": 123456789,
      "workspace_id": 123,
      "project_id": 456,
      "task_id": null,
      "billable": false,
      "start": "2024-01-15T09:00:00Z",
      "stop": "2024-01-15T10:30:00Z",
      "duration": 5400,
      "description": "Working on feature",
      "tags": ["development"],
      "tag_ids": [789],
      "client_name": "Client Name",
      "project_name": "Project Name",
      "user_name": "User Name"
    }
  ]
}
```

### Running Timer

For running entries:
- `duration` is negative: `-1 * (Unix timestamp of start time)`
- `stop` is null

Example:
```json
{
  "duration": -1705312800,
  "stop": null,
  "start": "2024-01-15T09:00:00Z"
}
```

## API Quotas & Rate Limits

- **Organization requests**: 30-600/hour depending on plan
- **User requests**: 30/hour for `/me` endpoints
- **Rate limit**: ~1 request/second recommended
- Watch headers: `X-Toggl-Quota-Remaining`, `X-Toggl-Quota-Resets-In`

## Scripts

Use the provided scripts for common operations:

- `scripts/toggl_client.py` - Python client with all API methods
- `scripts/fetch_all.py` - Fetch all data using with_related_data

## Common Workflows

### Get Current User with All Data
```python
me = client.get_me(with_related_data=True)
# Returns: user + workspaces + projects + clients + tags + tasks + time_entries
```

### Get Time Entries (Correct Way)
```python
entries = client.get_time_entries(start_date="2024-01-01", end_date="2024-01-31")
# Returns a list directly!
for entry in entries:
    print(f"{entry['description']} - {entry.get('project_name', 'No project')}")
```

### Start a Running Timer
```python
# Duration is calculated automatically as -1 * Unix timestamp
entry = client.start_time_entry(
    workspace_id=123,
    description="Working on feature",
    project_id=456
)
```

### Get Currently Running Timer
```python
current = client.get_current_time_entry()
if current:
    print(f"Running: {current['description']}")
```

## Error Handling

- `403`: Authentication failed
- `429`: Rate limit exceeded - back off
- `402`: Quota exceeded - wait for reset
- `410`: Endpoint deprecated - don't retry
- `5xx`: Server error - retry with delay

## References

For complete API details, see [references/api_reference.md](references/api_reference.md)
