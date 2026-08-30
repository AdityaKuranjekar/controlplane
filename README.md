# ControlPlane

**ControlPlane** is a deadline-tiered risk middleware for generative AI. It classifies every check by *when the answer is needed* — block-before-send, decide-before-inference, or verify-after-delivery — and routes each to hardware that can meet that deadline.

## Documentation

Please refer to the `docs/` folder for comprehensive documentation on the system:
- [Implementation Plan](docs/IMPLEMENTATION_PLAN.md): The phased build ladder (L0 - L4) for developing the prototype.
- [Architecture](docs/ARCHITECTURE.md): The core system flow and differentiators.
- [Scaling to Production](docs/SCALING.md): How the prototype architecture translates to an enterprise environment.
- [Limitations](docs/LIMITATIONS.md): Known prototype limitations and boundaries.

## Quickstart (Running Locally)

To run the full ControlPlane prototype locally, you need to start two processes in separate terminal windows. Both processes require the Python virtual environment (`.venv`) to be active, and a valid `.env` file with `GROQ_API_KEY`.

### 1. Start the API Gateway
The gateway handles all core policy routing, semantic caching, PII redaction, and grounding evaluation.

```powershell
# In Terminal 1:
.venv\Scripts\activate
uvicorn gateway.main:app --reload --port 8080
```

### 2. Start the Streamlit UI Console
The console provides the Live Inspector, Audit Explorer, Bandit Curves, and Grounding Calibration tools.

```powershell
# In Terminal 2:
.venv\Scripts\activate
python -m streamlit run console/app.py
```

*Note on Windows: Use `python -m streamlit` instead of just `streamlit` to avoid conflicts with Windows Store aliases.*

## Repository Structure

```text
controlplane/
├── README.md
├── docs/                (Architecture and design docs)
├── gateway/             (FastAPI backend and policy engine)
├── console/             (Streamlit UI frontend)
├── eval/                (Evaluation scripts and datasets)
├── tests/               (Unit tests)
└── data/                (Runtime databases, e.g., audit.db)
```