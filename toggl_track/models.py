"""Data models for Toggl Track API responses."""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime


@dataclass
class User:
    """Toggl user model."""
    id: int
    email: str
    fullname: str
    api_token: Optional[str] = None
    default_workspace_id: Optional[int] = None
    timezone: Optional[str] = None
    beginning_of_week: Optional[int] = None
    image_url: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "User":
        return cls(
            id=data.get("id"),
            email=data.get("email", ""),
            fullname=data.get("fullname", ""),
            api_token=data.get("api_token"),
            default_workspace_id=data.get("default_workspace_id"),
            timezone=data.get("timezone"),
            beginning_of_week=data.get("beginning_of_week"),
            image_url=data.get("image_url"),
            created_at=data.get("created_at"),
            updated_at=data.get("at"),
        )


@dataclass
class TimeEntry:
    """Toggl time entry model."""
    id: int
    workspace_id: int
    description: Optional[str] = None
    project_id: Optional[int] = None
    task_id: Optional[int] = None
    user_id: Optional[int] = None
    start: Optional[str] = None
    stop: Optional[str] = None
    duration: int = 0
    billable: bool = False
    tags: List[str] = field(default_factory=list)
    tag_ids: List[int] = field(default_factory=list)
    project_name: Optional[str] = None
    client_name: Optional[str] = None
    task_name: Optional[str] = None
    created_with: Optional[str] = None
    at: Optional[str] = None
    
    @property
    def is_running(self) -> bool:
        """Check if this is a running timer (negative duration)."""
        return self.duration < 0
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TimeEntry":
        return cls(
            id=data.get("id"),
            workspace_id=data.get("workspace_id", data.get("wid", 0)),
            description=data.get("description"),
            project_id=data.get("project_id", data.get("pid")),
            task_id=data.get("task_id", data.get("tid")),
            user_id=data.get("user_id", data.get("uid")),
            start=data.get("start"),
            stop=data.get("stop"),
            duration=data.get("duration", 0),
            billable=data.get("billable", False),
            tags=data.get("tags") or [],
            tag_ids=data.get("tag_ids") or [],
            project_name=data.get("project_name"),
            client_name=data.get("client_name"),
            task_name=data.get("task_name"),
            created_with=data.get("created_with"),
            at=data.get("at"),
        )


@dataclass
class Project:
    """Toggl project model."""
    id: int
    workspace_id: int
    name: str
    client_id: Optional[int] = None
    client_name: Optional[str] = None
    color: Optional[str] = None
    active: bool = True
    billable: Optional[bool] = None
    is_private: bool = True
    rate: Optional[float] = None
    estimated_hours: Optional[int] = None
    actual_hours: Optional[int] = None
    created_at: Optional[str] = None
    at: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Project":
        return cls(
            id=data.get("id"),
            workspace_id=data.get("workspace_id", data.get("wid", 0)),
            name=data.get("name", ""),
            client_id=data.get("client_id", data.get("cid")),
            client_name=data.get("client_name"),
            color=data.get("color"),
            active=data.get("active", True),
            billable=data.get("billable"),
            is_private=data.get("is_private", True),
            rate=data.get("rate"),
            estimated_hours=data.get("estimated_hours"),
            actual_hours=data.get("actual_hours"),
            created_at=data.get("created_at"),
            at=data.get("at"),
        )


@dataclass
class Client:
    """Toggl client model."""
    id: int
    workspace_id: int
    name: str
    archived: bool = False
    at: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Client":
        return cls(
            id=data.get("id"),
            workspace_id=data.get("wid", 0),
            name=data.get("name", ""),
            archived=data.get("archived", False),
            at=data.get("at"),
        )


@dataclass
class Tag:
    """Toggl tag model."""
    id: int
    workspace_id: int
    name: str
    at: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Tag":
        return cls(
            id=data.get("id"),
            workspace_id=data.get("workspace_id", data.get("wid", 0)),
            name=data.get("name", ""),
            at=data.get("at"),
        )


