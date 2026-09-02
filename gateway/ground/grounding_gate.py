from .segmenter import StreamingSegmenter
from .nli_model import contradiction_score, entailment_score

class GroundingGate:
    """
    Wraps a StreamingSegmenter; as each sentence commits, scores it against
    the top-k context chunks using two signals:

    1. Contradiction score  — is this claim contradicted by context? (hallucination)
    2. Evasion score        — does the full response fail to entail ANY context claim?
                              A refusal or completely off-topic response when the context
                              contains relevant facts is also a grounding failure.
    """
    def __init__(self, context_chunks: list[str], threshold: float):
        self.segmenter = StreamingSegmenter()
        self.context_chunks = context_chunks
        self.threshold = threshold
        self.claim_results: list[dict] = []
        self._full_response_tokens: list[str] = []
        self._evasion_flagged: bool = False

    def feed_token(self, token: str) -> list[dict]:
        self._full_response_tokens.append(token)
        newly_committed = self.segmenter.feed(token)
        return [self._score_sentence(s) for s in newly_committed]

    def finalize(self) -> dict | None:
        tail = self.segmenter.flush()
        tail_result = self._score_sentence(tail) if tail else None

        # ── Evasion Check ─────────────────────────────────────────────────────
        # After full response is collected, check if the LLM's output
        # entails ANY of the context claims. If it entails nothing (score < 0.25),
        # it's an evasion/hallucination — the response is grounding-unanchored.
        full_response = " ".join(self._full_response_tokens).strip()
        if full_response and self.context_chunks:
            max_entailment = max(
                entailment_score(chunk, full_response)
                for chunk in self.context_chunks
            )
            if max_entailment < 0.25:
                # The response is completely unanchored to the context
                evasion_event = {
                    "sentence": full_response[:200],
                    "score": round(1.0 - max_entailment, 4),
                    "flagged": True,
                    "best_chunk": self.context_chunks[0][:120],
                    "type": "evasion",
                }
                self._evasion_flagged = True
                self.claim_results.append(evasion_event)
                return evasion_event

        return tail_result

    def _score_sentence(self, sentence: str) -> dict:
        if not self.context_chunks:
            result = {"sentence": sentence, "score": None, "flagged": False, "best_chunk": None}
        else:
            scores = [(contradiction_score(chunk, sentence), chunk) for chunk in self.context_chunks]
            best_score, best_chunk = max(scores, key=lambda x: x[0])
            result = {
                "sentence": sentence, "score": round(best_score, 4),
                "flagged": best_score >= self.threshold,
                "best_chunk": best_chunk[:120],
            }
        self.claim_results.append(result)
        return result

    def grounding_risk(self) -> float:
        """Aggregate risk: fraction of flagged sentences + evasion penalty."""
        scored = [r for r in self.claim_results if r.get("score") is not None]
        if not scored:
            return 0.0
        # Evasion events always count as 100% flagged
        flagged_count = sum(1 for r in scored if r.get("flagged"))
        return round(flagged_count / len(scored), 4)

