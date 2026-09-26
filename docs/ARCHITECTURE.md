# Mentis-Q: System Architecture & Design Specification

## 1. System Architecture Overview

The **Mentis-Q Quantum Digital Signature Framework** is a full-stack research, simulation, and demonstration platform designed for **Smart India Hackathon (SIH)**. It implements an information-theoretically motivated Quantum Digital Signature (QDS) scheme based on published quantum cryptography theory, combining Bell pair teleportation with Pauli correction, multi-verifier quantum memory registries, dual-threshold projective verification, mathematical concentration bounds, and live hardware-level attack simulation.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 REACT 19 + VITE FRONTEND                               │
│  ├── Key Distribution Page (/key-distribution)    - 4-Stage Teleportation Pipeline     │
│  ├── Forgery Analysis Page (/forgery-analysis)     - Recharts Hoeffding vs Monte Carlo │
│  ├── Performance Page (/performance)               - O(L) Scaling & 2x2 Confusion Grid │
│  ├── Signature & Verification Pages               - L Copies, Mismatch m & Detectors   │
│  └── Physics Lab & Attack Simulation Pages        - CHSH Test, Tomography & Kraus Noise│
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │ HTTP / JSON REST APIs
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 FASTAPI PYTHON BACKEND                                 │
│  ├── /api/qds/*        - Keygen, QPKD Teleportation, Classical Signing, Verification   │
│  ├── /api/analysis/*   - Hoeffding Bounds, Monte Carlo Sweeps, Aer Validation, CSV/JSON│
│  ├── /api/attacks/*    - Forgery, Impersonation, Nonce Replay, Rate Limiter Lockout    │
│  ├── /api/physics-lab/*- Density Matrix, Tomography, CHSH Bell Test, No-Cloning Bound  │
│  └── /api/signatures/* - Legacy & Extended Quantum State Operations                    │
└───────────────────────┬────────────────────────────────────────────┬───────────────────┘
                        │                                            │
                        ▼                                            ▼
┌──────────────────────────────────────────────────┐ ┌───────────────────────────────────┐
│              QUANTUM SIMULATION ENGINE           │ │         PERSISTENCE LAYER         │
│  - Qiskit 2.x & Qiskit Aer Statevector Engine    │ │  - SQLite with WAL Mode & Pooling │
│  - app/qds/ (Alphabet, Keygen, Memory, Verify)   │ │  - SQLAlchemy ORM Schema          │
│  - app/analysis/ (Hoeffding Bounds, Sweeps, ROC) │ │  - qds_nonces (One-Time TTL Guard)│
│  - app/quantum/ (Kraus Channels, EPR Pairs)      │ │  - qds_verifiers & qds_rate_limits│
└──────────────────────────────────────────────────┘ └───────────────────────────────────┘
```

---

## 2. Codebase Organization & Module Directory

```
Mentis-Q/
├── backend/
│   ├── app/
│   │   ├── qds/                         # Core Quantum Digital Signature Engine
│   │   │   ├── __init__.py              # Package exports & public API
│   │   │   ├── keygen.py                # 6 Pauli eigenstates alphabet & private/public keygen
│   │   │   ├── distribution.py          # Bell pair generation, teleportation & quantum memory
│   │   │   ├── signing.py               # Classical signature release & SHA-256 binding
│   │   │   ├── verification.py          # Projective measurement & mismatch rate calculation
│   │   │   ├── thresholds.py            # Dual thresholds (s_a, s_v) & decision logic
│   │   │   └── adversary.py             # Forgery, Impersonation, Replay & Rate Limiter attacks
│   │   ├── analysis/                    # Theoretical Analysis & Benchmarking
│   │   │   ├── __init__.py              # Package exports
│   │   │   ├── forgery.py               # Analytical Hoeffding bounds, Monte Carlo, Aer test
│   │   │   └── benchmarks.py            # O(L) latency/memory scaling & dynamic confusion matrix
│   │   ├── api/                         # FastAPI REST Route Controllers
│   │   │   ├── analysis.py              # /api/analysis/* (Bounds, Sweeps, Exports, Benchmarks)
│   │   │   ├── attacks.py               # /api/attacks/* (Adversary simulation & detectors)
│   │   │   ├── physics_lab.py           # /api/physics-lab/* (Tomography, CHSH, Kraus noise)
│   │   │   ├── signatures.py            # /api/signatures/* (Signing endpoints)
│   │   │   ├── verification.py          # /api/verification/* (Verification endpoints)
│   │   │   ├── dashboard.py             # /api/dashboard/* (Summary metrics)
│   │   │   ├── analytics.py             # /api/analytics/* (Database-driven accuracy rates)
│   │   │   ├── logs.py                  # /api/logs/* (Audit logging)
│   │   │   └── settings.py              # /api/settings/* (System parameters)
│   │   ├── database/                    # SQLAlchemy Storage Layer
│   │   │   ├── models.py                # Signatures, Logs, QDSNonce, QDSVerifier, QDSRateLimit
│   │   │   └── session.py               # Session lifecycle & SQLite WAL initialization
│   │   ├── quantum/                     # Foundational Quantum Physics Subsystem
│   │   │   ├── teleportation.py         # Bell pair preparation, BSM & Pauli feed-forward
│   │   │   ├── density_matrix.py        # Purity, von Neumann entropy, Trace distance
│   │   │   ├── tomography.py            # Projective Pauli state tomography
│   │   │   ├── channels.py              # 6 Kraus channels (depolarizing, amplitude/phase damping)
│   │   │   ├── entanglement.py          # CHSH inequality test (S ≈ 2.8284)
│   │   │   ├── experiments.py           # No-cloning theorem & Intercept-Resend eavesdropping
│   │   │   ├── noise_models.py          # Aer noise models for quantum channel simulation
│   │   │   └── bloch.py                 # 3D Bloch sphere vector calculations
│   │   ├── schemas/                     # Pydantic Schemas & DTO Validation
│   │   │   └── schemas.py               # Typed request/response models
│   │   ├── services/                    # Background Services
│   │   │   └── seed_data.py             # Initial database seeder (labeled synthetic)
│   │   ├── config.py                    # Environment settings
│   │   └── main.py                      # FastAPI app initialization & CORS middleware
│   └── tests/                           # Pytest Automated Test Suite (130 Tests)
│       ├── test_qds.py                  # 17 QDS protocol lifecycle & threshold tests
│       ├── test_adversary.py            # 13 Attack vectors & detector tests
│       ├── test_analysis.py             # 24 Hoeffding, Monte Carlo & Benchmark tests
│       ├── test_teleportation.py        # 5 Quantum teleportation & fidelity tests
│       └── test_quantum_security.py     # 71 Physics lab, Kraus channels & tomography tests
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── KeyDistributionPage.tsx  # Interactive Bell teleportation & quantum memory viewer
│   │   │   ├── ForgeryAnalysisPage.tsx  # Recharts curves: bound vs empirical, sliders, ROC, export
│   │   │   ├── PerformancePage.tsx      # O(L) scaling, latency/memory curves, 2x2 confusion matrix
│   │   │   ├── SignatureGenPage.tsx     # Signature generation with L copies & SHA-256 token
│   │   │   ├── VerificationPage.tsx     # Projective verification, mismatch rate, thresholds
│   │   │   ├── AttackSimPage.tsx        # Adversary simulation, detector badges & noise injection
│   │   │   ├── PhysicsLabPage.tsx       # 8 Quantum physics experiments
│   │   │   ├── PqcComparisonPage.tsx    # QDS vs NIST PQC vs QKD architectural matrix
│   │   │   └── DashboardPage.tsx        # Real-time health & security metrics
│   │   ├── services/
│   │   │   └── api.ts                   # Complete REST client wrapper with strict TypeScript types
│   │   ├── types/
│   │   │   └── index.ts                 # Type definitions matching backend Pydantic models
│   │   ├── components/common/
│   │   │   ├── Sidebar.tsx              # Navigation bar with Lucide icons
│   │   │   └── Header.tsx               # Top status bar
│   │   ├── layouts/
│   │   │   └── MainLayout.tsx           # Glassmorphic shell layout
│   │   └── App.tsx                      # Client-side routing table
│   └── package.json                     # Vite, React 19, Recharts, Tailwind CSS
│
└── docs/
    ├── SIGNATURE_ALGORITHM.md           # Mathematical QDS protocol specification
    ├── ARCHITECTURE.md                  # Detailed system architecture (this document)
    ├── ATTACK_MODEL.md                  # Comprehensive cyber & quantum attack vectors
    ├── SECURITY_ANALYSIS.md             # Theoretical derivations, bounds, limits & SIH mapping
    └── QUANTUM_CONCEPTS.md              # Foundational quantum information theory notes
```

---

## 3. Communication Protocols & Core API Endpoints

### Quantum Digital Signature Protocol (`/api/qds/*`)
- `POST /api/qds/keygen`: Generates private key $(\text{basis}, \text{bit})$ and public quantum states from the 6 Pauli eigenstates.
- `POST /api/qds/distribute`: Teleports public key states to verifiers (Bob, Charlie) via Bell pairs with classical feedforward Pauli corrections.
- `POST /api/qds/sign`: Releases the classical private key string $\text{SK}_b$ cryptographically bound to the message via SHA-256.
- `POST /api/qds/verify`: Performs projective measurements on stored quantum states, computes empirical mismatch rate $m$, and compares against $s_a$ and $s_v$.
- `GET /api/qds/memory/{verifier_id}`: Retrieves quantum memory occupancy and state properties for a verifier.

### Theoretical Bounds & Benchmarks (`/api/analysis/*`)
- `GET /api/analysis/hoeffding`: Computes analytical Hoeffding bounds for forgery acceptance and honest false reject, returning documented assumptions.
- `POST /api/analysis/monte-carlo`: Runs vectorized Monte Carlo simulation with Wilson 95% confidence intervals and verifies bound invariance.
- `GET /api/analysis/aer-validation`: Cross-validates vectorized NumPy Born-rule sampling against Qiskit Aer statevector simulation.
- `GET /api/analysis/sweeps`: Generates full parameter sweeps ($vs\ L$, $vs\ s_a$, $vs\ \text{strategy}$, $vs\ \text{noise}$, and ROC curve).
- `GET /api/analysis/sweeps/export`: Exports parameter sweep datasets as downloadable CSV or JSON files.
- `GET /api/analysis/benchmarks`: Measures signing and verification execution time and memory scaling across varying key lengths $L$ and verifier counts $K$.
- `GET /api/analysis/confusion-matrix`: Executes real simulation runs across 5 attack vectors and honest traffic to calculate dynamic TP, FP, TN, FN, Accuracy, Precision, Recall, Specificity, and F1-Score.

### Adversary & Threat Simulation (`/api/attacks/*`)
- `POST /api/attacks/simulate`: Simulates specific attack scenarios (Random Guess, Measure & Guess, Impersonation, Channel Noise, Nonce Replay, Rate Limit Exceeded) and returns decision, mismatch rate, and specific detector fired (`threshold`, `nonce`, `rate-limit`, `authorization`).
