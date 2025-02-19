# tldw_tube/api/dependencies.py
import time
from fastapi import Request, HTTPException, status
from core.config import settings
from typing import Dict
from functools import wraps

# Rate limiting (simplified, in-memory; use Redis in production)
def rate_limit(limit: int = settings.rate_limit_count, period: int = settings.rate_limit_period):
    requests: Dict[str, list] = {}

    def decorator(f):
        @wraps(f)
        async def wrapped(request: Request, *args, **kwargs):
            now = time.time()
            ip = request.client.host

            # Clean old entries
            requests.setdefault(ip, [])
            requests[ip] = [t for t in requests[ip] if now - t < period]

            if len(requests[ip]) >= limit:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded. Please try again later."
                )
            requests[ip].append(now)
            return await f(request, *args, **kwargs)
        return wrapped
    return decorator
