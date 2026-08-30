import json
import os
from .cost_model import serving_cost_threshold

CACHE_FILE = "exact_match_cache.json"

# In-memory dictionary for exact match caching
_cache = {}

# Load on module init
if os.path.exists(CACHE_FILE):
    try:
        with open(CACHE_FILE, "r") as f:
            _cache = json.load(f)
    except Exception:
        _cache = {}

def cache_lookup(query: str, profile_name: str) -> dict | None:
    """
    Lite version: Exact match instead of semantic match.
    Returns None on miss (caller should invoke the cascade router).
    """
    query_key = query.strip().lower()
    if query_key in _cache:
        # We always pretend similarity is 1.0 since it's an exact match
        threshold = serving_cost_threshold(profile_name)
        if 1.0 >= threshold:
            meta = _cache[query_key]
            meta["hits"] = meta.get("hits", 0) + 1
            # persist hit count optionally, skipping for speed
            return {
                "response": meta["response"], 
                "similarity": 1.0, # Fake 100% similarity
                "matched_query": meta["query"], 
                "tier_used": meta["tier_used"]
            }
    return None

def cache_store(query: str, response: str, tier_used: str):
    query_key = query.strip().lower()
    _cache[query_key] = {
        "query": query,
        "response": response,
        "tier_used": tier_used,
        "hits": 0
    }
    # Persist to disk so cache survives restarts on free hosts
    try:
        with open(CACHE_FILE, "w") as f:
            json.dump(_cache, f)
    except Exception:
        pass
