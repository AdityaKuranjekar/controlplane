import json
import os
import hashlib
from .cost_model import serving_cost_threshold

CACHE_FILE = "exact_match_cache.json"

# In-memory dictionary for compound match caching
_cache = {}

# Load on module init
if os.path.exists(CACHE_FILE):
    try:
        with open(CACHE_FILE, "r") as f:
            _cache = json.load(f)
    except Exception:
        _cache = {}

def generate_compound_key(query: str, profile_name: str = "customer_bot", context_chunks: list[str] | None = None) -> str:
    """
    Computes a compound SHA-256 hash:
    Key = SHA256(profile || prompt || rag_context)
    """
    ctx_str = "::".join(c.strip() for c in context_chunks) if context_chunks else ""
    raw = f"{profile_name.strip().lower()}:{query.strip().lower()}:{ctx_str}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]

def cache_lookup(query: str, profile_name: str = "customer_bot", context_chunks: list[str] | None = None) -> dict | None:
    """
    Compound cache lookup preventing collisions between identical prompts with differing contexts/profiles.
    """
    compound_key = generate_compound_key(query, profile_name, context_chunks)
    if compound_key in _cache:
        threshold = serving_cost_threshold(profile_name)
        if 1.0 >= threshold:
            meta = _cache[compound_key]
            meta["hits"] = meta.get("hits", 0) + 1
            return {
                "response": meta["response"], 
                "similarity": 1.0,
                "matched_query": meta.get("query", query), 
                "tier_used": meta.get("tier_used", "tier0"),
                "action": meta.get("action", "ALLOW"),
            }
    return None

def cache_store(query: str, response: str, tier_used: str, profile_name: str = "customer_bot", context_chunks: list[str] | None = None, action: str = "ALLOW"):
    compound_key = generate_compound_key(query, profile_name, context_chunks)
    _cache[compound_key] = {
        "query": query,
        "profile": profile_name,
        "context_chunks": context_chunks or [],
        "response": response,
        "tier_used": tier_used,
        "action": action,
        "hits": 0
    }
    try:
        with open(CACHE_FILE, "w") as f:
            json.dump(_cache, f)
    except Exception:
        pass

