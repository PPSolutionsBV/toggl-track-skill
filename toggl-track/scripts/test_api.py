#!/usr/bin/env python3
"""Test script voor Toggl Track API"""

import os
import sys

# Voeg het scripts pad toe
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from toggl_client import TogglClient

def test_connection():
    """Test basic connection"""
    token = os.getenv("TOGGL_API_TOKEN")
    if not token:
        print("❌ TOGGL_API_TOKEN niet gezet")
        sys.exit(1)
    
    print(f"🔐 Token gevonden: {token[:8]}...")
    
    try:
        client = TogglClient(api_token=token)
        print("✓ Client aangemaakt")
    except Exception as e:
        print(f"❌ Client error: {e}")
        sys.exit(1)
    
    # Test auth
    print("\n🔐 Test authenticatie...")
    if client.check_logged_in():
        print("✓ Authenticatie OK")
    else:
        print("❌ Authenticatie mislukt")
        sys.exit(1)
    
    # Test get_me
    print("\n👤 Test get_me()...")
    try:
        me = client.get_me()
        print(f"✓ User: {me.get('fullname', 'Unknown')} ({me.get('email', 'No email')})")
        print(f"  ID: {me.get('id')}")
        print(f"  Default workspace: {me.get('default_workspace_id')}")
    except Exception as e:
        print(f"❌ get_me error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test get_me with related data
    print("\n👤 Test get_me(with_related_data=True)...")
    try:
        me_full = client.get_me(with_related_data=True)
        print(f"✓ Workspaces: {len(me_full.get('workspaces') or [])}")
        print(f"✓ Projects: {len(me_full.get('projects') or [])}")
        print(f"✓ Clients: {len(me_full.get('clients') or [])}")
        print(f"✓ Tags: {len(me_full.get('tags') or [])}")
        print(f"✓ Time entries: {len(me_full.get('time_entries') or [])}")
    except Exception as e:
        print(f"❌ get_me(with_related_data) error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test get_time_entries
    print("\n⏱️  Test get_time_entries()...")
    try:
        entries = client.get_time_entries()
        print(f"✓ Response type: {type(entries)}")
        
        if isinstance(entries, list):
            print(f"✓ Aantal entries: {len(entries)}")
            
            if entries:
                print("\n  Eerste entry:")
                entry = entries[0]
                print(f"    ID: {entry.get('id')}")
                print(f"    Description: {entry.get('description')}")
                print(f"    Duration: {entry.get('duration')}")
                print(f"    Start: {entry.get('start')}")
        else:
            print(f"⚠️  Unexpected response format: {entries}")
    except Exception as e:
        print(f"❌ get_time_entries error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test current timer
    print("\n⏲️  Test get_current_time_entry()...")
    try:
        current = client.get_current_time_entry()
        if current:
            print(f"✓ Running timer: {current.get('description', 'No description')}")
        else:
            print("✓ Geen running timer")
    except Exception as e:
        print(f"❌ get_current_time_entry error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n✅ Test voltooid!")

if __name__ == "__main__":
    test_connection()
