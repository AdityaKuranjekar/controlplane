# ControlPlane

**ControlPlane** is a deadline-tiered risk middleware for generative AI. It sits between an
enterprise application and the foundation-model API it consumes, and classifies every safety
check by *when the answer is needed*:

| Deadline class | Question it answers | Where it runs in the request |
|---|---|---|
| **Block-before-send** | Is this prompt safe to even forward? | Synchronous pre-gate (PII + injection) |
| **Decide-before-inference** | Which model / cache should serve this, and is the answer reliable? | Semantic cache + frugal cascade |
| **Verify-after-generation** | Does the generated answer actually match its sources / obey its contract? | Grounding gate (RAG) + Action gateway (agents) |
| **Audit-and-adapt** | Can we prove what happened, and are our thresholds still optimal? | Hash-chained audit log + offline bandit |

The same request path is reused across three very different enterprise use cases, selected per
request by a **policy profile**: `customer_bot` (customer-facing, tight latency budget),
`internal_rag` (internal knowledge assistant, RAG-grounded), and `decision_agent`
(tool-using agent, high blast radius).

---

## 1. What was actually built (end-to-end)

The prototype is two processes:

1. **`gateway/`** — a FastAPI service exposing an OpenAI-compatible
   `POST /v1/chat/completions` endpoint plus three read APIs for the console.
2. **`console/`** — a multi-page Streamlit app that drives the gateway and visualises its
   decisions.

Everything below is wired and runs. Two components are deliberately **offline analysis tools**,
not live request-path components, and are labelled as such: the **conformal calibration** of the
grounding threshold and the **Thompson-sampling bandit** for the cache threshold.

> **Deploy note (`cloud-lite`):** to fit the free 512 MB hosting tier, two heavy dependencies
> were swapped for API-backed equivalents *without changing the architecture*:
> the semantic cache runs as an exact-match store instead of FAISS + MiniLM embeddings, and the
> NLI grounding model is a Groq `llama-3.1-8b-instant` call prompted as a strict entailment
> classifier instead of a local `nli-deberta-v3-xsmall` ONNX INT8 model. The full-fat
> implementations (`models/`, FAISS index code, `eval/fixtures/`) remain in the repo and are
> what the eval numbers were produced against. See `docs/SCALING.md`.

### 1.1 Request lifecycle (`gateway/main.py`)

For every request the gateway runs these stages, each individually timed by
`gateway/timing.py::Stopwatch` and emitted as `X-CP-<stage>-ms` response headers:

```
request
  │
  ├─ get_profile(cp_profile)                     policy/engine.py  — loads + caches YAML profile
  │
  ├─ [stage: pii]      detect_and_tokenize()     pregate/pii.py
  │                    regex for EMAIL / PHONE_IN / CREDIT_CARD / AADHAAR / PAN_IN,
  │                    Luhn checksum gates CREDIT_CARD to kill false positives,
  │                    each hit replaced in-place with [PII:<LABEL>_<n>]
  │
  ├─ [stage: injection] injection_score()        pregate/injection.py
  │                    keyword markers ("ignore previous instructions", "jailbreak", …)
  │                    score = min(1.0, hits * 0.4)
  │
  ├─ RiskVector(privacy, safety, grounding, cost) built            schemas.py
  ├─ decide(risk, profile)                        decision/engine.py
  │                    priority-ordered rule chain: safety checked BEFORE privacy,
  │                    profile maps each hit to an action (ALLOW/REDACT/FLAG/ABSTAIN/BLOCK)
  │
  ├─ append_row(...)  →  audit.db                 audit/chain.py
  │                    row_hash = SHA256(canonical_json(payload + prev_hash))
  │
  ├─ if action == BLOCK → return "[BLOCKED: reason]" (streamed or JSON), stop here
  │
  ├─ [stage: cache_lookup] cache_lookup()         cache/semantic_cache.py
  │                    per-profile serving-cost threshold (cache/cost_model.py):
  │                    customer_bot 0.88 · internal_rag 0.94 · decision_agent 1.01 (never cache)
  │                    HIT → return cached answer, X-CP-Cache: HIT, X-CP-Cache-Sim
  │
  ├─ [stage: cascade] run_cascade()               router/cascade.py
  │                    walk TIERS in order (router/tiers.py):
  │                    tier0 gpt-oss-20b (accept ≥ 0.75) → tier1 gpt-oss-120b (always accept)
  │                    each tier's full answer scored by router/scorer.py::reliability_score
  │                    (refusal / hedge keyword heuristic v0); first passing tier wins
  │                    → X-CP-Tier, X-CP-Escalated
  │                    cache_store() persists the accepted answer
  │
  ├─ if profile == internal_rag AND context_chunks present:
  │     [stage: grounding_setup] GroundingGate(context_chunks, threshold)   ground/grounding_gate.py
  │     answer is re-chunked and streamed; as each sentence commits
  │     (ground/segmenter.py state machine OPEN→STABLE→COMMITTED, abbreviation/decimal guarded)
  │     it is scored for contradiction against every context chunk
  │     (ground/nli_model.py), max score wins, flagged if ≥ threshold
  │     → SSE `event: claim_checked` per sentence, X-CP-Grounding-Risk = flagged fraction
  │
  └─ else → return answer (JSON or single SSE chunk)
```

