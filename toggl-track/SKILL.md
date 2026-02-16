---
name: toggl-track
description: Complete Toggl Track time tracking integration. Use when the user wants to retrieve, create, update, or manage time entries, projects, clients, workspaces, tags, or reports from Toggl Track. Handles authentication via API token, fetches all data types including running timers, and supports both personal and workspace-level queries.
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
| `/me` | GET | Current user details, workspaces, preferences |
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
| `/me/time_entries` | GET | Current user's time entries |
| `/me/time_entries/current` | GET | Currently running timer |
| `/workspaces/{workspace_id}/time_entries` | GET | Workspace time entries |
| `/workspaces/{workspace_id}/time_entries/{entry_id}` | GET/PUT/DELETE | Single entry operations |

### Reports

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/reports/api/v3/workspace/{workspace_id}/summary/time_entries` | POST | Summary report |
| `/reports/api/v3/workspace/{workspace_id}/details/time_entries` | POST | Detailed report |
| `/reports/api/v3/workspace/{workspace_id}/weekly/time_entries` | POST | Weekly report |

## Query Parameters

### Time Entries

- `start_date` / `end_date`: ISO 8601 format (e.g., `2024-01-01T00:00:00Z`)
- `description`: Filter by description text
- `project_ids`: Comma-separated project IDs
- `client_ids`: Comma-separated client IDs
- `tag_ids`: Comma-separated tag IDs
- `billable`: `true` or `false`

### Reports

All reports use POST with JSON body:

```json
{
  "start_date": "2024-01-01",
  "end_date": "2024-01-31",
  "description": "optional filter",
  "project_ids": [123, 456],
  "client_ids": [789],
  "tag_ids": [101, 102],
  "billable": true
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
- `scripts/fetch_all.py` - Fetch all data (workspaces, projects, entries)

## Common Workflows

### Get Current User Info
```bash
curl -u $TOGGL_API_TOKEN:api_token https://api.track.toggl.com/api/v9/me
```

### Get Time Entries for Date Range
```bash
curl -u $TOGGL_API_TOKEN:api_token \
  "https://api.track.toggl.com/api/v9/me/time_entries?start_date=2024-01-01T00:00:00Z&end_date=2024-01-31T23:59:59Z"
```

### Get Currently Running Timer
```bash
curl -u $TOGGL_API_TOKEN:api_token \
  https://api.track.toggl.com/api/v9/me/time_entries/current
```

### Get Workspace Projects
```bash
curl -u $TOGGL_API_TOKEN:api_token \
  https://api.track.toggl.com/api/v9/workspaces/{workspace_id}/projects
```

## Error Handling

- `403`: Authentication failed
- `429`: Rate limit exceeded - back off
- `402`: Quota exceeded - wait for reset
- `410`: Endpoint deprecated - don't retry
- `5xx`: Server error - retry with delay

## References

For complete API details, see [references/api_reference.md](references/api_reference.md)
