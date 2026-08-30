import re

REFUSAL_MARKERS = [
    "i cannot", "i can't", "i don't have access", "i'm not able to",
    "as an ai", "i don't know", "unable to determine",
]
HEDGE_MARKERS = ["might be", "possibly", "i'm not sure", "it could be", "perhaps"]

def reliability_score(answer: str) -> float:
    """
    Heuristic v0 reliability score in [0,1]. Higher = more likely acceptable.
    Upgrade path: L3/L4 replaces this with a trained regression head
    (DistilBERT-style, per FrugalGPT) once labeled (query,answer,correct) data exists.
    """
    a = answer.lower().strip()
    if len(a) < 3:
        return 0.1
    score = 1.0
    if any(m in a for m in REFUSAL_MARKERS):
        score -= 0.5
    hedge_hits = sum(1 for m in HEDGE_MARKERS if m in a)
    score -= 0.15 * hedge_hits
    if len(a.split()) < 3:
        score -= 0.2
    return max(0.0, min(1.0, score))
