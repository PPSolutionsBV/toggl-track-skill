"""Reports endpoints."""

from typing import Optional, List, Dict, Any
from .base import BaseEndpoint
from ..models import Report
from ..utils import clean_params, validate_workspace_id, paginated_list


class ReportsEndpoint(BaseEndpoint):
    """Endpoints for reports (Summary, Detailed, Weekly)."""
    
    BASE_URL = "https://api.track.toggl.com/reports/api/v3"
    
    def summary(
        self,
        workspace_id: int,
        start_date: str,
        end_date: str,
        description: Optional[str] = None,
        project_ids: Optional[List[int]] = None,
        client_ids: Optional[List[int]] = None,
        tag_ids: Optional[List[int]] = None,
        user_ids: Optional[List[int]] = None,
        billable: Optional[bool] = None,
    ) -> Report:
        """
        Get summary report.
        
        Args:
            workspace_id: Workspace ID
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            description: Filter by description
            project_ids: Filter by projects
            client_ids: Filter by clients
            tag_ids: Filter by tags
            user_ids: Filter by users
            billable: Filter by billable status
            
        Returns:
            Report model with aggregated data
        """
        workspace_id = validate_workspace_id(workspace_id)
        
        data = clean_params({
            "start_date": start_date,
            "end_date": end_date,
            "description": description,
            "project_ids": project_ids,
            "client_ids": client_ids,
            "tag_ids": tag_ids,
            "user_ids": user_ids,
            "billable": billable,
        })
        
        url = f"{self.BASE_URL}/workspace/{workspace_id}/summary/time_entries"
        result = self._post(url, data)
        return Report.from_dict(result)
    
    def detailed(
        self,
        workspace_id: int,
        start_date: str,
        end_date: str,
        description: Optional[str] = None,
        project_ids: Optional[List[int]] = None,
        client_ids: Optional[List[int]] = None,
        tag_ids: Optional[List[int]] = None,
        user_ids: Optional[List[int]] = None,
        billable: Optional[bool] = None,
        page: int = 1,
        per_page: int = 50,
        auto_paginate: bool = False,
        max_pages: Optional[int] = None,
    ) -> Report:
        """
        Get detailed report with individual time entries.
        
        Args:
            workspace_id: Workspace ID
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            description: Filter by description
            project_ids: Filter by projects
            client_ids: Filter by clients
            tag_ids: Filter by tags
            user_ids: Filter by users
            billable: Filter by billable status
            page: Page number
            per_page: Items per page
            auto_paginate: Fetch all pages automatically
            max_pages: Max pages when auto_paginate=True
            
        Returns:
            Report model with detailed entries
        """
        workspace_id = validate_workspace_id(workspace_id)
        
        data = clean_params({
            "start_date": start_date,
            "end_date": end_date,
            "description": description,
            "project_ids": project_ids,
            "client_ids": client_ids,
            "tag_ids": tag_ids,
            "user_ids": user_ids,
            "billable": billable,
        })
        
        url = f"{self.BASE_URL}/workspace/{workspace_id}/details/time_entries"
        
        def fetch_page(p: int, pp: int):
            page_data = {**data, "page": p, "per_page": pp}
            return self._post(url, page_data)
        
        if auto_paginate:
            result = paginated_list(fetch_page, page, per_page, True, max_pages)
            return Report(items=result.items)
        else:
            result = fetch_page(page, per_page)
            return Report.from_dict(result)
    
    def weekly(
        self,
        workspace_id: int,
        start_date: str,
        end_date: str,
        description: Optional[str] = None,
        project_ids: Optional[List[int]] = None,
        client_ids: Optional[List[int]] = None,
        tag_ids: Optional[List[int]] = None,
        user_ids: Optional[List[int]] = None,
        billable: Optional[bool] = None,
    ) -> Report:
        """
        Get weekly report grouped by day.
        
        Args:
            workspace_id: Workspace ID
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            description: Filter by description
            project_ids: Filter by projects
            client_ids: Filter by clients
            tag_ids: Filter by tags
            user_ids: Filter by users
            billable: Filter by billable status
            
        Returns:
            Report model with weekly data
        """
        workspace_id = validate_workspace_id(workspace_id)
        
        data = clean_params({
            "start_date": start_date,
            "end_date": end_date,
            "description": description,
            "project_ids": project_ids,
            "client_ids": client_ids,
            "tag_ids": tag_ids,
            "user_ids": user_ids,
            "billable": billable,
        })
        
        url = f"{self.BASE_URL}/workspace/{workspace_id}/weekly/time_entries"
        result = self._post(url, data)
        return Report.from_dict(result)
