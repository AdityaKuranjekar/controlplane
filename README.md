# 🛡️ ControlPlane: Deadline-Tiered Risk Middleware for Generative AI

[![Accenture Innovation Challenge 2026](https://img.shields.io/badge/Accenture%20Innovation%20Challenge-2026-blueviolet.svg)](#)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](#)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-FF4B4B.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](#)

> **ControlPlane** is a deadline-tiered risk middleware for enterprise Generative AI applications. It classifies every security, safety, and compliance check by *when the decision is needed* — **Block-Before-Send**, **Decide-Before-Inference**, or **Verify-After-Delivery** — and dynamically routes traffic to hardware and model tiers optimized for strict latency budgets.

---

## 🚀 Key Performance Benchmarks

| Metric | Measured Value | Impact |
| :--- | :--- | :--- |
| **Semantic Cache Hit Rate** | **57.5%** | Cuts expensive outbound LLM API calls by over half |
| **Cache Hit Latency** | **11.4 ms** | ~400x faster than raw LLM inference (~4,600 ms) |
| **Inference Cost Reduction** | **92.7%** | Achieved via FAISS caching + Frugal Model Cascading |
| **Adversarial Intercept Rate** | **100% (20/20)** | Zero prompt injections passed in benchmark tests |
| **Hallucination Detection Recall** | **90.0%** | Real-time sentence-level ONNX NLI streaming verification |
| **Audit Chain Integrity** | **100% Cryptographic** | SHA-256 hash-chained SQLite tamper-evident ledger |

---

## 🏛️ Deadline-Tiered Architecture

Traditional AI guardrails introduce high latency overhead (500ms+) by evaluating all policies synchronously before inference, or fail to stop agentic actions by evaluating post-hoc. **ControlPlane solves this with deadline-tiered execution:**

```text
               +-------------------------------------------------------+
               |                  Incoming User Request                 |
               +---------------------------+---------------------------+
                                           |
                                           v
[STAGE 1: BLOCK-BEFORE-SEND] <15ms Latency Budget
  ├── PII Redaction (Regex + Luhn Checksum validation -> Credit Cards)
  ├── Prompt Injection Profiling (Strict / Lenient policy DSL)
  └── [ACTION] -> If Violates Policy: BLOCK (HTTP 403 / Stream Terminate)
                                           | (ALLOW)
                                           v
[STAGE 2: DECIDE-BEFORE-INFERENCE] <25ms Latency Budget
  ├── FAISS Vector Similarity Cache (all-MiniLM-L6-v2 embeddings)
  │    └── Cache HIT -> Return immediately (11.4ms response time)
  └── Cache MISS -> Frugal Model Cascade Router
       ├── Tier 0: Fast Local/Edge Model (llama-3.1-8b)
       └── Tier 1: Fallback Enterprise Model (llama-3.3-70b upon refusal)
                                           |
                                           v
[STAGE 3: VERIFY-IN-STREAM / AFTER-DELIVERY] Concurrent / Async Budget
  ├── Real-Time Grounding Evaluator (ONNX INT8 DeBERTa-v3 NLI)
  │    ├── Sentence-Boundary Token Buffer & Claim Extraction
  │    └── Entailment Verification against Context -> Inject [REDACTED]
  └── Intent Contracts & Tool Sandbox Gateway (Agent Tool Call Validation)
                                           |
                                           v
[STAGE 4: GOVERNANCE & AUDIT] Continuous
  ├── Hash-Chained Audit Ledger (SHA256(prev_hash + payload) -> audit.db)
  ├── Thompson-Sampling Multi-Armed Bandit (Offline tau-threshold tuning)
  └── Streamlit Live Governance Console & Waterfall Telemetry
```

---

## 📦 System Modules & Directory Structure

```text
controlplane/
├── gateway/                 # FastAPI Backend & Core Policy Pipeline
│   ├── main.py              # Main API routes & streaming event handlers
│   ├── pregate/             # Stage 1: PII detection & Injection profiling
│   ├── cache/               # Stage 2: FAISS semantic caching engine
│   ├── router/              # Stage 2: Frugal model cascade router
│   ├── ground/              # Stage 3: ONNX NLI grounding evaluator
│   ├── agent/               # Stage 3: Tool sandbox & Intent contracts
│   ├── audit/               # Stage 4: SHA-256 hash-chain audit ledger
│   └── policy/              # Profile configuration loader (YAML policy DSL)
├── console/                 # Streamlit Live Dashboard & Operations Console
│   ├── app.py               # Main hero & navigation overview
│   └── pages/               # Interactive tabs: Inspector, Audit, Bandit, Scaling
├── docs/                    # Deep technical architecture & scaling docs
│   ├── ARCHITECTURE.md      # Micro-architecture & execution stages
│   ├── IMPLEMENTATION_PLAN.md # Phased development build ladder (L0 - L4)
│   ├── SCALING.md           # Enterprise production migration guide
│   └── LIMITATIONS.md       # Prototype boundaries & calibration notes
├── eval/                    # Evaluation suites, datasets, & metrics generators
├── tests/                   # Unit & Pytest verification suites
└── TEST_EVALUATION.md       # Comprehensive test execution checklist & logs
```

---

## ⚡ Quickstart Guide

### Prerequisites
- Python 3.10 or higher
- Groq API Key (Set in `.env` as `GROQ_API_KEY=your_key_here`)

### 1. Installation & Environment Setup
```powershell
# Clone the repository
git clone https://github.com/antrikshagalaxy/controlplane
cd controlplane

# Create & activate virtual environment
python -m venv .venv
.venv\Scripts\activate   # On Windows (or 'source .venv/bin/activate' on Linux/macOS)

# Install dependencies
pip install -r requirements.txt
```

### 2. Start the API Gateway (Backend)
```powershell
uvicorn gateway.main:app --reload --port 8080
```
*The API gateway runs at `http://localhost:8080` providing OpenAI-compatible `/v1/chat/completions` endpoints.*

### 3. Start the Governance Console (Frontend Dashboard)
```powershell
python -m streamlit run console/app.py
```
*Open your browser to `http://localhost:8501` to access the Live Request Inspector, Audit Chain Explorer, Grounding Calibration, and Bandit Tuning views.*

---

## 🧪 Running Verifications & Benchmark Evaluation

ControlPlane comes with full automated test suites and metric evaluation scripts:

```powershell
# Run L0-L3 Pytest suites
pytest tests/

# Run L1 Semantic Cache & Frugal Router Eval
python eval/suite_1_cache_cascade.py

# Run L2 Grounding Evaluator Calibration
python eval/suite_2_grounding.py

# Run L3 Injection Defense Evaluation
python eval/suite_3_injections.py

# Run L4 Offline Thompson-Sampling Bandit Replay
python eval/suite_4_bandit.py
```

---

## 📊 Enterprise Scaling Roadmap

| Capability | Free-Tier Prototype | Enterprise Production Equivalent |
| :--- | :--- | :--- |
| **Guard Model** | ONNX INT8 MiniLM / DeBERTa | Llama Guard 3-1B-INT4 on Edge / ExecuTorch |
| **Vector Store** | In-Process FAISS Flat Index | Qdrant / Pinecone Distributed Cluster |
| **Audit Ledger** | SQLite Cryptographic Hash-Chain | ClickHouse + S3 WORM Object Lock |
| **Policy Engine** | YAML Rules Engine | Open Policy Agent (OPA) / AWS Cedar |
| **Gateway Runtime**| FastAPI (Python) | Axum / Tonic (Rust) Gateway (Sub-5ms p99) |

---

## 👥 Team & Submission Info

- **Hackathon:** Accenture Innovation Challenge 2026
- **Team Name:** ProdMindAI
- **License:** MIT License