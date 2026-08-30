# LIMITATIONS

1. **Simulated Streaming for Grounding**: The grounding gate simulates streaming by chunking a complete cascade answer rather than scoring concurrently with live LLM token generation. True concurrent scoring would require restructuring the cascade to stream only pre-accepted tiers.

## Grounding Gate Evaluator Limitations
Streaming NLI grounding detects 87% of hallucinated claims (recall 0.87) at a calibrated 20% target FNR, but currently over-flags supported claims at a 65% false-positive rate (FPR: 0.65), driven by DeBERTa-xsmall's limited capacity on short-context claims. This is a known small-model tradeoff - the paper's larger DeBERTa-v3-large NLI variant reports substantially better separation; our xsmall model was chosen for the free-tier CPU latency budget. We prioritize recall (catching hallucinations) over precision (avoiding false alarms) as the correct tradeoff for a hallucination safety net, and expect production deployment to combine this with either a larger model or a second-stage confirmation step before user-facing action.

## Cache Bandit Offline Replay Limitations
The Thompson-sampling bandit (L4) for the cache threshold is configured as an offline-replay mechanism, not a live-wired production router. While the bandit accurately achieves sublinear regret convergence across the evaluation stream, it operates as an analytical tool rather than a real-time gateway component in this prototype phase.
