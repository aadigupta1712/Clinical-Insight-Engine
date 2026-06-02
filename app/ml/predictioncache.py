import hashlib
import json
from collections import OrderedDict
import time

class LRUPredictionCache:
    def __init__(self, max_size=1000, ttl_seconds=300):  # 5 min TTL
        self.cache = OrderedDict()
        self.max_size = max_size
        self.ttl = ttl_seconds

    def _make_key(self, params: dict) -> str:
        # Sort keys so order doesn't matter
        serialized = json.dumps(params, sort_keys=True)
        return hashlib.sha256(serialized.encode()).hexdigest()

    def get(self, params: dict):
        key = self._make_key(params)
        if key not in self.cache:
            return None
        value, timestamp = self.cache[key]
        if time.time() - timestamp > self.ttl:
            del self.cache[key]
            return None
        # Move to end (most recently used)
        self.cache.move_to_end(key)
        return value

    def set(self, params: dict, result):
        key = self._make_key(params)
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = (result, time.time())
        if len(self.cache) > self.max_size:
            self.cache.popitem(last=False)  # evict least recently used

# Singleton instance
prediction_cache = LRUPredictionCache()
