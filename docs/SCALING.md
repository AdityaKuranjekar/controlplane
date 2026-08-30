# Scaling to Production

This document maps out how the current free-tier prototype architecture translates into an enterprise-grade production environment.

| Prototype (free tier) | Production Equivalent | Why |
|---|---|---|
| ONNX INT8 MiniLM guard | Llama Guard 3-1B-INT4 on ARM/ExecuTorch | Higher F1, multilingual support; requires dedicated CPU/edge footprint. |
| FAISS in-process | Qdrant / Pinecone cluster | Persistence, sharding, capability to handle >10M vectors. |
| SQLite hash chain | ClickHouse + WORM/S3 Object Lock | Compliance-grade immutability and high-throughput analytics. |
| YAML policy DSL | OPA/Rego + AWS Cedar | Formal verification, integrations with existing enterprise IAM/tooling. |
| asyncio queue | Kafka / Redis Streams | Backpressure handling, message replay, multi-consumer support. |
| FastAPI (Python) | Rust (Axum) gateway | 5–10× lower p99 overhead. |
| SelfCheck N=3-5 (planned, L4) | N=20 + token-level probes on self-hosted fleet | Higher AUC; probes require inference-time access to model weights. |
| Fixed τ_cache per profile (L1) | Learned per-query cost via CUCB-SC / CLCB-SC-LS bandit (L4) | Adapts to real traffic distributions instead of a hand-tuned constant. |
