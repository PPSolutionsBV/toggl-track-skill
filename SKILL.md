# Toggl Track Skill for OpenClaw

Complete Toggl Track API v9 integration for OpenClaw. Production-ready client with full API coverage.

## Features

- ✅ **Complete API Coverage**: Time entries, projects, clients, tags, workspaces, tasks, reports
- ✅ **Pagination Support**: Automatic pagination for large datasets
- ✅ **Rate Limiting**: Respects API quotas and rate limits
- ✅ **Type Hints**: Full typing support with dataclass models
- ✅ **Error Handling**: Comprehensive exception hierarchy
- ✅ **Bulk Operations**: Patch multiple time entries at once

## Installation

```bash
# Copy to OpenClaw skills directory
cp -r toggl-track-complete ~/.openclaw/skills/toggl-track

# Or install via clawhub (when published)
clawhub install toggl-track
```

## Authentication

Get your API token at: https://track.toggl.com/profile

### Method 1: Environment Variable (Recommended)
```bash
export TOGGL_API_TOKEN=your_token_here
```

### Method 2: Direct
```python
from toggl_track import TogglClient
client = TogglClient(api_token="your_token")
```

## Quick Start

```python
from toggl_track import TogglClient

# Connect
client = TogglClient()

# Get current user
me = client.me.get()
print(f"Hello {me.fullname}!")

# List workspaces
workspaces = client.workspaces.list()
for ws in workspaces:
    print(f"Workspace: {ws.name}")

# Get time entries
entries = client.time_entries.list(
    start_date="2024-01-01",
    end_date="2024-01-31"
)

# Start a timer
timer = client.time_entries.start(
    workspace_id=123,
    description="Working on project",
    project_id=456
)

# Stop current timer
current = client.time_entries.current()
if current:
    client.time_entries.stop(current.workspace_id, current.id)
```

## API Reference

### Time Entries

```python
# List entries
entries = client.time_entries.list(
    start_date="2024-01-01",
    end_date="2024-01-31",
    meta=True  # Include project/client names
)

# Get current running timer
current = client.time_entries.current()

# Create entry
entry = client.time_entries.create(
    workspace_id=123,
    description="Meeting",
    duration=3600,
    start="2024-01-15T10:00:00Z"
)

# Start timer
entry = client.time_entries.start(
    workspace_id=123,
    description="Working",
    project_id=456,
    tags=["important"]
)

# Stop timer
entry = client.time_entries.stop(workspace_id, entry_id)

# Update entry
entry = client.time_entries.update(
    workspace_id,
    entry_id,
    description="Updated description"
)

# Delete entry
client.time_entries.delete(workspace_id, entry_id)

# Bulk patch (max 100)
result = client.time_entries.patch(
    workspace_id=123,
    time_entry_ids=[1, 2, 3],
    operations=[
        {"op": "replace", "path": "/description", "value": "New desc"}
    ]
)
```

### Projects

```python
# List with pagination
projects = client.projects.list(
    workspace_id=123,
    active=True,
    page=1,
    per_page=50,
    auto_paginate=True  # Fetch all pages
)

# Create
project = client.projects.create(
    workspace_id=123,
    name="New Project",
    client_id=456,
    color="#06aaf5"
)

# Update
project = client.projects.update(
    workspace_id,
    project_id,
    name="Updated Name"
)

# Delete
client.projects.delete(workspace_id, project_id)
```

### Project Users

```python
# List users
users = client.project_users.list(workspace_id=123)

# Add user
pu = client.project_users.add(
    workspace_id=123,
    project_id=456,
    user_id=789,
    manager=True
)

# Update
pu = client.project_users.update(
    workspace_id,
    project_user_id,
    manager=False
)

# Remove
client.project_users.delete(workspace_id, project_user_id)
```

### Reports

```python
# Summary report
report = client.reports.summary(
    workspace_id=123,
    start_date="2024-01-01",
    end_date="2024-01-31"
)

# Detailed report with pagination
report = client.reports.detailed(
    workspace_id=123,
    start_date="2024-01-01",
    end_date="2024-01-31",
    auto_paginate=True
)

# Weekly report
report = client.reports.weekly(
    workspace_id=123,
    start_date="2024-01-01",
    end_date="2024-01-31"
)
```

### Workspaces

```python
# List
workspaces = client.workspaces.list()

# Get
workspace = client.workspaces.get(workspace_id)

# Update
workspace = client.workspaces.update(
    workspace_id,
    name="New Name"
)

# List users
users = client.workspace_users.list(
    organization_id=123,
    workspace_id=456,
    auto_paginate=True
)

# Groups
groups = client.workspaces.groups(workspace_id)
```

### Clients

```python
# List
clients = client.clients.list(workspace_id)

# Create
client_obj = client.clients.create(workspace_id, name="Client Name")

# Update
client.clients.update(workspace_id, client_id, name="New Name")

# Delete
client.clients.delete(workspace_id, client_id)
```

### Tags

```python
# List
tags = client.tags.list(workspace_id)

# Create
tag = client.tags.create(workspace_id, name="urgent")

# Update
client.tags.update(workspace_id, tag_id, name="high-priority")

# Delete
client.tags.delete(workspace_id, tag_id)
```

### Tasks

```python
# List
tasks = client.tasks.list(workspace_id, project_id=123)

# Create
task = client.tasks.create(
    workspace_id,
    project_id=123,
    name="New Task",
    estimated_seconds=3600
)

# Update
client.tasks.update(workspace_id, task_id, name="Updated")

# Delete
client.tasks.delete(workspace_id, task_id)
```

## Error Handling

```python
from toggl_track import (
    TogglClient,
    TogglAuthError,
    TogglRateLimitError,
    TogglQuotaError,
    TogglNotFoundError,
)

client = TogglClient()

try:
    entry = client.time_entries.get(99999)
except TogglAuthError:
    print("Invalid credentials")
except TogglRateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after} seconds")
except TogglQuotaError as e:
    print(f"Quota exceeded. Resets in {e.quota_resets_in} seconds")
except TogglNotFoundError:
    print("Time entry not found")
```

## Scripts

### Fetch All Data
```bash
export TOGGL_API_TOKEN=xxx
python scripts/fetch_all.py --days 30 --output data.json
```

## Models

All API responses are parsed into typed dataclasses:

- `User` - User account info
- `TimeEntry` - Time tracking entry
- `Project` - Project details
- `Client` - Client information
- `Tag` - Tag details
- `Workspace` - Workspace settings
- `Task` - Task information
- `ProjectUser` - Project membership
- `WorkspaceUser` - Workspace membership
- `Report` - Report data

## Rate Limits

The client automatically handles:
- **Request rate**: 1 request per second (configurable)
- **Quota headers**: Respects X-Toggl-Quota-Remaining
- **Retry-After**: Waits when rate limited (429)

## License

MIT
