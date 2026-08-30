from .segmenter import StreamingSegmenter
from .nli_model import contradiction_score

class GroundingGate:
    """
    Wraps a StreamingSegmenter; as each sentence commits, scores it against
    the top-k context chunks and returns the max contradiction score
    (i.e. worst-case: is this claim contradicted by ANY chunk we retrieved,
    or unsupported by ALL of them).
    """
    def __init__(self, context_chunks: list[str], threshold: float):
        self.segmenter = StreamingSegmenter()
        self.context_chunks = context_chunks
        self.threshold = threshold
        self.claim_results: list[dict] = []

    def feed_token(self, token: str) -> list[dict]:
        newly_committed = self.segmenter.feed(token)
        return [self._score_sentence(s) for s in newly_committed]

    def finalize(self) -> dict | None:
        tail = self.segmenter.flush()
        return self._score_sentence(tail) if tail else None

    def _score_sentence(self, sentence: str) -> dict:
        if not self.context_chunks:
            result = {"sentence": sentence, "score": None, "flagged": False, "best_chunk": None}
        else:
            scores = [(contradiction_score(chunk, sentence), chunk) for chunk in self.context_chunks]
            best_score, best_chunk = max(scores, key=lambda x: x[0])
            result = {
                "sentence": sentence, "score": round(best_score, 4),
                "flagged": best_score >= self.threshold,
                "best_chunk": best_chunk[:120],  # truncate for logging
            }
        self.claim_results.append(result)
        return result

    def grounding_risk(self) -> float:
        """Aggregate risk_vector.grounding value: fraction of flagged sentences, or 0 if none scored."""
        scored = [r for r in self.claim_results if r["score"] is not None]
        if not scored:
            return 0.0
        return sum(1 for r in scored if r["flagged"]) / len(scored)
