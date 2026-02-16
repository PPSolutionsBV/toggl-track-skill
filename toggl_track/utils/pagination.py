"""Pagination utilities for Toggl API."""

from typing import Iterator, TypeVar, Callable, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

T = TypeVar("T")


class PaginatedResult:
    """Wrapper for paginated API results."""
    
    def __init__(
        self,
        items: list,
        total_count: Optional[int] = None,
        page: int = 1,
        per_page: int = 50,
        has_more: bool = False
    ):
        self.items = items
        self.total_count = total_count
        self.page = page
        self.per_page = per_page
        self.has_more = has_more
    
    def __iter__(self):
        return iter(self.items)
    
    def __len__(self):
        return len(self.items)
    
    def __getitem__(self, index):
        return self.items[index]


def auto_paginate(
    fetch_func: Callable[[int, int], Dict[str, Any]],
    page: int = 1,
    per_page: int = 50,
    max_pages: Optional[int] = None,
    items_key: str = "items"
) -> Iterator[Dict[str, Any]]:
    """
    Automatically paginate through all results.
    
    Args:
        fetch_func: Function that takes (page, per_page) and returns response dict
        page: Starting page number
        per_page: Items per page
        max_pages: Maximum number of pages to fetch (None for all)
        items_key: Key in response dict containing the items list
    
    Yields:
        Individual items from each page
    """
    current_page = page
    pages_fetched = 0
    
    while True:
        if max_pages and pages_fetched >= max_pages:
            logger.debug(f"Reached max_pages limit ({max_pages})")
            break
        
        response = fetch_func(current_page, per_page)
        
        if not response:
            break
        
        items = response.get(items_key, [])
        if not items:
            break
        
        for item in items:
            yield item
        
        pages_fetched += 1
        
        # Check if there are more pages
        total_count = response.get("total_count")
        if total_count is not None:
            # Calculate if we've fetched all items
            fetched_count = current_page * per_page
            if fetched_count >= total_count:
                break
        
        # Some APIs use has_more flag
        if not response.get("has_more", True):
            break
        
        current_page += 1


def paginated_list(
    fetch_func: Callable[[int, int], Dict[str, Any]],
    page: int = 1,
    per_page: int = 50,
    auto_fetch: bool = False,
    max_pages: Optional[int] = None,
    items_key: str = "items"
) -> PaginatedResult:
    """
    Get a paginated list of results.
    
    Args:
        fetch_func: Function that takes (page, per_page) and returns response dict
        page: Page number to fetch
        per_page: Items per page
        auto_fetch: If True, fetch all pages and combine
        max_pages: Maximum pages when auto_fetch=True
        items_key: Key in response dict containing the items list
    
    Returns:
        PaginatedResult with items and pagination info
    """
    if auto_fetch:
        all_items = list(auto_paginate(fetch_func, page, per_page, max_pages, items_key))
        return PaginatedResult(
            items=all_items,
            total_count=len(all_items),
            page=page,
            per_page=per_page,
            has_more=False
        )
    
    response = fetch_func(page, per_page)
    items = response.get(items_key, [])
    total_count = response.get("total_count")
    
    # Determine if there are more pages
    has_more = False
    if total_count is not None:
        has_more = (page * per_page) < total_count
    elif len(items) == per_page:
        has_more = True
    
    return PaginatedResult(
        items=items,
        total_count=total_count,
        page=page,
        per_page=per_page,
        has_more=has_more
    )
