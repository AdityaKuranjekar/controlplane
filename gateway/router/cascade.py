import groq
from gateway.llm.groq_client import complete_sync
from .scorer import reliability_score
from .tiers import TIERS

async def run_cascade(messages: list[dict]) -> dict:
    """
    Walks tiers in order; accepts the first answer whose reliability score
    clears that tier's threshold. Returns which tier was used (for cost accounting).
    """
    for i, tier in enumerate(TIERS):
        is_last_tier = (i == len(TIERS) - 1)
        try:
            answer = await complete_sync(messages, model=tier["model"])
        except groq.BadRequestError as e:
            if is_last_tier:
                raise
            continue
        
        score = reliability_score(answer)
        if score >= tier["accept_threshold"] or is_last_tier:
            return {"answer": answer, "tier_used": tier["name"], "score": score,
                     "escalated": i > 0}
    # unreachable given is_last_tier guard, but keep for safety
    raise RuntimeError("cascade exhausted without acceptance")
