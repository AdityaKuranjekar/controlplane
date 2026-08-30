# LLM Control Plane Architecture

The Control Plane is structured across four functional layers:

1. **L1 - Semantic Cache Cascade**: FAISS-based semantic caching routing hit requests immediately, while cascading misses through tier models (e.g. `llama3-8b-8192` -> `gpt-oss-20b`) upon rate limit or failure exhaustion.
2. **L2 - Grounding Evaluator**: A streaming NLI validation layer using `DeBERTa-v3` variants. The gate splits streams logically by sentence boundaries, evaluates for entailment against provided RAG context, and injects `[REDACTED]` tokens for detected hallucinations.
3. **L3 - Action Gateway & Intent Contracts**: An interception proxy that verifies JSON-RPC tool payloads against a declared Intent Contract, enforcing strict boundaries (e.g., zero write-ops, allowed endpoint whitelists, rate ceilings) via stateless Hash-Chained Audit Logs (`audit.db`).
4. **L4 - Bandit Optimization & Console**: 
   * **Console**: A Streamlit dashboard to inspect live inference traffic, navigate the cryptographically verified hash chain, and visualize offline model convergence.
   * **Offline Bandit**: A Thompson-sampling mechanism (Beta distribution) used to identify optimal semantic similarity thresholds ($\tau$). **NOTE: The Bandit is explicitly designed as an offline replay tool.** It is not wired directly into the production request path. To achieve full sublinear convergence, the bandit must be replayed against a larger corpus (1000+ rounds), as the sample 15-item evaluation stream is insufficient to separate competitive cache thresholds fully.
