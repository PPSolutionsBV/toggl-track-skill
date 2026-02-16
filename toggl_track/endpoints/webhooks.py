"""Webhooks endpoints."""

from typing import Optional, List, Dict, Any
from .base import BaseEndpoint
from ..models import Webhook
from ..utils import clean_params, validate_workspace_id


class WebhooksEndpoint(BaseEndpoint):
    """Endpoints for webhook management."""
    
    def list(
        self,
        workspace_id: int,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
    ) -> List[Webhook]:
        """
        List webhooks in workspace.
        
        Args:
            workspace_id: Workspace ID
            page: Page number
            per_page: Items per page
            
        Returns:
            List of Webhook models
        """
        workspace_id = validate_workspace_id(workspace_id)
        
        params = clean_params({
            "page": page,
            "per_page": per_page,
        })
        
        data = self._get(f"/workspaces/{workspace_id}/webhooks", params)
        if isinstance(data, list):
            return [Webhook.from_dict(item) for item in data]
        return []
    
    def get(self, workspace_id: int, webhook_id: int) -> Optional[Webhook]:
        """
        Get a specific webhook.
        
        Args:
            workspace_id: Workspace ID
            webhook_id: Webhook ID
            
        Returns:
            Webhook model or None if not found
        """
        workspace_id = validate_workspace_id(workspace_id)
        
        try:
            data = self._get(f"/workspaces/{workspace_id}/webhooks/{webhook_id}")
            return Webhook.from_dict(data) if data else None
        except Exception:
            return None
    
    def create(
        self,
        workspace_id: int,
        url: str,
        event_filters: List[str],
        description: Optional[str] = None,
        enabled: bool = True,
        **kwargs
    ) -> Webhook:
        """
        Create a new webhook.
        
        Args:
            workspace_id: Workspace ID
            url: Webhook URL endpoint
            event_filters: List of events to subscribe to
                (time_entry.created, project.created, etc.)
            description: Webhook description
            enabled: Whether webhook is enabled
            **kwargs: Additional fields
            
        Returns:
            Created Webhook model
        """
        workspace_id = validate_workspace_id(workspace_id)
        
        data = clean_params({
            "url": url,
            "event_filters": event_filters,
            "description": description,
            "enabled": enabled,
            **kwargs
        })
        
        result = self._post(f"/workspaces/{workspace_id}/webhooks", data)
        return Webhook.from_dict(result)
    
    def update(
        self,
        workspace_id: int,
        webhook_id: int,
        **kwargs
    ) -> Webhook:
        """
        Update a webhook.
        
        Args:
            workspace_id: Workspace ID
            webhook_id: Webhook ID
            **kwargs: Fields to update
            
        Returns:
            Updated Webhook model
        """
        workspace_id = validate_workspace_id(workspace_id)
        
        result = self._put(f"/workspaces/{workspace_id}/webhooks/{webhook_id}", kwargs)
        return Webhook.from_dict(result)
    
    def delete(self, workspace_id: int, webhook_id: int) -> bool:
        """
        Delete a webhook.
        
        Args:
            workspace_id: Workspace ID
            webhook_id: Webhook ID
            
        Returns:
            True if deleted successfully
        """
        workspace_id = validate_workspace_id(workspace_id)
        
        return self._delete(f"/workspaces/{workspace_id}/webhooks/{webhook_id}")
    
    def ping(self, workspace_id: int, webhook_id: int) -> Dict[str, Any]:
        """
        Send a ping to test webhook.
        
        Args:
            workspace_id: Workspace ID
            webhook_id: Webhook ID
            
        Returns:
            Ping response
        """
        workspace_id = validate_workspace_id(workspace_id)
        
        return self._post(f"/workspaces/{workspace_id}/webhooks/{webhook_id}/ping") or {}
