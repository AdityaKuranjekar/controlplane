# L1 simplification: c(q) is a fixed calibrated constant per profile,
# standing in for the paper's learned, query-specific serving cost.
# Upgrade path: L4 replaces this with CUCB-SC (offline) / CLCB-SC-LS (online) bandit estimates.

PROFILE_CACHE_THRESHOLDS = {
    "customer_bot": 0.88,     # aggressive caching: high repetition, low individual stakes
    "internal_rag": 0.94,     # conservative: wrong cached fact is costlier here
    "decision_agent": 1.01,   # effectively never cache (>max cosine sim) — every agent turn is fresh
}

def serving_cost_threshold(profile_name: str) -> float:
    return PROFILE_CACHE_THRESHOLDS.get(profile_name, 0.90)
