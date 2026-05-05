"""
Rate limiting middleware implementation.

Tracks requests per client IP and enforces limits on expensive operations.
"""

import time
import logging
from collections import defaultdict
from fastapi import Request
from fastapi.responses import JSONResponse

from app.core import RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW

logger = logging.getLogger(__name__)

# In-memory store of request timestamps per client IP
_request_log: dict[str, list[float]] = defaultdict(list)


def check_rate_limit(client_ip: str) -> tuple[bool, int]:
    """
    Check if client has exceeded rate limit.
    
    Args:
        client_ip: The client's IP address.
    
    Returns:
        Tuple of (is_allowed, remaining_requests).
        is_allowed: True if request is within limit.
        remaining_requests: Number of requests still available in window.
    """
    now = time.time()
    window_start = now - RATE_LIMIT_WINDOW
    
    # Clean old requests outside the window
    _request_log[client_ip] = [t for t in _request_log[client_ip] if t > window_start]
    
    # Check if limit exceeded
    if len(_request_log[client_ip]) >= RATE_LIMIT_REQUESTS:
        return False, 0
    
    # Record this request
    _request_log[client_ip].append(now)
    remaining = RATE_LIMIT_REQUESTS - len(_request_log[client_ip])
    return True, remaining


async def rate_limit_middleware(request: Request, call_next):
    """
    Apply rate limiting to expensive operations.
    
    Only limits /ask and /upload-pdf endpoints per client IP.
    
    Args:
        request: The incoming HTTP request.
        call_next: Next middleware/handler in the chain.
    
    Returns:
        Response or 429 Too Many Requests if limit exceeded.
    """
    # Only rate limit expensive operations
    if request.url.path in ["/ask", "/upload-pdf"]:
        client_ip = request.client.host if request.client else "unknown"
        is_allowed, remaining = check_rate_limit(client_ip)
        
        if not is_allowed:
            logger.warning("Rate limit exceeded for client: %s", client_ip)
            return JSONResponse(
                status_code=429,
                content={
                    "detail": f"Rate limit exceeded. Maximum {RATE_LIMIT_REQUESTS} "
                             f"requests per {RATE_LIMIT_WINDOW} seconds."
                }
            )
    
    return await call_next(request)
