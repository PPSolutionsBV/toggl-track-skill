"""Input validation utilities."""

from typing import Optional, List, Any
from datetime import datetime


def validate_date_format(date_str: str) -> bool:
    """Validate date string format (YYYY-MM-DD or RFC3339)."""
    if not date_str:
        return True
    
    # Try YYYY-MM-DD
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        pass
    
    # Try RFC3339 (simplified check)
    if "T" in date_str:
        return True
    
    return False


def validate_required(value: Any, name: str) -> None:
    """Validate that a required value is present."""
    if value is None or value == "":
        raise ValueError(f"{name} is required")


def validate_workspace_id(workspace_id: Optional[int]) -> int:
    """Validate and return workspace ID."""
    if workspace_id is None:
        raise ValueError("workspace_id is required")
    if not isinstance(workspace_id, int) or workspace_id <= 0:
        raise ValueError("workspace_id must be a positive integer")
    return workspace_id


def validate_project_id(project_id: Optional[int]) -> int:
    """Validate and return project ID."""
    if project_id is None:
        raise ValueError("project_id is required")
    if not isinstance(project_id, int) or project_id <= 0:
        raise ValueError("project_id must be a positive integer")
    return project_id


def validate_time_entry_id(time_entry_id: Optional[int]) -> int:
    """Validate and return time entry ID."""
    if time_entry_id is None:
        raise ValueError("time_entry_id is required")
    if not isinstance(time_entry_id, int) or time_entry_id <= 0:
        raise ValueError("time_entry_id must be a positive integer")
    return time_entry_id


def validate_duration(duration: int) -> None:
    """Validate time entry duration."""
    if duration == 0:
        raise ValueError("duration cannot be 0")
    # Negative duration is valid for running entries


def validate_tags(tags: Optional[List[str]]) -> List[str]:
    """Validate and normalize tags."""
    if tags is None:
        return []
    if not isinstance(tags, list):
        raise ValueError("tags must be a list")
    return [str(tag).strip() for tag in tags if tag]


def clean_params(params: dict) -> dict:
    """Remove None values from params dict."""
    return {k: v for k, v in params.items() if v is not None}
