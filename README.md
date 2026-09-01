# 🛡️ ControlPlane: Deadline-Tiered Risk Middleware for Generative AI

[![Accenture Innovation Challenge 2026](https://img.shields.io/badge/Accenture%20Innovation%20Challenge-2026-blueviolet.svg)](#)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](#)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com/)
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
  └── Native HTML5/CSS3/JS Web Interface & Waterfall Telemetry
```

---

## 📦 System Modules & Directory Structure

```text
controlplane/

---

## 👥 Team & Submission Info

- **Hackathon:** Accenture Innovation Challenge 2026
- **Team Name:** ProdMindAI
- **License:** MIT License
>>>>>>> pr-main