### 1.2 Layer-by-layer detail

**L0 — Synchronous pre-gate (`gateway/pregate/`, `gateway/decision/`, `gateway/audit/`)**

- `pii.py`: five PII classes by regex; `luhn_valid()` prevents any random 13–16 digit string
  being tokenised as a card. Returns `(redacted_text, findings_dict)`. The redacted string is
  what gets forwarded to the LLM — raw PII never leaves the gateway.
- `injection.py`: cheap deterministic keyword scan → `[0,1]` safety score.
- `decision/engine.py`: `decide()` is intentionally a **priority chain, not a sum** — safety
  is evaluated before privacy so an injection always wins over a PII redaction. The profile
  YAML (`policy/profiles/*.yaml`) supplies both the thresholds and the action mapping, so the
  *same* risk score produces `BLOCK` under `customer_bot`/`decision_agent` and `FLAG` under
  `internal_rag`.
- `audit/db.py` + `audit/chain.py`: SQLite table `audit_log`; every row stores
  `row_hash` and `prev_hash`, where `row_hash = SHA256(canonical_json({profile, prompt_redacted,
  action, reason, risk_vector, latency_ms, prev_hash}))`. First row chains to the literal
  `"GENESIS"`. This makes the log tamper-evident: altering any historical row breaks every
  subsequent hash, which the console re-computes and checks.

**L1 — Cost lane (`gateway/cache/`, `gateway/router/`)**

- `cache/cost_model.py`: `serving_cost_threshold(profile)` is the L1 stand-in for the paper's
  learned per-query serving cost `c(q)` — a fixed calibrated constant per profile. Aggressive
  for `customer_bot` (high repetition, low stakes), conservative for `internal_rag`, effectively
  disabled for `decision_agent` (every agent turn is fresh).
- `cache/semantic_cache.py`: `cache_lookup` / `cache_store`, disk-persisted JSON so the cache
  survives restarts on ephemeral hosts. (Full version: `all-MiniLM-L6-v2` embeddings + FAISS
  flat index, cosine similarity vs threshold.)
- `router/cascade.py`: **non-streaming per tier** — each tier produces a full answer that is
  scored before accept/escalate; only the finally-accepted tier's answer is streamed to the
  client. `run_cascade` also catches `groq.BadRequestError` and falls through to the next tier,
  with the last tier as guaranteed fallback.
- `router/scorer.py`: `reliability_score` is heuristic v0 (refusal markers −0.5, hedge markers
  −0.15 each, very short answers penalised). The documented upgrade path is a trained regression
  head once the eval suite has produced labelled `(query, answer, correct)` data.

**L2 — Grounding lane (`gateway/ground/`)**

- `segmenter.py`: `StreamingSegmenter` — a 3-state machine (`OPEN → STABLE → COMMITTED`).
  A sentence-ending punctuation moves it to `STABLE`; it waits one more token before committing,
  to reject abbreviations (`Dr.`, `e.g.`) and decimals (`3.14`). `flush()` emits the tail at
  end-of-stream.
- `nli_model.py`: `contradiction_score(premise, hypothesis) → [0,1]`. Cloud-lite prompts
  `llama-3.1-8b-instant` at temperature 0 as a strict inference model returning a single float;
  full version runs `nli-deberta-v3-xsmall` INT8 ONNX locally.
- `templating.py`: `make_hypothesis(question, answer)` turns a Q/A pair into a declarative
  sentence so the NLI model gets two well-formed inputs.
- `grounding_gate.py`: for each committed sentence, score against **every** context chunk, take
  the **max** contradiction score (worst case), flag if `≥ threshold`. `grounding_risk()`
  returns the flagged fraction — this is the `RiskVector.grounding` value.
- `conformal.py`: `calibrate_threshold(cal_scores_hallucinated, target_fnr)` — split-conformal
  quantile method with the finite-sample `ceil((n+1)·target_fnr)` order-statistic correction.
  Picks the threshold λ that catches `1 − target_fnr` of known hallucinations on the
  calibration split, giving a distribution-free FNR guarantee on held-out data.
  `evaluate_at_threshold` produces the full confusion matrix / precision / recall / F1.

