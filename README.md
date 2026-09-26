# Mentis-Q: Physics-Based Quantum Digital Signature (QDS) Security & Verification Framework

A research-grade, **physics- and mathematics-based Quantum Digital Signature (QDS)** verification, adversary simulation, and statistical concentration benchmarking framework developed for **Smart India Hackathon (SIH)**.

Built with **FastAPI, Qiskit Aer, React 19, Recharts, and Tailwind CSS**.

> ⚡ **CRITICAL THEORETICAL ASSURANCE: ZERO AI / HEURISTIC MACHINE LEARNING**  
> All threat detection, channel diagnostics, state verification, confidence intervals, and security metrics are derived **strictly and deterministically** from quantum mechanics, linear algebra, spectral analysis, and probability concentration bounds.
>
> ⚠️ **FOUNDATIONAL THEORETICAL NOTICE**:  
> **Information-theoretic security in Quantum Digital Signatures is established by published quantum cryptography theory** (Gottesman & Chuang 2001, Clarke et al. 2012, Arrazola & Neduvath 2014, Amiri et al. 2016). **This software framework simulates, benchmarks, and empirically validates these theoretical bounds against real quantum circuit simulation and statistical sampling; it does NOT mathematically prove theorems from first principles within its computational runtime.**

![Mentis-Q QDS Architecture](https://img.shields.io/badge/Architecture-100%25%20Physics%20Based-blue?style=for-the-badge)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Qiskit](https://img.shields.io/badge/Qiskit%20Aer-6929C4?style=for-the-badge&logo=qiskit)
![React](https://img.shields.io/badge/React%2019-20232A?style=for-the-badge&logo=react)
![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css)
![Pytest Status](https://img.shields.io/badge/Tests-130%2F130%20Passing-brightgreen?style=for-the-badge)

---

## 1. Protocol Architecture & Workflow

Mentis-Q implements an end-to-end multi-party Quantum Digital Signature scheme:

```
                            [ Alice (Signer) ]
                                    │
           ┌────────────────────────┴────────────────────────┐
           ▼                                                 ▼
[ Bell Pair Teleportation ]                       [ Classical Keygen ]
Public Keys: |ψ_{b,i}⟩ ∈ {Pauli Alphabet}         Private Keys: (basis, bit)
           │                                                 │
           ▼                                                 ▼
[ Verifier Quantum Memories ]                     [ Signature Release ]
Bob & Charlie store |ψ⟩ states                    Alice transmits (basis, bit) + SHA-256
           │                                                 │
           └────────────────────────┬────────────────────────┘
                                    ▼
                      [ Projective Verification ]
                  Measure stored states in claimed basis
                  Calculate Mismatch Rate: m = N_err / L
                                    │
               ┌────────────────────┴────────────────────┐
               ▼                                         ▼
         m ≤ s_a (Accept)                         m > s_a (Reject)
```

1. **Pauli Alphabet**: The six eigenstates of the Pauli operators ($\sigma_z, \sigma_x, \sigma_y$): $|0\rangle, |1\rangle, |+\rangle, |-\rangle, |+i\rangle, |-i\rangle$.
2. **Keygen**: For each message bit $b \in \{0, 1\}$, Alice draws $L$ random Pauli eigenstates. Private key = basis + bit string; Public key = $L$ quantum statevectors.
3. **QPKD Distribution via Teleportation**: Alice generates EPR Bell pairs with each verifier (Bob, Charlie). Public-key states are teleported using Bell State Measurements (BSM) with classical feedforward Pauli corrections ($I, X, Z, XZ$). Verifiers store received states in local quantum memory registries.
4. **Signing Protocol**: To sign a message $M$, Alice computes $H = \text{SHA-256}(M)$, binds bit $b$, and releases the classical private key string $\text{SK}_b$.
5. **Projective Verification**: Verifiers measure their stored states in the claimed bases, computing empirical mismatch rate $m = N_{\text{err}} / L$.
6. **Dual Thresholds**:
   - $m \le s_a$ ($0.100$): **ACCEPTED** (Valid signature).
   - $m > s_v$ ($0.250$): **REJECTED** (Attack detected).
   - $s_a < m \le s_v$: **MIDDLE ZONE DISPUTE** (Rejected to ensure verifier consensus).

---

## 2. Theoretical Security Bounds

- **Adversary Forgery Acceptance Bound**:
  $$P(\text{forgery accepted}) \le \exp\left(-2L(p_e - s_a)^2\right) \quad \text{for } p_e > s_a$$
- **Honest False Rejection Bound**:
  $$P(\text{false reject}) \le \exp\left(-2L(s_a - p_h)^2\right) \quad \text{for } p_h < s_a$$
- **Adversary Error Rates**:
  - *Random Guess*: $\mathbb{E}[m] = 0.50 \implies P(\text{forgery}) \le \exp(-0.32 L)$.
  - *Single-Basis Measure & Guess*: $\mathbb{E}[m] = 1/3 \approx 0.3333 \implies P(\text{forgery}) \le \exp(-0.1089 L)$.
  - *Optimal POVM Bound (Literature)*: $m_{\min} = \frac{1}{2}(1 - 1/\sqrt{3}) \approx 21.13\% > s_a$.

---

## 3. Directory Structure

```
Mentis-Q/
├── backend/
│   ├── app/
│   │   ├── qds/                         # Quantum Digital Signature Core Subsystem
│   │   │   ├── keygen.py                # 6 Pauli eigenstates & private/public keygen
│   │   │   ├── distribution.py          # Bell pair teleportation & memory registries
│   │   │   ├── signing.py               # Classical key release & SHA-256 binding
│   │   │   ├── verification.py          # Projective measurement & mismatch rate m
│   │   │   ├── thresholds.py            # Dual thresholds (s_a, s_v) & decision logic
│   │   │   └── adversary.py             # 5 Adversary attack vectors & detector engine
│   │   ├── analysis/                    # Theoretical Analysis & Benchmarking
│   │   │   ├── forgery.py               # Analytical Hoeffding bounds, Monte Carlo, Aer test
│   │   │   └── benchmarks.py            # O(L) complexity, latency/memory, confusion matrix
│   │   ├── api/                         # FastAPI REST Routes
│   │   │   ├── qds.py                   # /api/qds/* (Keygen, Distribute, Sign, Verify)
│   │   │   ├── analysis.py              # /api/analysis/* (Bounds, Sweeps, Exports, Benchmarks)
│   │   │   ├── attacks.py               # /api/attacks/* (Adversary simulation & detectors)
│   │   │   ├── physics_lab.py           # /api/physics-lab/* (Tomography, CHSH, Kraus noise)
│   │   │   └── signatures.py            # /api/signatures/* (Extended signing)
│   │   ├── database/                    # SQLAlchemy Storage Layer
│   │   │   └── models.py                # qds_nonces, qds_verifiers, qds_rate_limits
│   │   └── quantum/                     # Foundational Physics & Circuits
│   └── tests/                           # 130 Automated Pytest Tests (All Passing)
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── KeyDistributionPage.tsx  # 4-Stage Bell Teleportation & Memory Inspector
│   │   │   ├── ForgeryAnalysisPage.tsx  # Recharts Bound vs Empirical, Sliders, ROC & Export
│   │   │   ├── PerformancePage.tsx      # O(L) Scaling Curves & 2x2 Confusion Matrix Grid
│   │   │   ├── SignatureGenPage.tsx     # Signature Generation (L copies & SHA-256 token)
│   │   │   ├── VerificationPage.tsx     # Projective Verification (m, thresholds, detector)
│   │   │   └── AttackSimPage.tsx        # Attack Simulation & Detector Badges
│   │   ├── services/api.ts              # Typed REST API Client
│   │   └── types/index.ts               # Strict TypeScript Models
│
└── docs/
    ├── SIGNATURE_ALGORITHM.md           # Formal mathematical QDS protocol specification
    ├── ARCHITECTURE.md                  # Comprehensive system architecture & directory map
    ├── ATTACK_MODEL.md                  # Threat model & adversary vector derivations
    ├── SECURITY_ANALYSIS.md             # Theoretical derivations, results & SIH mapping
    └── QUANTUM_CONCEPTS.md              # Foundational quantum information theory notes
```

---

## 4. API Endpoints Reference

| Route | Method | Description |
|:---|:---:|:---|
| `/api/qds/keygen` | `POST` | Generates private key $(\text{basis}, \text{bit})$ and public quantum states from the 6 Pauli eigenstates. |
| `/api/qds/distribute` | `POST` | Teleports public key states to verifiers (Bob, Charlie) via Bell pairs with classical feedforward Pauli corrections. |
| `/api/qds/sign` | `POST` | Releases classical private key string $\text{SK}_b$ cryptographically bound to message digest via SHA-256. |
| `/api/qds/verify` | `POST` | Performs projective measurements on stored quantum states, computes empirical mismatch rate $m$, and compares against $s_a, s_v$. |
| `/api/qds/memory/{verifier_id}` | `GET` | Retrieves quantum memory occupancy and state properties for a verifier. |
| `/api/analysis/hoeffding` | `GET` | Computes analytical Hoeffding bounds for forgery acceptance and honest false reject with documented assumptions. |
| `/api/analysis/monte-carlo` | `POST` | Runs vectorized Monte Carlo simulation with Wilson 95% confidence intervals and verifies bound invariance. |
| `/api/analysis/aer-validation` | `GET` | Cross-validates vectorized NumPy Born-rule sampling against Qiskit Aer statevector simulation. |
| `/api/analysis/sweeps` | `GET` | Generates full parameter sweeps ($vs\ L$, $vs\ s_a$, $vs\ \text{strategy}$, $vs\ \text{noise}$, and ROC curve). |
| `/api/analysis/sweeps/export` | `GET` | Exports parameter sweep datasets as downloadable CSV or JSON files. |
| `/api/analysis/benchmarks` | `GET` | Measures signing and verification execution time and memory scaling across varying key lengths $L$ and verifier counts $K$. |
| `/api/analysis/confusion-matrix` | `GET` | Executes real simulation runs across 5 attack vectors and honest traffic to calculate dynamic TP, FP, TN, FN, Accuracy, Precision, Recall. |
| `/api/attacks/simulate` | `POST` | Simulates specific attack scenarios and returns decision, mismatch rate, and specific detector fired (`threshold`, `nonce`, `rate-limit`, `authorization`). |

---

## 5. Installation & Run Steps

### Prerequisites
- Python 3.10+ (tested on Python 3.14)
- Node.js 18+ and npm

### 1. Unified Launcher
To launch both backend and frontend concurrently:
```bash
python run.py
```
Or on Windows:
```powershell
.\start.ps1
```

### 2. Manual Setup

**Backend**:
```bash
cd backend
pip install -r requirements.txt
python -m pytest -v
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Frontend**:
```bash
cd frontend
npm install
npm run build
npm run dev
```

The frontend will be available at `http://localhost:5173` and the backend at `http://localhost:8000` (API docs at `/docs`).

---

## 6. Verification & Test Results

### Automated Test Suite Summary
```
============================== test session starts ==============================
collected 130 items

tests/test_adversary.py .............                                    [ 10%]
tests/test_analysis.py ........................                          [ 28%]
tests/test_qds.py .................                                      [ 41%]
tests/test_quantum_security.py ......................................... [ 73%]
..............................                                           [ 96%]
tests/test_teleportation.py .....                                        [100%]

======================= 130 passed in 10.18s =======================
```

### Frontend Code Quality
- **TypeScript**: `npx tsc -b` passes cleanly with **0 errors**.
- **Oxlint**: `npx oxlint` passes with **0 errors and 0 warnings**.
- **Production Build**: `npm run build` succeeds in **798ms**.

---

## 7. SIH Requirement Compliance & Verification Evidence

| SIH Requirement | Target Functionality | Implementing Files | Verification Evidence | Status |
|:---|:---|:---|:---|:---:|
| **QDS Alphabet** | Six Pauli eigenstates $\|0\rangle, \|1\rangle, \|+\rangle, \|-\rangle, \|+i\rangle, \|-i\rangle$ | `backend/app/qds/keygen.py` | `test_pauli_eigenstates_normalization`, `test_pauli_eigenstates_eigenvalues` | **PASS** |
| **Keygen Engine** | $L$ random Pauli states per bit $b \in \{0, 1\}$ | `backend/app/qds/keygen.py` | `test_keygen_lengths_and_structure` | **PASS** |
| **QPKD Distribution** | Bell pair generation, teleportation, Pauli correction | `backend/app/qds/distribution.py`, `backend/app/quantum/teleportation.py` | `test_noiseless_honest_teleportation_and_storage`, `test_two_verifier_distribution` | **PASS** |
| **Signing Protocol** | Classical private key release + SHA-256 binding | `backend/app/qds/signing.py` | `test_signing_structure_and_sha256_binding` | **PASS** |
| **Projective Verification** | Basis measurement on stored states, mismatch rate $m$ | `backend/app/qds/verification.py` | `test_honest_noiseless_signature_acceptance` ($m = 0.0, 100\%$ accept) | **PASS** |
| **Threshold Decision** | $s_a < s_v < 0.50$ dual thresholds & middle zone dispute | `backend/app/qds/thresholds.py` | `test_thresholds_middle_zone_rejection`, `test_thresholds_validation` | **PASS** |
| **Random Guess Attack** | Adversary mismatch $\mathbb{E}[m] = 0.50 > s_v$ | `backend/app/qds/adversary.py` | `test_random_guess_expected_mismatch_and_rejection` | **PASS** |
| **Measure & Guess** | Single & multi-basis POVM, literature bound cited | `backend/app/qds/adversary.py` | `test_single_basis_measure_and_guess`, `test_multi_basis_measure_and_guess_literature_bound` | **PASS** |
| **Impersonation Attack** | Attacker with zero key credentials | `backend/app/qds/adversary.py` | `test_impersonation_detection` | **PASS** |
| **Channel Attack** | Depolarizing, Pauli noise, Intercept-Resend | `backend/app/qds/adversary.py`, `backend/app/quantum/noise_models.py` | `test_intercept_resend_channel_attack` | **PASS** |
| **Replay Protection** | Real database nonce store, TTL window, single-use | `backend/app/qds/adversary.py`, `backend/app/database/models.py` | `test_nonce_one_time_use_and_second_submission_rejection` | **PASS** |
| **Rate Limiter / Auth** | Verifier token check, sliding-window rate limit | `backend/app/qds/adversary.py` | `test_unauthorized_token_rejection`, `test_sliding_window_rate_limit_lockout` | **PASS** |
| **Hoeffding Bounds** | $P(\text{forgery}) \le \exp(-2L(p_e - s_a)^2)$, false reject bound | `backend/app/analysis/forgery.py` | `test_hoeffding_forgery_formula_exact`, `test_hoeffding_false_reject_formula_exact` | **PASS** |
| **Monte Carlo Engine** | Vectorized Born-rule sampling, Wilson CI, bound invariant | `backend/app/analysis/forgery.py` | `test_empirical_rate_does_not_exceed_hoeffding_bound`, `test_wilson_confidence_interval_bounds` | **PASS** |
| **Aer Validation** | NumPy sampling cross-validated against Qiskit Aer | `backend/app/analysis/forgery.py` | `test_born_rule_sampling_validated_against_aer` | **PASS** |
| **Sweeps & Export** | Sweeps vs $L, s_a, \text{strategy}, \text{noise}$, ROC, CSV/JSON | `backend/app/analysis/forgery.py`, `backend/app/api/analysis.py` | `test_sweep_forgery_vs_L_strictly_decreasing`, `test_roc_curve_and_auc`, `test_csv_export_format` | **PASS** |
| **Performance Benchmarks** | $O(L)$ latency & memory scaling, linear regression fit | `backend/app/analysis/benchmarks.py` | `test_benchmarks_linear_complexity_O_L` | **PASS** |
| **Real Confusion Matrix** | Dynamic TP, FP, TN, FN, Accuracy, Precision, Recall | `backend/app/analysis/benchmarks.py` | `test_confusion_matrix_metrics_are_computed_not_constants` | **PASS** |
| **Frontend UI (Step 5)** | 3 New pages, Recharts curves, Sliders, Detector badges | `frontend/src/pages/*`, `frontend/src/services/api.ts` | `tsc -b` clean (0 errors), `oxlint` clean (0 warnings), `npm run build` (built in 798ms) | **PASS** |
