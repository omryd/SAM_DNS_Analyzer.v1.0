"""Caching layer for reputation results"""
import time
from typing import Dict, Any, Optional


class ReputationCache:
    def __init__(self, ttl: int = 3600):
        self.cache = {}
        self.ttl = ttl

    async def get(self, domain: str) -> Optional[Dict[str, Any]]:
        """Get cached result for domain"""
        # if the domain is indeed cached (we have already queried for it)
        if domain in self.cache:
            entry = self.cache[domain]
            # if the cached entry hasn't passed the age TTL - return this entry
            if time.time() - entry['timestamp'] < self.ttl:
                return entry['data']
            # delete slate entry from cache
            else:
                # Expired
                del self.cache[domain]
        # returning None in case the domain is not cached
        return None

    async def set(self, domain: str, data: Dict[str, Any]):
        """Cache result for domain"""
        self.cache[domain] = {
            'data': data,
            'timestamp': time.time()
        }

    def clear(self):
        """Clear all cached entries"""
        self.cache.clear()

    def size(self) -> int:
        """Get cache size"""
        return len(self.cache)