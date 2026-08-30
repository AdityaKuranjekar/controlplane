# ControlPlane

**ControlPlane** is a deadline-tiered risk middleware for generative AI. It classifies every check by *when the answer is needed* — block-before-send, decide-before-inference, or verify-after-delivery — and routes each to hardware that can meet that deadline.

## Documentation

Please refer to the `docs/` folder for comprehensive documentation on the system:
- [Implementation Plan](docs/IMPLEMENTATION_PLAN.md): The phased build ladder (L0 - L4) for developing the prototype.
- [Architecture](docs/ARCHITECTURE.md): The core system flow and differentiators.
- [Scaling to Production](docs/SCALING.md): How the prototype architecture translates to an enterprise environment.
- [Limitations](docs/LIMITATIONS.md): Known prototype limitations and boundaries.

## Repository Structure

```text
controlplane/
├── README.md
├── docs/
│   ├── ARCHITECTURE.md
│   ├── IMPLEMENTATION_PLAN.md
│   ├── LIMITATIONS.md
│   └── SCALING.md
├── gateway/             (To be implemented)
├── worker/              (To be implemented)
├── console/             (To be implemented)
├── eval/                (To be implemented)
└── models/              (To be implemented)
```