"""Fetch all Toggl data script."""

import os
import json
import argparse
from datetime import datetime, timedelta

from toggl_track import TogglClient


def fetch_all_data(client: TogglClient, days: int = 30) -> dict:
    """Fetch all data from Toggl account."""
    
    print("Fetching user data...")
    me = client.me.get(with_related_data=True)
    
    print(f"User: {me.fullname} ({me.email})")
    
    # Get workspaces
    print("Fetching workspaces...")
    workspaces = client.workspaces.list()
    print(f"  Found {len(workspaces)} workspaces")
    
    all_data = {
        "user": {
            "id": me.id,
            "email": me.email,
            "fullname": me.fullname,
            "timezone": me.timezone,
        },
        "workspaces": [],
        "fetched_at": datetime.now().isoformat(),
    }
    
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")
    
    for workspace in workspaces:
        print(f"\nWorkspace: {workspace.name} (ID: {workspace.id})")
        
        ws_data = {
            "id": workspace.id,
            "name": workspace.name,
            "premium": workspace.premium,
        }
        
        # Projects
        print("  Fetching projects...")
        projects = client.projects.list(workspace.id)
        ws_data["projects"] = [
            {
                "id": p.id,
                "name": p.name,
                "client_id": p.client_id,
                "active": p.active,
                "billable": p.billable,
            }
            for p in projects
        ]
        print(f"    {len(projects)} projects")
        
        # Clients
        print("  Fetching clients...")
        clients = client.clients.list(workspace.id)
        ws_data["clients"] = [
            {"id": c.id, "name": c.name}
            for c in clients
        ]
        print(f"    {len(clients)} clients")
        
        # Tags
        print("  Fetching tags...")
        tags = client.tags.list(workspace.id)
        ws_data["tags"] = [
            {"id": t.id, "name": t.name}
            for t in tags
        ]
        print(f"    {len(tags)} tags")
        
        # Time entries
        print(f"  Fetching time entries ({start_str} to {end_str})...")
        entries = client.time_entries.list(
            start_date=start_str,
            end_date=end_str,
            meta=True
        )
        ws_data["time_entries"] = [
            {
                "id": e.id,
                "description": e.description,
                "project_id": e.project_id,
                "project_name": e.project_name,
                "start": e.start,
                "stop": e.stop,
                "duration": e.duration,
                "billable": e.billable,
                "tags": e.tags,
            }
            for e in entries
        ]
        print(f"    {len(entries)} time entries")
        
        all_data["workspaces"].append(ws_data)
    
    return all_data


def main():
    parser = argparse.ArgumentParser(description="Fetch all Toggl data")
    parser.add_argument("--days", type=int, default=30, help="Days of time entries to fetch")
    parser.add_argument("--output", type=str, default="toggl_data.json", help="Output file")
    parser.add_argument("--token", type=str, help="API token (or set TOGGL_API_TOKEN)")
    args = parser.parse_args()
    
    # Get API token
    token = args.token or os.getenv("TOGGL_API_TOKEN")
    if not token:
        print("Error: Please provide --token or set TOGGL_API_TOKEN environment variable")
        return 1
    
    # Create client
    client = TogglClient(api_token=token)
    
    # Test authentication
    if not client.me.check_logged_in():
        print("Error: Authentication failed")
        return 1
    
    # Fetch data
    data = fetch_all_data(client, args.days)
    
    # Save to file
    with open(args.output, "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"\nData saved to {args.output}")
    return 0


if __name__ == "__main__":
    exit(main())
