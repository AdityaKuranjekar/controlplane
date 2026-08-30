from .embeddings import embed
from .vector_store import VectorStore
from .cost_model import serving_cost_threshold

_store = VectorStore()

def cache_lookup(query: str, profile_name: str) -> dict | None:
    """
    Implements: serve from cache iff mismatch_cost <= serving_cost_threshold
    i.e. iff cosine_similarity >= threshold  (since higher sim == lower mismatch)
    Returns None on miss (caller should invoke the cascade router).
    """
    vec = embed(query)
    sims, ids = _store.search(vec, k=1)
    if len(sims) == 0:
        return None

    best_sim, best_id = float(sims[0]), int(ids[0])
    threshold = serving_cost_threshold(profile_name)

    if best_sim >= threshold:
        meta = _store.get_meta(best_id)
        if meta:
            _store.bump_hits(best_id)
            return {"response": meta["response"], "similarity": best_sim,
                     "matched_query": meta["query"], "tier_used": meta["tier_used"]}
    return None

def cache_store(query: str, response: str, tier_used: str):
    vec = embed(query)
    _store.add(vec, query, response, tier_used)
    _store.persist()  # fsync to disk so cache survives restarts on free hosts
