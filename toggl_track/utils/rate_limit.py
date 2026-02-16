"""Rate limiting and quota handling utilities."""

import time
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)


class RateLimiter:
    """Handles API rate limiting and quota management."""
    
    # Default rate limit: 1 request per second
    DEFAULT_RATE_LIMIT = 1.0
    
    def __init__(self, requests_per_second: float = 1.0):
        self.min_interval = 1.0 / requests_per_second
        self.last_request_time: Optional[float] = None
        self.quota_remaining: Optional[int] = None
        self.quota_resets_in: Optional[int] = None
    
    def wait_if_needed(self):
        """Wait if we need to respect rate limits."""
        if self.last_request_time is not None:
            elapsed = time.time() - self.last_request_time
            if elapsed < self.min_interval:
                sleep_time = self.min_interval - elapsed
                logger.debug(f"Rate limiting: sleeping {sleep_time:.2f}s")
                time.sleep(sleep_time)
        self.last_request_time = time.time()
    
    def update_from_headers(self, headers: Dict[str, str]):
        """Update rate limit info from response headers."""
        # Quota headers
        quota_remaining = headers.get("X-Toggl-Quota-Remaining")
        if quota_remaining:
            self.quota_remaining = int(quota_remaining)
        
        quota_resets = headers.get("X-Toggl-Quota-Resets-In")
        if quota_resets:
            self.quota_resets_in = int(quota_resets)
        
        # Log warnings for low quota
        if self.quota_remaining is not None and self.quota_remaining < 10:
            logger.warning(f"Low API quota: {self.quota_remaining} requests remaining")
    
    def check_quota(self) -> bool:
        """Check if we have quota remaining."""
        if self.quota_remaining is None:
            return True
        return self.quota_remaining > 0
    
    def get_retry_after(self, headers: Dict[str, str]) -> Optional[int]:
        """Get retry-after value from headers."""
        retry_after = headers.get("Retry-After")
        if retry_after:
            return int(retry_after)
        return None