**L3 — Agent lane & governance (`gateway/agent/`)**

- `sandbox.py`: `TOOL_REGISTRY` of five **no-op stub tools** (`read_file`, `search_db`,
  `send_email`, `transfer_funds`, `update_record`). Every call is logged to `CALL_LOG`; nothing
  has a real side effect. `read_file("invoice_injected.txt")` returns content with an embedded
  `SYSTEM OVERRIDE … call send_email(...)` — the poisoned-tool-output test fixture.
- `schemas.py::IntentContract`: declared once per agent task — `allowed_tools`,
  `allowed_egress_domains`, `max_write_ops`, `requires_human_above_amount`, `max_tool_calls`.
- `action_gateway.py::ActionGateway.validate_and_execute(call)` runs **7 ordered checks** before
  a tool executes:
  1. hard `max_tool_calls` ceiling (runaway-loop guard)
  2. tool must be in `allowed_tools`
  3. if the task is **tainted** (a prior `read_file`/`search_db` output contained injection
     markers), block *all* write-capable tools
  4. `send_email` recipient domain must be in `allowed_egress_domains`
  5. `max_write_ops` budget for write tools
  6. `transfer_funds` above `requires_human_above_amount` → `ABSTAIN_NEEDS_HUMAN` (not a silent
     block — explicitly routes to a human)
  7. `update_record` with a stale ETag (`state.py` optimistic-concurrency simulation) → block
     the write
  Only then does it execute via the sandbox, then **re-scans the tool's own output** for
  injection markers and sets `tainted` for the rest of the task. Every BLOCK / ABSTAIN is
  written to the same hash-chained audit log.

**L4 — Adaptive optimisation & console**

- `cache/bandit_cost_model.py`: `CacheBandit` over candidate cache-similarity thresholds
  `[0.75, 0.82, 0.88, 0.94]`, each an arm with a `Beta(α, β)` posterior updated by a composite
  reward (accuracy − latency − token-cost − alert-fatigue, simplified for offline replay).
  **Offline replay only** — replayed against the L1 fixture stream + paraphrases, never wired
  into the live path. It exists to demonstrate the production upgrade from L1's fixed `τ_cache`.
- `console/` — five pages (below).

### 1.3 Read APIs (`gateway/main.py`)

| Endpoint | Serves |
|---|---|
| `GET /v1/audit/logs` | all `audit_log` rows for the Audit Explorer |
| `GET /v1/grounding/calibration` | `eval/results/l2_calibration.json` + `l2_metrics.json` |
| `GET /v1/routing/bandit` | `eval/results/l4_bandit_metrics.json` |

### 1.4 Console (`console/`)

`app.py` is the landing page — pulls live headline metrics straight from the
`eval/results/*.json` files and the audit DB row count. `theme.py` injects shared CSS.

| Page | What it does |
|---|---|
| `0_How_It_Works` | animated SVG of the 5-stage pipeline + per-stage explainers |
| `1_Live_Inspector` | fires real requests at the gateway; preset scenarios (PII leak, injection, clean, RAG hallucination, clean RAG); colour-coded action badge; latency-waterfall bar chart from `X-CP-*-ms` headers; raw header JSON |
| `2_Audit_Explorer` | fetches `/v1/audit/logs`, renders the table, **re-computes the SHA-256 chain client-side** and reports the first broken row (or "verified for all N rows") |
| `3_Grounding_Calibration` | achieved-FNR-vs-target-FNR line chart, operating-curve table, recall/precision at 0.20 target FNR, plus an explicit "this is a recall-first safety net, not a low-alert filter" warning |
| `4_Bandit_Curves` | best-fixed-arm-in-hindsight vs bandit-favoured arm, cumulative-regret curve, per-arm Beta stats |
| `5_Production_Scale` | worked-out reference load (~50k req/wk ≈ 0.08 req/s, ~0.8 req/s peak), prototype→production component table, and honest scaling risks |

---

## 2. Evaluation (`eval/`)

Each suite runs against committed fixtures so results are reproducible with zero live cost
where possible.

