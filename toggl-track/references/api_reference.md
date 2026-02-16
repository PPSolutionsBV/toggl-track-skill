# Toggl Track API Reference

Complete reference for Toggl Track API v9 endpoints.

## Base URLs

- **API v9**: `https://api.track.toggl.com/api/v9`
- **Reports API v3**: `https://api.track.toggl.com/reports/api/v3`

## Authentication

All requests require HTTP Basic Auth with your API token:

```bash
curl -u <api_token>:api_token https://api.track.toggl.com/api/v9/me
```

Get your API token at: https://track.toggl.com/profile

## User Endpoints

### GET /me
Get current user details, workspaces, and preferences.

**Response:**
```json
{
  "id": 123456,
  "api_token": "...",
  "email": "user@example.com",
  "fullname": "John Doe",
  "timezone": "Europe/Amsterdam",
  "default_workspace_id": 123,
  "workspaces": [...],
  "projects": [...],
  "tags": [...],
  "clients": [...]
}
```

### GET /me/logged
Check if authentication is working. Returns 200 if valid.

### POST /me/reset_token
Reset API token. Returns new token.

## Workspace Endpoints

### GET /workspaces
List all workspaces for current user.

### GET /workspaces/{workspace_id}
Get workspace details.

### GET /workspaces/{workspace_id}/users
List workspace users (admin required for full list).

### GET /workspaces/{workspace_id}/groups
List workspace groups.

### GET /workspaces/{workspace_id}/tasks
List workspace tasks.

## Project Endpoints

### GET /workspaces/{workspace_id}/projects
List all projects in workspace.

**Query Parameters:**
- `active`: Filter by status (`true`, `false`, or omit for all)
- `since`: Get projects modified since timestamp

### GET /workspaces/{workspace_id}/projects/{project_id}
Get project details.

### POST /workspaces/{workspace_id}/projects
Create new project.

**Request Body:**
```json
{
  "name": "Project Name",
  "client_id": 123,
  "active": true,
  "billable": false,
  "color": "#06aaf5",
  "is_private": false
}
```

### PUT /workspaces/{workspace_id}/projects/{project_id}
Update project.

### DELETE /workspaces/{workspace_id}/projects/{project_id}
Delete project.

## Client Endpoints

### GET /workspaces/{workspace_id}/clients
List all clients in workspace.

### GET /workspaces/{workspace_id}/clients/{client_id}
Get client details.

### POST /workspaces/{workspace_id}/clients
Create new client.

**Request Body:**
```json
{
  "name": "Client Name",
  "wid": 123,
  "notes": "Optional notes"
}
```

## Tag Endpoints

### GET /workspaces/{workspace_id}/tags
List all tags in workspace.

### POST /workspaces/{workspace_id}/tags
Create new tag.

**Request Body:**
```json
{
  "name": "Tag Name"
}
```

## Time Entry Endpoints

### GET /me/time_entries
Get current user's time entries.

**Query Parameters:**
- `start_date`: ISO 8601 datetime (e.g., `2024-01-01T00:00:00Z`)
- `end_date`: ISO 8601 datetime
- `description`: Filter by description text
- `project_ids`: Comma-separated project IDs
- `client_ids`: Comma-separated client IDs
- `tag_ids`: Comma-separated tag IDs
- `billable`: `true` or `false`

### GET /me/time_entries/current
Get currently running time entry (timer).

### GET /workspaces/{workspace_id}/time_entries
Get workspace time entries (admin access required).

### GET /workspaces/{workspace_id}/time_entries/{entry_id}
Get specific time entry.

### POST /workspaces/{workspace_id}/time_entries
Create time entry or start timer.

**Request Body:**
```json
{
  "description": "Working on feature X",
  "project_id": 123,
  "workspace_id": 456,
  "start": "2024-01-15T09:00:00Z",
  "duration": 3600,
  "billable": true,
  "tags": ["development", "urgent"],
  "created_with": "my-app"
}
```

To start a timer, set `duration` to `-1` and omit `stop`.

### PUT /workspaces/{workspace_id}/time_entries/{entry_id}
Update time entry.

### DELETE /workspaces/{workspace_id}/time_entries/{entry_id}
Delete time entry.

### PATCH /workspaces/{workspace_id}/time_entries/{entry_id}/stop
Stop running timer.

## Report Endpoints

All reports use POST with JSON body.

### POST /reports/api/v3/workspace/{workspace_id}/summary/time_entries
Get summary report grouped by project/user.

### POST /reports/api/v3/workspace/{workspace_id}/details/time_entries
Get detailed report with individual entries.

### POST /reports/api/v3/workspace/{workspace_id}/weekly/time_entries
Get weekly report grouped by day.

**Common Report Parameters:**
```json
{
  "start_date": "2024-01-01",
  "end_date": "2024-01-31",
  "description": "optional filter text",
  "project_ids": [123, 456],
  "client_ids": [789],
  "tag_ids": [101, 102],
  "user_ids": [1001, 1002],
  "billable": true,
  "page": 1,
  "per_page": 50
}
```

## Data Types

### Time Entry
```json
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
  "duronly": false,
  "at": "2024-01-15T10:30:00Z",
  "uid": 1001
}
```

### Project
```json
{
  "id": 123,
  "workspace_id": 456,
  "client_id": 789,
  "name": "Project Name",
  "billable": false,
  "is_private": false,
  "active": true,
  "color": "#06aaf5",
  "actual_hours": 100
}
```

### Workspace
```json
{
  "id": 123,
  "name": "My Workspace",
  "profile": 100,
  "premium": true,
  "admin": true,
  "default_hourly_rate": 50,
  "default_currency": "EUR",
  "only_admins_may_create_projects": false,
  "only_admins_see_billable_rates": false,
  "rounding": 1,
  "rounding_minutes": 0
}
```

## Quotas and Limits

### Organization-specific Requests
- **Free**: 30 requests/hour/user/org
- **Starter**: 240 requests/hour/user/org
- **Premium**: 600 requests/hour/user/org

### User-specific Requests
- `/me` endpoints: 30 requests/hour/user

### Rate Limiting
- General: ~1 request/second recommended
- Watch headers: `X-Toggl-Quota-Remaining`, `X-Toggl-Quota-Resets-In`

## Error Codes

| Code | Meaning | Action |
|------|---------|--------|
| 403 | Forbidden | Check authentication |
| 429 | Too Many Requests | Back off and retry |
| 402 | Payment Required | Quota exceeded, wait |
| 410 | Gone | Endpoint deprecated |
| 5xx | Server Error | Retry with delay |

## Time Format

All times use ISO 8601 / RFC 3339 format in UTC:
- Format: `YYYY-MM-DDTHH:MM:SSZ`
- Example: `2024-01-15T09:00:00Z`

Convert to user's timezone using their profile settings.

## Pagination

Reports support pagination:
- `page`: Page number (1-based)
- `per_page`: Items per page (max 1000)

Response includes:
```json
{
  "total_count": 150,
  "per_page": 50,
  "total_grand": 3600000
}
```
