#!/usr/bin/env python3
"""
Fetch all Toggl Track data

Usage:
    export TOGGL_API_TOKEN=your_token_here
    python3 fetch_all.py [--days 30] [--output toggl_data.json]
    
    OR
    
    export TOGGL_EMAIL=your@email.com
    export TOGGL_PASSWORD=your_password
    python3 fetch_all.py [--days 30] [--output toggl_data.json]
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone, timedelta

# Import the client
from toggl_client import TogglClient


def format_duration(seconds: int) -> str:
    """Format seconds as HH:MM:SS"""
    if seconds < 0:
        # Running entry - calculate current duration
        seconds = int(datetime.now(timezone.utc).timestamp()) + seconds
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def fetch_all_data(client: TogglClient, days: int = 30) -> dict:
    """Fetch comprehensive Toggl data using with_related_data for efficiency"""
    
    print(f"📊 Fetching all Toggl Track data...")
    print()
    
    data = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "user": None,
        "workspaces": [],
        "time_entries": [],
        "summary": {}
    }
    
    # 1. User info with all related data (efficient single call)
    print("👤 Fetching user info with related data...")
    me = client.get_me(with_related_data=True)
    data["user"] = me
    
    print(f"   ✓ {me.get('fullname', 'Unknown')} ({me.get('email', 'No email')})")
    print(f"   ✓ {len(me.get('workspaces') or [])} workspaces")
    print(f"   ✓ {len(me.get('projects') or [])} projects")
    print(f"   ✓ {len(me.get('clients') or [])} clients")
    print(f"   ✓ {len(me.get('tags') or [])} tags")
    print(f"   ✓ {len(me.get('time_entries') or [])} time entries (from related data)")
    
    # Store related data
    data["workspaces"] = me.get('workspaces') or []
    data["projects"] = me.get('projects') or []
    data["clients"] = me.get('clients') or []
    data["tags"] = me.get('tags') or []
    data["time_entries"] = me.get('time_entries') or []
    
    # 2. Get additional time entries for date range if needed
    if days > 0:
        print(f"\n⏱️  Fetching time entries for last {days} days...")
        end = datetime.now(timezone.utc)
        start = end - timedelta(days=days)
        
        entries = client.get_time_entries(
            start_date=start.strftime("%Y-%m-%d"),
            end_date=end.strftime("%Y-%m-%d"),
            meta=True
        )
        
        print(f"   ✓ {len(entries)} entries found")
        
        # Merge with existing entries (avoid duplicates)
        existing_ids = {e.get('id') for e in data['time_entries']}
        for entry in entries:
            if entry.get('id') not in existing_ids:
                data['time_entries'].append(entry)
    
    # 3. Currently running timer
    print("\n⏲️  Checking for running timer...")
    current = client.get_current_time_entry()
    if current:
        data["current_timer"] = current
        print(f"   ⏱️  Running: {current.get('description', 'No description')}")
    else:
        print("   ✓ No timer running")
    
    # 4. Summary statistics
    print("\n📈 Calculating summary...")
    
    # Calculate total duration
    total_duration = 0
    for entry in data["time_entries"]:
        duration = entry.get("duration", 0)
        if duration > 0:
            total_duration += duration
    
    # Group by project
    project_times = {}
    for entry in data["time_entries"]:
        pid = entry.get("project_id")
        if pid:
            project_times[pid] = project_times.get(pid, 0) + max(0, entry.get("duration", 0))
    
    # Group by date
    daily_times = {}
    for entry in data["time_entries"]:
        start = entry.get("start", "")
        if start:
            date = start[:10]  # YYYY-MM-DD
            duration = entry.get("duration", 0)
            if duration > 0:
                daily_times[date] = daily_times.get(date, 0) + duration
    
    data["summary"] = {
        "total_entries": len(data["time_entries"]),
        "total_duration_seconds": total_duration,
        "total_duration_formatted": format_duration(total_duration),
        "date_range": {
            "start": (datetime.now(timezone.utc) - timedelta(days=days)).isoformat(),
            "end": datetime.now(timezone.utc).isoformat()
        },
        "project_breakdown": {
            str(pid): format_duration(dur) 
            for pid, dur in sorted(project_times.items(), key=lambda x: x[1], reverse=True)[:10]
        },
        "daily_totals": {
            date: format_duration(dur)
            for date, dur in sorted(daily_times.items())
        }
    }
    
    print(f"   ✓ Summary calculated")
    
    return data


def main():
    parser = argparse.ArgumentParser(description="Fetch all Toggl Track data")
    parser.add_argument("--days", type=int, default=30, help="Number of days to fetch (default: 30)")
    parser.add_argument("--output", type=str, default="toggl_data.json", help="Output file (default: toggl_data.json)")
    parser.add_argument("--token", type=str, help="Toggl API token (or set TOGGL_API_TOKEN env var)")
    parser.add_argument("--email", type=str, help="Toggl email (alternative to token)")
    parser.add_argument("--password", type=str, help="Toggl password (alternative to token)")
    
    args = parser.parse_args()
    
    # Get authentication credentials
    token = args.token or os.getenv("TOGGL_API_TOKEN")
    email = args.email or os.getenv("TOGGL_EMAIL")
    password = args.password or os.getenv("TOGGL_PASSWORD")
    
    # Create client with available credentials
    try:
        if token:
            client = TogglClient(api_token=token)
            auth_method = "API Token"
        elif email and password:
            client = TogglClient(email=email, password=password)
            auth_method = "Email/Password"
        else:
            print("❌ Error: Authentication required")
            print("   Provide one of:")
            print("     --token (or TOGGL_API_TOKEN env var)")
            print("     --email + --password (or TOGGL_EMAIL + TOGGL_PASSWORD env vars)")
            print("\n   Get your API token at: https://track.toggl.com/profile")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Error creating client: {e}")
        sys.exit(1)
    
    # Test authentication
    print(f"🔐 Testing authentication ({auth_method})...")
    if not client.check_logged_in():
        print("❌ Authentication failed - check your credentials")
        sys.exit(1)
    print("✓ Authentication successful\n")
    
    # Fetch data
    try:
        data = fetch_all_data(client, days=args.days)
    except Exception as e:
        print(f"\n❌ Error fetching data: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Save to file
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Data saved to: {args.output}")
    print(f"📦 File size: {os.path.getsize(args.output) / 1024:.1f} KB")
    
    # Print summary
    print("\n" + "="*50)
    print("📊 SUMMARY")
    print("="*50)
    print(f"User:        {data['user'].get('fullname', 'Unknown')}")
    print(f"Workspaces:  {len(data['workspaces'])}")
    print(f"Projects:    {len(data.get('projects', []))}")
    print(f"Clients:     {len(data.get('clients', []))}")
    print(f"Tags:        {len(data.get('tags', []))}")
    print(f"Entries:     {data['summary']['total_entries']}")
    print(f"Total time:  {data['summary']['total_duration_formatted']}")
    
    if data.get("current_timer"):
        print(f"\n⏱️  Running timer: {data['current_timer'].get('description', 'No description')}")


if __name__ == "__main__":
    main()
