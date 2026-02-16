"""Clients endpoints."""

from typing import Optional, List
from .base import BaseEndpoint
from ..models import Client
from ..utils import clean_params, validate_workspace_id


class ClientsEndpoint(BaseEndpoint):
    """Endpoints for client management."""
    
    def list(self, workspace_id: int) -> List[Client]:
        """
        Get all clients in a workspace.
        
        Args:
            workspace_id: Workspace ID
            
        Returns:
            List of Client models
        """
        workspace_id = validate_workspace_id(workspace_id)
        
        data = self._get(f"/workspaces/{workspace_id}/clients")
        if isinstance(data, list):
            return [Client.from_dict(item) for item in data]
        return []
    
    def get(self, workspace_id: int, client_id: int) -> Optional[Client]:
        """
        Get a specific client.
        
        Args:
            workspace_id: Workspace ID
            client_id: Client ID
            
        Returns:
            Client model or None if not found
        """
        workspace_id = validate_workspace_id(workspace_id)
        
        try:
            data = self._get(f"/workspaces/{workspace_id}/clients/{client_id}")
            return Client.from_dict(data) if data else None
        except Exception:
            return None
    
    def create(
        self,
        workspace_id: int,
        name: str,
        **kwargs
    ) -> Client:
        """
        Create a new client.
        
        Args:
            workspace_id: Workspace ID
            name: Client name
            **kwargs: Additional fields
            
        Returns:
            Created Client model
        """
        workspace_id = validate_workspace_id(workspace_id)
        
        data = clean_params({"name": name, **kwargs})
        result = self._post(f"/workspaces/{workspace_id}/clients", data)
        return Client.from_dict(result)
    
    def update(
        self,
        workspace_id: int,
        client_id: int,
        **kwargs
    ) -> Client:
        """
        Update a client.
        
        Args:
            workspace_id: Workspace ID
            client_id: Client ID
            **kwargs: Fields to update
            
        Returns:
            Updated Client model
        """
        workspace_id = validate_workspace_id(workspace_id)
        
        result = self._put(f"/workspaces/{workspace_id}/clients/{client_id}", kwargs)
        return Client.from_dict(result)
    
    def delete(self, workspace_id: int, client_id: int) -> bool:
        """
        Delete a client.
        
        Args:
            workspace_id: Workspace ID
            client_id: Client ID
            
        Returns:
            True if deleted successfully
        """
        workspace_id = validate_workspace_id(workspace_id)
        
        return self._delete(f"/workspaces/{workspace_id}/clients/{client_id}")
