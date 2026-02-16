# Toggl Track Skill

## Beschrijving

Complete Toggl Track API integratie voor tijdregistratie, projecten, rapporten en meer.

## Installatie

```bash
git clone https://github.com/PPSolutionsBV/toggl-track-skill.git /tmp/toggl-track
cp -r /tmp/toggl-track/toggl_track ~/.openclaw/skills/
```

## Gebruik

### Basis gebruik

```python
from toggl_track import TogglClient

client = TogglClient(api_token="jouw_token")
```

### Authenticatie

Set environment variable:
```bash
export TOGGL_API_TOKEN=ef84e82078bd84b40e15e8da92d55524
```

Of gebruik direct in code:
```python
client = TogglClient(api_token="ef84e82078bd84b40e15e8da92d55524")
```

### Time Entries

```python
# Lijst ophalen (laatste 7 dagen)
from datetime import datetime, timedelta
end = datetime.now()
start = end - timedelta(days=7)

entries = client.time_entries.list(
    start_date=start.strftime("%Y-%m-%d"),
    end_date=end.strftime("%Y-%m-%d")
)

# Huidige timer
current = client.time_entries.current()

# Timer starten
client.time_entries.start(
    workspace_id=5784952,
    description="Werk aan project",
    project_id=123456
)

# Timer stoppen
if current:
    client.time_entries.stop(current.workspace_id, current.id)
```

### Projecten

```python
# Alle projecten
projects = client.projects.list(workspace_id=5784952)

# Met auto-pagination (alle pagina's)
projects = client.projects.list(
    workspace_id=5784952,
    auto_paginate=True
)
```

### Rapporten

```python
# Summary report
report = client.reports.summary(
    workspace_id=5784952,
    start_date="2026-02-01",
    end_date="2026-02-17"
)

# Detailed report
report = client.reports.detailed(
    workspace_id=5784952,
    start_date="2026-02-01",
    end_date="2026-02-17",
    auto_paginate=True
)
```

### Workspaces

```python
workspaces = client.workspaces.list()
workspace = client.workspaces.get(5784952)
```

### Clients & Tags

```python
clients = client.clients.list(workspace_id=5784952)
tags = client.tags.list(workspace_id=5784952)
```

## API Token

Workspace: PP Solutions Toggl (ID: 5784952)
Token: `ef84e82078bd84b40e15e8da92d55524`

## Beschikbare Endpoints

- `client.me` - Gebruiker info
- `client.time_entries` - Tijdregistraties
- `client.projects` - Projecten
- `client.project_users` - Project gebruikers
- `client.clients` - Klanten
- `client.tags` - Tags
- `client.workspaces` - Workspaces
- `client.workspace_users` - Workspace gebruikers
- `client.tasks` - Taken
- `client.groups` - Groepen
- `client.organizations` - Organisaties
- `client.reports` - Rapporten (summary, detailed, weekly)
- `client.webhooks` - Webhooks
- `client.expenses` - Onkosten

## Voorbeelden

### Wat heb ik vandaag gedaan?

```python
from datetime import datetime
from toggl_track import TogglClient

client = TogglClient()
today = datetime.now().strftime("%Y-%m-%d")

entries = client.time_entries.list(
    start_date=today,
    end_date=today,
    meta=True
)

for e in entries:
    print(f"{e.description} - {e.duration/60:.0f} min")
```

### Totaal uren deze week

```python
from datetime import datetime, timedelta
from toggl_track import TogglClient

client = TogglClient()
end = datetime.now()
start = end - timedelta(days=7)

entries = client.time_entries.list(
    start_date=start.strftime("%Y-%m-%d"),
    end_date=end.strftime("%Y-%m-%d")
)

total = sum(e.duration for e in entries if e.duration > 0)
print(f"Totaal: {total/3600:.2f} uur")
```

## Error Handling

```python
from toggl_track import TogglClient, TogglAuthError, TogglRateLimitError

try:
    client = TogglClient()
except TogglAuthError:
    print("Ongeldige credentials")
except TogglRateLimitError as e:
    print(f"Rate limit, wacht {e.retry_after} seconden")
```
