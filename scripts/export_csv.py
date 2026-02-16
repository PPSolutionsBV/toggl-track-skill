#!/usr/bin/env python3
"""Export Toggl Track time entries to CSV.

This script exports time entries to a CSV file with various formatting options.
"""

import argparse
import csv
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from toggl_track import TogglClient


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Export Toggl Track time entries to CSV"
    )
    parser.add_argument(
        "--token",
        required=True,
        help="Toggl API token"
    )
    parser.add_argument(
        "--output",
        default="toggl_export.csv",
        help="Output CSV file path (default: toggl_export.csv)"
    )
    parser.add_argument(
        "--start-date",
        required=True,
        help="Start date (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--end-date",
        required=True,
        help="End date (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--workspace-id",
        type=int,
        help="Filter by workspace ID"
    )
    parser.add_argument(
        "--project-id",
        type=int,
        help="Filter by project ID"
    )
    parser.add_argument(
        "--include-running",
        action="store_true",
        help="Include currently running time entries"
    )
    parser.add_argument(
        "--format",
        choices=["detailed", "simple", "summary"],
        default="detailed",
        help="Export format (default: detailed)"
    )
    return parser.parse_args()


def format_duration(seconds: int) -> str:
    """Format duration in seconds to HH:MM:SS.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    if seconds < 0:
        return "Running"
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def format_duration_decimal(seconds: int) -> str:
    """Format duration in seconds to decimal hours.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Duration in decimal hours (e.g., 1.5 for 1:30)
    """
    if seconds < 0:
        return "Running"
    
    return f"{seconds / 3600:.2f}"


def parse_datetime(dt_str: str) -> datetime:
    """Parse ISO datetime string.
    
    Args:
        dt_str: ISO format datetime string
        
    Returns:
        Parsed datetime
    """
    if dt_str.endswith("Z"):
        dt_str = dt_str[:-1] + "+00:00"
    
    try:
        return datetime.fromisoformat(dt_str)
    except ValueError:
        # Try alternative formats
        for fmt in ["%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"]:
            try:
                return datetime.strptime(dt_str[:19], fmt)
            except ValueError:
                continue
        raise


def export_detailed(client: TogglClient, entries: list, output_path: Path):
    """Export entries in detailed format.
    
    Args:
        client: TogglClient instance
        entries: List of time entries
        output_path: Output file path
    """
    fieldnames = [
        "id",
        "description",
        "start_date",
        "start_time",
        "end_date",
        "end_time",
        "duration",
        "duration_decimal",
        "project",
        "project_id",
        "client",
        "client_id",
        "task",
        "task_id",
        "tags",
        "billable",
        "workspace",
        "workspace_id",
    ]
    
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for entry in entries:
            # Handle both model objects and dicts
            if hasattr(entry, 'id'):
                te_id = entry.id
                description = entry.description or ""
                start = entry.start
                stop = entry.stop
                duration = entry.duration
                project = entry.project_name or ""
                project_id = entry.project_id
                client = entry.client_name or ""
                task = entry.task_name or ""
                task_id = entry.task_id
                tags = ", ".join(entry.tags) if entry.tags else ""
                billable = "Yes" if entry.billable else "No"
                workspace_id = entry.workspace_id
            else:
                te_id = entry.get("id")
                description = entry.get("description", "")
                start = entry.get("start")
                stop = entry.get("stop")
                duration = entry.get("duration", 0)
                project = entry.get("project_name", "")
                project_id = entry.get("project_id")
                client = entry.get("client_name", "")
                task = entry.get("task_name", "")
                task_id = entry.get("task_id")
                tags = ", ".join(entry.get("tags", []))
                billable = "Yes" if entry.get("billable") else "No"
                workspace_id = entry.get("workspace_id")
            
            # Parse dates
            try:
                start_dt = parse_datetime(start) if start else None
                start_date = start_dt.strftime("%Y-%m-%d") if start_dt else ""
                start_time = start_dt.strftime("%H:%M:%S") if start_dt else ""
            except:
                start_date = ""
                start_time = start or ""
            
            try:
                stop_dt = parse_datetime(stop) if stop else None
                end_date = stop_dt.strftime("%Y-%m-%d") if stop_dt else ""
                end_time = stop_dt.strftime("%H:%M:%S") if stop_dt else ""
            except:
                end_date = ""
                end_time = stop or ""
            
            # Get workspace name
            workspace = ""
            if workspace_id:
                try:
                    ws = client.workspaces.get(workspace_id)
                    workspace = ws.name if ws else ""
                except:
                    pass
            
            writer.writerow({
                "id": te_id,
                "description": description,
                "start_date": start_date,
                "start_time": start_time,
                "end_date": end_date,
                "end_time": end_time,
                "duration": format_duration(duration),
                "duration_decimal": format_duration_decimal(duration),
                "project": project,
                "project_id": project_id or "",
                "client": client,
                "client_id": "",  # Not directly available in time entry
                "task": task,
                "task_id": task_id or "",
                "tags": tags,
                "billable": billable,
                "workspace": workspace,
                "workspace_id": workspace_id or "",
            })


def export_simple(client: TogglClient, entries: list, output_path: Path):
    """Export entries in simple format.
    
    Args:
        client: TogglClient instance
        entries: List of time entries
        output_path: Output file path
    """
    fieldnames = ["date", "project", "description", "duration", "billable"]
    
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for entry in entries:
            if hasattr(entry, 'id'):
                start = entry.start
                project = entry.project_name or ""
                description = entry.description or ""
                duration = format_duration(entry.duration)
                billable = "Yes" if entry.billable else "No"
            else:
                start = entry.get("start", "")
                project = entry.get("project_name", "")
                description = entry.get("description", "")
                duration = format_duration(entry.get("duration", 0))
                billable = "Yes" if entry.get("billable") else "No"
            
            try:
                start_dt = parse_datetime(start) if start else None
                date = start_dt.strftime("%Y-%m-%d") if start_dt else ""
            except:
                date = ""
            
            writer.writerow({
                "date": date,
                "project": project,
                "description": description,
                "duration": duration,
                "billable": billable,
            })


def export_summary(client: TogglClient, entries: list, output_path: Path):
    """Export entries in summary format (grouped by project).
    
    Args:
        client: TogglClient instance
        entries: List of time entries
        output_path: Output file path
    """
    from collections import defaultdict
    
    # Group by project
    project_data = defaultdict(lambda: {"duration": 0, "entries": 0, "billable_duration": 0})
    
    for entry in entries:
        if hasattr(entry, 'id'):
            project = entry.project_name or "No Project"
            duration = entry.duration if entry.duration > 0 else 0
            billable = entry.billable
        else:
            project = entry.get("project_name") or "No Project"
            dur = entry.get("duration", 0)
            duration = dur if dur > 0 else 0
            billable = entry.get("billable", False)
        
        project_data[project]["duration"] += duration
        project_data[project]["entries"] += 1
        if billable:
            project_data[project]["billable_duration"] += duration
    
    fieldnames = ["project", "entries", "total_duration", "total_hours", "billable_duration", "billable_hours"]
    
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for project, data in sorted(project_data.items()):
            writer.writerow({
                "project": project,
                "entries": data["entries"],
                "total_duration": format_duration(data["duration"]),
                "total_hours": format_duration_decimal(data["duration"]),
                "billable_duration": format_duration(data["billable_duration"]),
                "billable_hours": format_duration_decimal(data["billable_duration"]),
            })


def main():
    """Main entry point."""
    args = parse_args()
    
    # Initialize client
    client = TogglClient(api_token=args.token)
    
    # Fetch time entries
    print(f"Fetching time entries from {args.start_date} to {args.end_date}...")
    
    try:
        entries = client.me.time_entries.list(
            start_date=args.start_date,
            end_date=args.end_date,
            auto_paginate=True
        )
    except Exception as e:
        print(f"Error fetching time entries: {e}")
        sys.exit(1)
    
    # Filter entries
    filtered_entries = []
    for entry in entries:
        if hasattr(entry, 'id'):
            # Filter by workspace
            if args.workspace_id and entry.workspace_id != args.workspace_id:
                continue
            # Filter by project
            if args.project_id and entry.project_id != args.project_id:
                continue
            # Filter running entries
            if not args.include_running and entry.duration < 0:
                continue
        else:
            # Filter by workspace
            if args.workspace_id and entry.get("workspace_id") != args.workspace_id:
                continue
            # Filter by project
            if args.project_id and entry.get("project_id") != args.project_id:
                continue
            # Filter running entries
            if not args.include_running and entry.get("duration", 0) < 0:
                continue
        
        filtered_entries.append(entry)
    
    print(f"Found {len(filtered_entries)} time entries")
    
    # Export
    output_path = Path(args.output)
    
    if args.format == "detailed":
        export_detailed(client, filtered_entries, output_path)
    elif args.format == "simple":
        export_simple(client, filtered_entries, output_path)
    elif args.format == "summary":
        export_summary(client, filtered_entries, output_path)
    
    print(f"Exported to: {output_path.absolute()}")
    
    # Check quota
    quota = client.get_quota_remaining()
    if quota is not None:
        print(f"API quota remaining: {quota}")


if __name__ == "__main__":
    main()
