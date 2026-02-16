"""Base endpoint class."""

from typing import TYPE_CHECKING, Any, Optional, Dict
import logging

if TYPE_CHECKING:
    from ..client import TogglClient

logger = logging.getLogger(__name__)


class BaseEndpoint:
    """Base class for all API endpoints."""
    
    def __init__(self, client: "TogglClient"):
        self.client = client
    
    def _get(self, endpoint: str, params: Optional[Dict] = None) -> Any:
        """Make GET request."""
        return self.client._get(endpoint, params)
    
    def _post(self, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Any:
        """Make POST request."""
        return self.client._post(endpoint, data, params)
    
    def _put(self, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Any:
        """Make PUT request."""
        return self.client._put(endpoint, data, params)
    
    def _patch(self, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Any:
        """Make PATCH request."""
        return self.client._patch(endpoint, data, params)
    
    def _delete(self, endpoint: str, params: Optional[Dict] = None) -> bool:
        """Make DELETE request."""
        return self.client._delete(endpoint, params)
