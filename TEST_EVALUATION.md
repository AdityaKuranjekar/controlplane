# ControlPlane Test Evaluation

This document tracks the End-to-End (E2E) testing and validation of the ControlPlane Gateway across its various development phases.

---

## Phase L0: The Spine (Synchronous Pre-Gate)

### ✅ Test Checklist

- [x] **1. Credit Card Tokenization**
  - *Criteria:* A valid Luhn credit card is tokenized and never appears in the outbound LLM call.
  - *Status:* **PASSED** (Replaced with `[PII:CREDIT_CARD_X]`)

- [x] **2. Fake Credit Card Handling**
  - *Criteria:* A 16-digit number that fails the Luhn check is NOT tokenized.
  - *Status:* **PASSED**

- [x] **3. Injection Phrase Profiling**
  - *Criteria:* "Ignore previous instructions" correctly `BLOCK`s on strict profiles (`customer_bot`, `decision_agent`) and `FLAG`s on lenient profiles (`internal_rag`).
  - *Status:* **PASSED**

- [x] **4. Clean Prompt Overhead**
  - *Criteria:* A clean prompt results in an `ALLOW` action and streams normally.
  - *Status:* **PASSED**

- [x] **5. Audit Log Cryptographic Chaining**
  - *Criteria:* Consecutive requests generate chronological rows in SQLite, each cryptographically chained to the `prev_hash`.
  - *Status:* **PASSED**

- [x] **6. Telemetry and Latency Budget**
  - *Criteria:* PII and Injection scanning complete in under 30ms, and individual header timings sum up to `X-CP-Total-ms`.
  - *Status:* **PASSED**

### 📝 Proof of Execution (Pytest Output)

```text
============================= test session starts =============================
platform win32 -- Python 3.14.6, pytest-9.0.3, pluggy-1.6.0
rootdir: D:\Professional Work\Business\Accenture\controlplane
plugins: anyio-4.13.0
collecting ... collected 5 items

verify_l0.py::test_credit_card_tokenized 
  Test 1 Passed: Valid Credit Card tokenized and omitted from outbound LLM payload.
  -> Outbound payload content: My card is [PII:CREDIT_CARD_1]
PASSED
verify_l0.py::test_fake_credit_card_not_tokenized 
  Test 2 Passed: Fake credit card (fails Luhn) is NOT tokenized.
PASSED
verify_l0.py::test_injection_phrase_handling 
  Test 3 Passed: Injection phrase handled correctly across profiles (BLOCK / FLAG).
PASSED
verify_l0.py::test_clean_prompt_and_timing 
  Test 4 & 6 Passed: Clean prompt ALLOWed, latency is <30ms overhead, and header components sum to Total.
PASSED
verify_l0.py::test_chaining 
  Test 5 Passed: Audit logs are chained chronologically with correct hashes.
PASSED

======================== 5 passed, 1 warning in 0.51s =========================
```


## Phase L1: Cost Lane (Frugal Router)

### ✅ Test Checklist

- [x] **1. Exact Cache Match**
  - *Criteria:* Identical query sent twice → second is a cache HIT with extremely low `t_compute`.
  - *Status:* **PASSED**

- [x] **2. Genuine Paraphrase**
  - *Criteria:* A semantic paraphrase hits the cache if it clears the `τ_cache` similarity threshold.
  - *Status:* **PASSED**

- [x] **3. Distinct Queries**
  - *Criteria:* Two genuinely different queries MISS both times, avoiding false hits.
  - *Status:* **PASSED**

- [x] **4. Cascade Escalation (Refusal)**
  - *Criteria:* Force a `tier0` refusal-style answer (test with a nonsense prompt) → confirm escalation to `tier1` happens and `X-CP-Escalated: True` shows in headers.
  - *Status:* **PASSED**

- [x] **5. Cascade Clean Tier0**
  - *Criteria:* Force a clean `tier0` answer → confirm it's accepted without escalation, `X-CP-Tier: tier0`.
  - *Status:* **PASSED**

- [x] **6. Index Persistence**
  - *Criteria:* Kill and restart the gateway process → FAISS index reloads from disk, previously cached entries still HIT.
  - *Status:* **PASSED**

- [x] **7. End-to-End Evaluation Harness**
  - *Criteria:* `suite_1_cache_cascade.py` runs end-to-end against fixture queries and produces `l1_metrics.json` with a non-trivial hit rate and cost savings.
  - *Status:* **PASSED** (13.3% hit rate, 92.7% est. cost savings on the 15-query mock dataset)

### 📝 Proof of Execution (Pytest & Eval Output)

```text
============================= test session starts =============================
verify_l1.py::test_identical_query PASSED
verify_l1.py::test_genuine_paraphrase PASSED
verify_l1.py::test_two_different_queries PASSED
verify_l1.py::test_cascade_escalation PASSED
verify_l1.py::test_cascade_clean_tier0 PASSED
verify_l1.py::test_faiss_reload PASSED
======================== 6 passed, 1 warning in 14.89s ========================

{
  "cache_hits": 2,
  "cache_misses": 13,
  "tier0_used": 13,
  "tier1_used": 0,
  "cache_hit_rate": 0.13333333333333333,
  "avg_hit_latency_ms": 280.53,
  "est_cost_savings_pct": 92.7
}
```
---