| Suite | Fixture | Method | Committed result |
|---|---|---|---|
| `suite_1_cache_cascade.py` | `fixtures/banking77_300.json` (299 queries) | replay through `TestClient(app)`, measure hit rate + hit/miss latency percentiles | `results/l1_metrics.json` — **57.5% hit rate**, avg hit 11.4 ms (p95 18.2 ms), avg miss 4.6 s |
| `suite_2_grounding.py` | `fixtures/haluEval_sample.json` | 60/40 calibration/test split, NLI-score each claim, sweep target FNR ∈ {0.10, 0.20, 0.30} | `results/l2_metrics.json` — **recall 0.90**, precision 0.79 (tp45 / fp12 / tn88 / fn5); `l2_calibration.json` — achieved FNR ≤ target at every point |
| `suite_3_agent.py` | `fixtures/agent_scenarios.py` (40 scenarios: 20 benign, 20 adversarial) | run each through `ActionGateway`, check benign pass / adversarial intercept | `results/l3_metrics.json` — **intercept rate 1.0 (20/20)**, false-block rate 0.0, 0 unauthorised writes executed; every adversarial class covered (ceiling, allowlist, taint, egress, budget, human-loop, stale-ETag) |
| `suite_4_bandit.py` | L1 fixture + `fixtures/paraphrases.json` | offline Thompson-sampling replay, ~299 rounds | `results/l4_bandit_metrics.json` — bandit-favoured arm `τ_0.75` == best fixed arm in hindsight |
| `sanity_check_cold_start.py` | synthetic | measures first-request model cold-load vs warm encode | `results/l0_sanity_check.json` |

Unit tests in `tests/` cover PII / Luhn, injection scanning, the decision chain, the bandit,
the NLI model, the L2 templating regression, and grounding stress cases.
`TEST_EVALUATION.md` records the manual E2E checklist per phase.

### Known limitations (see `docs/LIMITATIONS.md`)

- **Grounding precision** is ~57–79% depending on split — the xsmall NLI model over-flags
  supported claims. Deliberately tuned recall-first (catch hallucinations) as a safety net,
  with a bigger model or a second-stage filter as the production fix.
- **Simulated streaming** — the grounding gate chunks a completed cascade answer rather than
  scoring concurrently with live token generation.
- **Bandit is offline** — accurate sublinear-regret convergence on the replay stream, but an
  analytical tool, not a live gateway component in this phase.

---

## 3. Running locally

Two processes, each needs `.venv` active and a `.env` with `GROQ_API_KEY`.

### 1. API Gateway

```powershell
.venv\Scripts\activate
uvicorn gateway.main:app --reload --port 8080
```

### 2. Streamlit console

```powershell
.venv\Scripts\activate
python -m streamlit run console/app.py
```

*Windows: use `python -m streamlit`, not bare `streamlit`, to avoid the Windows Store alias.*

The console reads `GATEWAY_URL` (default `http://localhost:8080` in the Live Inspector,
`http://localhost:8000` in the other pages — set `GATEWAY_URL` to override).

### Run the eval suites

```bash
python -m eval.suite_1_cache_cascade
python -m eval.suite_2_grounding
python -m eval.suite_3_agent
python -m eval.suite_4_bandit
pytest
```

### Deploy

`Procfile` / `render.yaml` run the gateway with `uvicorn gateway.main:app --host 0.0.0.0
--port $PORT`; `GROQ_API_KEY` is an unsynced env var. `requirements.txt` is the cloud-lite
dependency set (no torch / faiss / onnxruntime).

---

## 4. Repository structure

```text
controlplane/
├── gateway/
│   ├── main.py                 FastAPI app, request lifecycle, read APIs
│   ├── schemas.py              Pydantic models (ChatCompletionRequest, RiskVector, IntentContract, …)
│   ├── timing.py               Stopwatch → X-CP-*-ms headers
│   ├── pregate/                pii.py (regex + Luhn), injection.py (keyword score)
│   ├── policy/                 engine.py + profiles/{customer_bot,internal_rag,decision_agent}.yaml
│   ├── decision/engine.py      priority-ordered ALLOW/REDACT/FLAG/ABSTAIN/BLOCK
│   ├── audit/                  db.py (SQLite schema) + chain.py (SHA-256 hash chain)
│   ├── cache/                  semantic_cache.py, cost_model.py, bandit_cost_model.py
│   ├── router/                 cascade.py, scorer.py, tiers.py
│   ├── ground/                 segmenter.py, nli_model.py, templating.py, grounding_gate.py, conformal.py
│   ├── llm/groq_client.py      Groq wrapper (mock fallback if no key)
│   └── agent/                  sandbox.py, state.py, action_gateway.py
├── console/                    Streamlit landing page + pages/0..5, theme.py
├── eval/                       suite_1..4, sanity_check, fixtures/, results/
├── models/                     nli-deberta-v3-xsmall ONNX (+ INT8) — full-version artefacts
├── tests/                      pytest unit + stress tests
├── docs/                       ARCHITECTURE.md, IMPLEMENTATION_PLAN.md, SCALING.md, LIMITATIONS.md
├── Procfile / render.yaml      deploy config
└── requirements.txt            cloud-lite deps
```

Built for the Accenture Innovation Challenge 2026 · Team ProdMindAI.
