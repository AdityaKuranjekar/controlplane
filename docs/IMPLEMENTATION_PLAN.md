# ControlPlane Implementation Plan

This document outlines the step-by-step build ladder for ControlPlane: a deadline-tiered risk middleware for generative AI.

## Phase 0 (L0): The Spine (Core Foundation)
*Goal: One working request path end-to-end with a real decision and latency tracking.*
- Initialize FastAPI app with `/v1/chat/completions` endpoint.
- Implement profile configuration loader (`customer_bot`, `internal_rag`, `decision_agent` YAMLs).
- Build PII pre-gate detector (custom regex + Luhn checksum validation for card numbers; no external DLP dependency at this stage) for prompt sanitization.
- Create Pydantic schemas including a RiskVector (privacy/safety/grounding/cost fields, only privacy+safety populated at L0).
- Set up pass-through streaming to the Groq API.
- Implement basic Decision Engine as a priority-ordered rule chain (safety checked before privacy) resulting in ALLOW / REDACT / BLOCK.
- Add per-stage latency instrumentation (`t_compute`).
- Set up SHA-256 hash-chained SQLite audit database with a prev_hash field per row to log requests.

## Phase 1 (L1): Cost Lane (Frugal Routing & Caching)
*Goal: Implement semantic caching and LLM routing to demonstrate cost/latency savings.*
- Implement Semantic Cache using `all-MiniLM-L6-v2` and FAISS flat index.
- Build the Frugal Router cascade: tier0 (Groq llama-3.1-8b-instant) -> tier1 (Groq llama-3.3-70b-versatile), scored by a heuristic v0 reliability scorer (refusal/hedge keyword detection); trained regression scorer is an L3/L4 upgrade once labeled data exists from the eval suite.
- Cascade is non-streaming per tier — each tier's full answer is scored before accept/escalate; only the finally-accepted tier's answer is streamed to the client.
- Create a local replay fixture generation script (`generate_paraphrases.py`, run once, output committed to repo for reproducible zero-cost eval replay) using e.g., a Banking77 subset.

## Phase 2 (L2): Grounding Lane (Real-time Hallucination Check)
*Goal: Streaming claim verification against retrieved chunks.*
- Export `nli-deberta-v3-xsmall` to ONNX INT8 for fast local inference.
- Build sentence-boundary streaming segmenter (buffer tokens, emit on sentence completion).
- Run NLI checks on stable claims against context chunks.
- Implement conformal threshold calibration using a RAGTruth evaluation slice.

## Phase 3 (L3): Agent Lane & Governance
*Goal: High-blast-radius use case protection and tamper-evident auditing.*
- Build Mock Tool Sandbox (`read_file`, `send_email`, etc.).
- Implement Intent Contracts and the Action Gateway (validate tool calls before execution).
- Set up hash-chained audit logging (`row_hash = SHA256(prev_hash + canonical_json(row))`).
- Develop a 40-scenario injection suite to test interception of malicious tool payloads.

## Phase 4 (L4): Adaptive & Console (Polish)
*Goal: UI for stakeholders and adaptive thresholds.*
- Build Streamlit Governance Console (live request inspector, policy editor, latency waterfall).
- Implement asynchronous background worker for SelfCheck-NLI verification.
- Add Thompson-sampling bandit for offline threshold tuning.
