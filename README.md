# Toggl Track Skill for OpenClaw

Complete Toggl Track API v9 integration for OpenClaw.

## Features

- ✅ **Complete API Coverage**: Time entries, projects, clients, tags, workspaces, tasks, groups, organizations, reports, webhooks, expenses
- ✅ **Pagination Support**: Automatic pagination for large datasets
- ✅ **Rate Limiting**: Respects API quotas and rate limits
- ✅ **Type Hints**: Full typing support with dataclass models
- ✅ **Error Handling**: Comprehensive exception hierarchy
- ✅ **Bulk Operations**: Patch multiple time entries at once

## Installation

```bash
clawhub install toggl-track --from https://github.com/PPSolutionsBV/toggl-track-skill
```

Or manually:
```bash
git clone https://github.com/PPSolutionsBV/toggl-track-skill.git
cp -r toggl-track-skill/toggl_track ~/.openclaw/skills/
```

## Quick Start

```python
from toggl_track import TogglClient

client = TogglClient(api_token="your_token")

# Get current user
me = client.me.get()
print(f"Hello {me.fullname}!")

# List time entries
entries = client.time_entries.list(
    start_date="2024-01-01",
    end_date="2024-01-31"
)

# Start a timer
timer = client.time_entries.start(
    workspace_id=123,
    description="Working on project"
)
```

## Authentication

Get your API token at: https://track.toggl.com/profile

```bash
export TOGGL_API_TOKEN=your_token_here
```

## Documentation

See [SKILL.md](SKILL.md) for complete API documentation.

## License

MIT
