"""Expenses endpoints."""

from typing import Optional, List, Dict, Any
from .base import BaseEndpoint
from ..models import Expense
from ..utils import clean_params, validate_workspace_id


class ExpensesEndpoint(BaseEndpoint):
    """Endpoints for expense management."""
    
    def list(
        self,
        workspace_id: int,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        project_ids: Optional[List[int]] = None,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
    ) -> List[Expense]:
        """
        List expenses in workspace.
        
        Args:
            workspace_id: Workspace ID
            start_date: Filter by start date (YYYY-MM-DD)
            end_date: Filter by end date (YYYY-MM-DD)
            project_ids: Filter by project IDs
            page: Page number
            per_page: Items per page
            
        Returns:
            List of Expense models
        """
        workspace_id = validate_workspace_id(workspace_id)
        
        params = clean_params({
            "start_date": start_date,
            "end_date": end_date,
            "project_ids": ",".join(map(str, project_ids)) if project_ids else None,
            "page": page,
            "per_page": per_page,
        })
        
        data = self._get(f"/workspaces/{workspace_id}/expenses", params)
        if isinstance(data, list):
            return [Expense.from_dict(item) for item in data]
        return []
    
    def get(self, workspace_id: int, expense_id: int) -> Optional[Expense]:
        """
        Get a specific expense.
        
        Args:
            workspace_id: Workspace ID
            expense_id: Expense ID
            
        Returns:
            Expense model or None if not found
        """
        workspace_id = validate_workspace_id(workspace_id)
        
        try:
            data = self._get(f"/workspaces/{workspace_id}/expenses/{expense_id}")
            return Expense.from_dict(data) if data else None
        except Exception:
            return None
    
    def create(
        self,
        workspace_id: int,
        amount: float,
        date: str,
        description: Optional[str] = None,
        project_id: Optional[int] = None,
        currency: Optional[str] = None,
        billable: bool = True,
        **kwargs
    ) -> Expense:
        """
        Create a new expense.
        
        Args:
            workspace_id: Workspace ID
            amount: Expense amount
            date: Expense date (YYYY-MM-DD)
            description: Expense description
            project_id: Associated project ID
            currency: Currency code
            billable: Whether expense is billable
            **kwargs: Additional fields
            
        Returns:
            Created Expense model
        """
        workspace_id = validate_workspace_id(workspace_id)
        
        data = clean_params({
            "amount": amount,
            "date": date,
            "description": description,
            "project_id": project_id,
            "currency": currency,
            "billable": billable,
            **kwargs
        })
        
        result = self._post(f"/workspaces/{workspace_id}/expenses", data)
        return Expense.from_dict(result)
    
    def update(
        self,
        workspace_id: int,
        expense_id: int,
        **kwargs
    ) -> Expense:
        """
        Update an expense.
        
        Args:
            workspace_id: Workspace ID
            expense_id: Expense ID
            **kwargs: Fields to update
            
        Returns:
            Updated Expense model
        """
        workspace_id = validate_workspace_id(workspace_id)
        
        result = self._put(f"/workspaces/{workspace_id}/expenses/{expense_id}", kwargs)
        return Expense.from_dict(result)
    
    def delete(self, workspace_id: int, expense_id: int) -> bool:
        """
        Delete an expense.
        
        Args:
            workspace_id: Workspace ID
            expense_id: Expense ID
            
        Returns:
            True if deleted successfully
        """
        workspace_id = validate_workspace_id(workspace_id)
        
        return self._delete(f"/workspaces/{workspace_id}/expenses/{expense_id}")