@dataclass
class Workspace:
    """Toggl workspace model."""
    id: int
    name: str
    organization_id: Optional[int] = None
    premium: bool = False
    business_ws: bool = False
    admin: bool = False
    default_hourly_rate: Optional[float] = None
    default_currency: str = "USD"
    projects_billable_by_default: bool = True
    rounding: Optional[int] = None
    rounding_minutes: Optional[int] = None
    at: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Workspace":
        return cls(
            id=data.get("id"),
            name=data.get("name", ""),
            organization_id=data.get("organization_id"),
            premium=data.get("premium", False),
            business_ws=data.get("business_ws", False),
            admin=data.get("admin", False),
            default_hourly_rate=data.get("default_hourly_rate"),
            default_currency=data.get("default_currency", "USD"),
            projects_billable_by_default=data.get("projects_billable_by_default", True),
            rounding=data.get("rounding"),
            rounding_minutes=data.get("rounding_minutes"),
            at=data.get("at"),
        )


@dataclass
class Task:
    """Toggl task model."""
    id: int
    workspace_id: int
    project_id: int
    name: str
    active: bool = True
    estimated_seconds: Optional[int] = None
    tracked_seconds: Optional[int] = None
    at: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        return cls(
            id=data.get("id"),
            workspace_id=data.get("workspace_id", data.get("wid", 0)),
            project_id=data.get("project_id", data.get("pid", 0)),
            name=data.get("name", ""),
            active=data.get("active", True),
            estimated_seconds=data.get("estimated_seconds"),
            tracked_seconds=data.get("tracked_seconds"),
            at=data.get("at"),
        )


@dataclass
class Group:
    """Toggl group model."""
    id: int
    workspace_id: int
    name: str
    at: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Group":
        return cls(
            id=data.get("id"),
            workspace_id=data.get("wid", 0),
            name=data.get("name", ""),
            at=data.get("at"),
        )


@dataclass
class ProjectUser:
    """Toggl project user model."""
    id: int
    project_id: int
    user_id: int
    workspace_id: int
    manager: bool = False
    rate: Optional[float] = None
    labor_cost: Optional[float] = None
    at: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProjectUser":
        return cls(
            id=data.get("id"),
            project_id=data.get("project_id"),
            user_id=data.get("user_id"),
            workspace_id=data.get("workspace_id"),
            manager=data.get("manager", False),
            rate=data.get("rate"),
            labor_cost=data.get("labor_cost"),
            at=data.get("at"),
        )


@dataclass
class WorkspaceUser:
    """Toggl workspace user model."""
    id: int
    user_id: int
    workspace_id: int
    name: str
    email: str
    admin: bool = False
    active: bool = True
    rate: Optional[float] = None
    labor_cost: Optional[float] = None
    group_ids: List[int] = field(default_factory=list)
    at: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkspaceUser":
        return cls(
            id=data.get("id"),
            user_id=data.get("user_id", data.get("uid", 0)),
            workspace_id=data.get("workspace_id", data.get("wid", 0)),
            name=data.get("name", ""),
            email=data.get("email", ""),
            admin=data.get("admin", False),
            active=data.get("active", True),
            rate=data.get("rate"),
            labor_cost=data.get("labor_cost"),
            group_ids=data.get("group_ids") or [],
            at=data.get("at"),
        )


@dataclass
class Report:
    """Toggl report model."""
    total_grand: Optional[int] = None
    total_billable: Optional[int] = None
    total_currencies: List[Dict[str, Any]] = field(default_factory=list)
    items: List[Dict[str, Any]] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Report":
        return cls(
            total_grand=data.get("total_grand"),
            total_billable=data.get("total_billable"),
            total_currencies=data.get("total_currencies") or [],
            items=data.get("items") or data.get("data") or [],
        )


@dataclass
class Webhook:
    """Toggl webhook model."""
    id: int
    workspace_id: int
    url: str
    enabled: bool = True
    event_filters: List[str] = field(default_factory=list)
    created_at: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Webhook":
        return cls(
            id=data.get("id"),
            workspace_id=data.get("workspace_id"),
            url=data.get("url", ""),
            enabled=data.get("enabled", True),
            event_filters=data.get("event_filters") or [],
            created_at=data.get("created_at"),
        )


@dataclass
class Expense:
    """Toggl expense model."""
    id: int
    workspace_id: int
    project_id: Optional[int] = None
    user_id: Optional[int] = None
    description: Optional[str] = None
    amount: float = 0.0
    currency: Optional[str] = None
    date: Optional[str] = None
    at: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Expense":
        return cls(
            id=data.get("id"),
            workspace_id=data.get("workspace_id"),
            project_id=data.get("project_id"),
            user_id=data.get("user_id"),
            description=data.get("description"),
            amount=data.get("amount", 0.0),
            currency=data.get("currency"),
            date=data.get("date"),
            at=data.get("at"),
        )
