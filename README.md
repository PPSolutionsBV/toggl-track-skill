# Toggl Track Skill for OpenClaw

Complete Toggl Track API v9 integration for OpenClaw. Fetch time entries, projects, clients, workspaces, tags, and reports.

## Installation

```bash
# Install from GitHub
clawhub install toggl-track --from https://github.com/YOUR_USERNAME/toggl-track-skill

# Or manually
git clone https://github.com/YOUR_USERNAME/toggl-track-skill.git
cp -r toggl-track-skill/toggl-track ~/.openclaw/skills/
```

## Authentication

Three methods supported:

### 1. API Token (Recommended)
Get your token at: https://track.toggl.com/profile

```bash
export TOGGL_API_TOKEN=your_token_here
```

### 2. Email + Password
```bash
export TOGGL_EMAIL=your@email.com
export TOGGL_PASSWORD=your_password
```

### 3. Session Cookie
```python
from toggl_client import TogglClient
session_cookie = TogglClient.create_session("user@example.com", "password")
client = TogglClient(session_cookie=session_cookie)
```

## Quick Start

```python
from toggl_client import TogglClient

# Connect
client = TogglClient(api_token="your_token")

# Get current user
me = client.get_me()
print(f"Hello {me['fullname']}!")

# Get time entries
entries = client.get_time_entries(
    start_date="2024-01-01T00:00:00Z",
    end_date="2024-01-31T23:59:59Z"
)

# Get running timer
current = client.get_current_time_entry()
if current:
    print(f"Currently tracking: {current['description']}")
```

## Fetch All Data

```bash
# Using API token
export TOGGL_API_TOKEN=xxx
python3 scripts/fetch_all.py

# Using email/password
export TOGGL_EMAIL=user@example.com
export TOGGL_PASSWORD=secret
python3 scripts/fetch_all.py

# Custom options
python3 scripts/fetch_all.py --days 7 --output my_data.json
```

## Features

- ✅ User & Session management
- ✅ Workspaces, Projects, Clients, Tags
- ✅ Time entries (with filters)
- ✅ Currently running timer
- ✅ Reports (Summary, Detailed, Weekly)
- ✅ Multiple authentication methods
- ✅ Rate limit handling

## API Coverage

| Endpoint | Method | Status |
|----------|--------|--------|
| /me | GET | ✅ |
| /me/time_entries | GET | ✅ |
| /me/time_entries/current | GET | ✅ |
| /workspaces | GET | ✅ |
| /workspaces/{id}/projects | GET/POST | ✅ |
| /workspaces/{id}/clients | GET/POST | ✅ |
| /workspaces/{id}/tags | GET/POST | ✅ |
| /workspaces/{id}/time_entries | GET/POST | ✅ |
| /reports/api/v3/... | POST | ✅ |

## License

MIT
