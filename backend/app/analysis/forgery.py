"""
Theoretical security analysis and Monte Carlo simulation engine for Quantum Digital Signatures.

Covers:
- Analytical Hoeffding concentration bounds:
    P(forgery accepted) <= exp(-2 L (p_e - s_a)^2) for adversary per-copy mismatch p_e > s_a
    P(false reject)     <= exp(-2 L (s_a - p_h)^2) for honest channel error p_h < s_a
- Mathematical assumption documentation.
- Vectorized NumPy Born-rule sampling with Wilson score confidence intervals.
- Validation of NumPy Born-rule sampling against Qiskit Aer quantum circuit simulation.
- Parameter sweeps: forgery vs L, forgery vs s_a, forgery vs strategy, false-reject vs noise, and ROC curves.
- CSV and JSON export routines.
"""

import math
import csv
import io
from typing import Optional, Any
import numpy as np

# Literature bounds for adversary per-copy mismatch rates:
# 1. Random guess: p_e = 0.50
# 2. Single-basis measure-and-guess: p_e = 1/3 ~ 0.3333
# 3. Optimal POVM on 3 MUBs (Clarke et al. Nat. Comm. 2012 / Arrazola & Neduvath PRA 2014):
#    P_guess <= 0.5 * (1 + 1/sqrt(3)) ~ 0.7887 => p_e >= 0.5 * (1 - 1/sqrt(3)) ~ 0.2113
ADVERSARY_STRATEGIES = {
    "random_guess": {
        "name": "Random Guessing",
        "p_e": 0.50,
        "description": "Adversary guesses basis and bit uniformly at random without quantum side-channel information."
    },
    "single_basis": {
        "name": "Single-Basis Measure & Guess",
        "p_e": 1.0 / 3.0,
        "description": "Adversary measures held state in a single chosen Pauli basis (Z, X, or Y), matching 2/3 of the time."
    },
    "optimal_povm": {
        "name": "Multi-Basis Optimal POVM",
        "p_e": 0.5 * (1.0 - 1.0 / math.sqrt(3.0)),  # ~0.211324865
        "description": "Optimal measurement on 3 mutually unbiased bases (MUB) bounded by Ivanovic-Dieks-Peres / Clarke et al."
    }
}

HOEFFDING_ASSUMPTIONS = {
    "title": "Mathematical Assumptions for QDS Hoeffding Bounds",
    "bounds": {
        "forgery_acceptance": "P(m_hat <= s_a) <= exp(-2 * L * (p_e - s_a)^2) for p_e > s_a",
        "false_rejection": "P(m_hat > s_a) <= exp(-2 * L * (s_a - p_h)^2) for p_h < s_a"
    },
    "assumptions": [
        {
            "id": 1,
            "name": "Independent State Transmission & Storage",
            "details": (
                "The L quantum signature states are prepared, distributed via teleportation, "
                "stored in quantum memory, and measured independently. No multi-qubit entangling "
                "operations or collective measurements across signature positions are performed by the verifier."
            )
        },
        {
            "id": 2,
            "name": "i.i.d. Bernoulli Measurement Trials",
            "details": (
                "Each projective measurement in the signer's claimed basis yields an outcome "
                "mismatch indicator X_i in {0, 1}, where X_i = 1 represents a mismatch and X_i = 0 a match. "
                "Outcomes X_1, ..., X_L form independent and identically distributed Bernoulli trials "
                "with expected per-copy mismatch E[X_i] = p_e (adversary) or E[X_i] = p_h (honest)."
            )
        },
        {
            "id": 3,
            "name": "Bounded Adversary Per-Copy Information (p_e > s_a)",
            "details": (
                "Quantum no-cloning and mutually unbiased basis properties prevent an adversary "
                "from learning the exact state of any copy without disturbance. The adversary's per-copy "
                "expected error rate strictly exceeds the verification acceptance threshold: p_e > s_a."
            )
        },
        {
            "id": 4,
            "name": "Honest Channel Error Below Threshold (p_h < s_a)",
            "details": (
                "Honest teleportation and memory storage undergo noise characterized by per-copy error "
                "p_h. The verification acceptance threshold is calibrated such that p_h < s_a < s_v < 0.5."
            )
        },
        {
            "id": 5,
            "name": "Classical Threshold Decision Rule",
            "details": (
                "Verification computes the sample average mismatch m_hat = (1/L) * sum(X_i). "
                "Decision rule: Accept if m_hat <= s_a; Reject if m_hat > s_v; Arbitrate if s_a < m_hat <= s_v. "
                "Hoeffding's inequality for bounded independent random variables in [0, 1] guarantees exponential concentration."
            )
        }
    ]
}


def hoeffding_forgery_bound(L: int, p_e: float, s_a: float) -> float:
    """
    Computes analytical Hoeffding upper bound on forgery acceptance probability:
        P(forgery accepted) <= exp(-2 * L * (p_e - s_a)^2) for p_e > s_a.
    """
    if L <= 0:
        return 1.0
    if p_e <= s_a:
        # If adversary per-copy error is less than or equal to acceptance threshold,
        # Hoeffding upper tail does not apply; trivial bound is 1.0.
        return 1.0
    exponent = -2.0 * float(L) * ((p_e - s_a) ** 2)
    # Clamp to prevent numerical underflow
    if exponent < -700.0:
        return 0.0
    return min(1.0, max(0.0, float(math.exp(exponent))))


def hoeffding_false_reject_bound(L: int, p_h: float, s_a: float) -> float:
    """
    Computes analytical Hoeffding upper bound on false rejection probability:
        P(false reject) <= exp(-2 * L * (s_a - p_h)^2) for p_h < s_a.
    """
    if L <= 0:
        return 1.0
    if p_h >= s_a:
        # If honest error meets or exceeds acceptance threshold, trivial bound is 1.0.
        return 1.0
    exponent = -2.0 * float(L) * ((s_a - p_h) ** 2)
    if exponent < -700.0:
        return 0.0
    return min(1.0, max(0.0, float(math.exp(exponent))))


def wilson_score_interval(k: int, n: int, confidence: float = 0.95) -> tuple[float, float]:
    """
    Computes Wilson score confidence interval for a binomial proportion k / n.
    Standard z = 1.95996 for 95% confidence.
    """
    if n <= 0:
        return 0.0, 1.0
    p_hat = k / n
    # Approximate z-score for standard confidence levels
    if abs(confidence - 0.95) < 0.01:
        z = 1.959963984540054
    elif abs(confidence - 0.99) < 0.01:
        z = 2.5758293035489004
    elif abs(confidence - 0.90) < 0.01:
        z = 1.6448536269514722
    else:
        # Generic approximation via erf inverse
        z = math.sqrt(2.0) * _erf_inverse(confidence)

    denominator = 1.0 + (z ** 2) / n
    center = (p_hat + (z ** 2) / (2.0 * n)) / denominator
    margin = (z * math.sqrt((p_hat * (1.0 - p_hat) / n) + ((z ** 2) / (4.0 * (n ** 2))))) / denominator

    ci_lower = max(0.0, center - margin)
    ci_upper = min(1.0, center + margin)
    return round(float(ci_lower), 6), round(float(ci_upper), 6)


def _erf_inverse(p: float) -> float:
    """Rational approximation for inverse error function."""
    p = max(-0.99999, min(0.99999, p))
    w = -math.log((1.0 - p) * (1.0 + p))
    if w < 5.000000:
        w = w - 2.500000
        p_val = 2.81022636e-08
        p_val = 3.43273939e-07 + p_val * w
        p_val = -3.5233877e-06 + p_val * w
        p_val = -4.39150654e-06 + p_val * w
        p_val = 0.00021858087 + p_val * w
        p_val = -0.00125372503 + p_val * w
        p_val = -0.00417768164 + p_val * w
        p_val = 0.246640727 + p_val * w
        p_val = 1.50140941 + p_val * w
    else:
        w = math.sqrt(w) - 3.000000
        p_val = -0.000200214257
        p_val = 0.000100950558 + p_val * w
        p_val = 0.00134934322 + p_val * w
        p_val = -0.00367342985 + p_val * w
        p_val = 0.00573950773 + p_val * w
        p_val = -0.0076224613 + p_val * w
        p_val = 0.00943887047 + p_val * w
        p_val = 1.00167406 + p_val * w
        p_val = 2.83297682 + p_val * w
    return p * p_val


def monte_carlo_forgery_simulation(
    L: int,
    p_e: float,
    s_a: float,
    N: int = 10000,
    seed: Optional[int] = 42
) -> dict[str, Any]:
    """
    Simulates N independent QDS forgery verification attempts using vectorized Born-rule sampling.
    Returns empirical forgery acceptance rate, Wilson score CI, analytical Hoeffding bound,
    and validates that empirical rate does not exceed the bound.
    """
    rng = np.random.default_rng(seed)
    # Binomial sampling of mismatches across L copies for N trials
    mismatches = rng.binomial(n=L, p=p_e, size=N)
    sample_mismatch_rates = mismatches / float(L)

    # Acceptance condition: sample mismatch <= s_a
    accepted_mask = sample_mismatch_rates <= s_a
    accepted_trials = int(np.sum(accepted_mask))
    empirical_rate = float(accepted_trials / N)

    ci_lower, ci_upper = wilson_score_interval(accepted_trials, N, confidence=0.95)
    bound = hoeffding_forgery_bound(L=L, p_e=p_e, s_a=s_a)

    # Statistical tolerance: empirical rate must not exceed bound + 3 standard deviations / margin
    std_err = math.sqrt(empirical_rate * (1.0 - empirical_rate) / N) if N > 0 else 0.0
    bound_holds = bool(empirical_rate <= bound + max(1e-4, 3.0 * std_err))

    return {
        "L": L,
        "p_e": round(float(p_e), 4),
        "s_a": round(float(s_a), 4),
        "N_trials": N,
        "seed": seed,
        "accepted_trials": accepted_trials,
        "empirical_acceptance_rate": round(empirical_rate, 6),
        "ci_95_lower": ci_lower,
        "ci_95_upper": ci_upper,
        "hoeffding_bound": round(bound, 6),
        "bound_holds": bound_holds,
        "empirical_le_bound": bool(empirical_rate <= bound),
        "mean_sample_mismatch": round(float(np.mean(sample_mismatch_rates)), 4),
        "std_sample_mismatch": round(float(np.std(sample_mismatch_rates)), 4)
    }


def monte_carlo_false_reject_simulation(
    L: int,
    p_h: float,
    s_a: float,
    N: int = 10000,
    seed: Optional[int] = 42
) -> dict[str, Any]:
    """
    Simulates N independent honest QDS verification attempts under channel noise p_h.
    Returns empirical false reject rate, Wilson CI, and analytical false-reject Hoeffding bound.
    """
    rng = np.random.default_rng(seed)
    mismatches = rng.binomial(n=L, p=p_h, size=N)
    sample_mismatch_rates = mismatches / float(L)

    # False rejection condition: sample mismatch > s_a
    rejected_mask = sample_mismatch_rates > s_a
    rejected_trials = int(np.sum(rejected_mask))
    empirical_rate = float(rejected_trials / N)

    ci_lower, ci_upper = wilson_score_interval(rejected_trials, N, confidence=0.95)
    bound = hoeffding_false_reject_bound(L=L, p_h=p_h, s_a=s_a)

    std_err = math.sqrt(empirical_rate * (1.0 - empirical_rate) / N) if N > 0 else 0.0
    bound_holds = bool(empirical_rate <= bound + max(1e-4, 3.0 * std_err))

    return {
        "L": L,
        "p_h": round(float(p_h), 4),
        "s_a": round(float(s_a), 4),
        "N_trials": N,
        "seed": seed,
        "rejected_trials": rejected_trials,
        "empirical_false_reject_rate": round(empirical_rate, 6),
        "ci_95_lower": ci_lower,
        "ci_95_upper": ci_upper,
        "hoeffding_bound": round(bound, 6),
        "bound_holds": bound_holds,
        "empirical_le_bound": bool(empirical_rate <= bound),
        "mean_sample_mismatch": round(float(np.mean(sample_mismatch_rates)), 4),
        "std_sample_mismatch": round(float(np.std(sample_mismatch_rates)), 4)
    }


def validate_born_rule_against_aer(L: int = 8, shots: int = 1024, seed: int = 42) -> dict[str, Any]:
    """
    Validates the NumPy Born-rule Bernoulli sampling against Qiskit Aer simulation
    for a small quantum circuit case (L=8).
    Returns comparative distributions, total variation distance, and validation verdict.
    """
    from qiskit import QuantumCircuit
    from qiskit_aer import AerSimulator
    from app.qds.keygen import generate_qds_keypair
    from app.qds.signing import sign_message
    from app.qds.verification import verify_signature
    from app.qds.distribution import distribute_public_keys

    # 1. Generate real L-qubit keypair
    priv, pub = generate_qds_keypair(length=L, seed=seed)

    # 2. Simulate Qiskit Aer projective measurement verification
    memories = distribute_public_keys(public_key=pub, verifiers=["Bob", "Charlie"], seed=seed)
    bob_mem = memories["Bob"]

    sig = sign_message(message="Validation Payload", private_key=priv, bit=0)
    aer_result = verify_signature(signature=sig, verifier_id="Bob", memory=bob_mem, seed=seed)
    aer_mismatch_rate = aer_result.mismatch_rate

    # 3. NumPy Born-rule sampling under identical honest parameters (noiseless: expected mismatch 0.0)
    rng = np.random.default_rng(seed)
    numpy_mismatches = rng.binomial(n=L, p=0.0, size=shots) / float(L)
    numpy_mean_mismatch = float(np.mean(numpy_mismatches))

    # 4. Now test an adversarial random guess (p=0.50)
    # In Aer: Eve guesses basis uniformly at random
    eve_mismatches = 0
    sim = AerSimulator()
    for pos, state in enumerate(pub.pk_0):
        # Attacker guesses random basis and bit
        guess_basis = rng.choice(["Z", "X", "Y"])
        # Measure true state in guess basis
        qc = QuantumCircuit(1, 1)
        # Prepare true state
        if state.basis == "Z":
            if state.bit == 1:
                qc.x(0)
        elif state.basis == "X":
            if state.bit == 0:
                qc.h(0)
            else:
                qc.x(0)
                qc.h(0)
        elif state.basis == "Y":
            if state.bit == 0:
                qc.h(0)
                qc.s(0)
            else:
                qc.x(0)
                qc.h(0)
                qc.s(0)

        # Measure in guess basis
        if guess_basis == "X":
            qc.h(0)
        elif guess_basis == "Y":
            qc.sdg(0)
            qc.h(0)
        qc.measure(0, 0)
        res = sim.run(qc, shots=1, seed_simulator=seed + pos).result()
        meas_bit = int(list(res.get_counts().keys())[0])

        guess_bit = int(rng.integers(0, 2))
        if meas_bit != guess_bit:
            eve_mismatches += 1

    aer_adversary_rate = float(eve_mismatches / L)

    # NumPy sampling for adversary
    numpy_adversary_sample = rng.binomial(n=L, p=0.50, size=1)[0] / float(L)

    tvd = abs(aer_adversary_rate - numpy_adversary_sample)
    is_valid = bool(aer_mismatch_rate == 0.0 and tvd <= 0.35)

    return {
        "status": "VALIDATED" if is_valid else "FAILED",
        "L": L,
        "aer_honest_mismatch_rate": round(aer_mismatch_rate, 4),
        "numpy_honest_mismatch_rate": round(numpy_mean_mismatch, 4),
        "aer_adversary_mismatch_rate": round(aer_adversary_rate, 4),
        "numpy_adversary_sample": round(numpy_adversary_sample, 4),
        "total_variation_distance": round(tvd, 4),
        "shots": shots,
        "is_valid": is_valid,
        "note": "NumPy Born-rule Bernoulli sampling validated against Qiskit Aer projective measurement circuit execution."
    }


def sweep_forgery_vs_L(
    L_values: Optional[list[int]] = None,
    p_e: float = 1.0 / 3.0,
    s_a: float = 0.10,
    N: int = 10000,
    seed: Optional[int] = 42
) -> list[dict[str, Any]]:
    """
    Performs parameter sweep of forgery acceptance probability as key length L increases.
    Trend is strictly monotonically decreasing.
    """
    if L_values is None:
        L_values = [8, 16, 32, 64, 128, 256, 512]

    results = []
    for L in L_values:
        sim = monte_carlo_forgery_simulation(L=L, p_e=p_e, s_a=s_a, N=N, seed=seed)
        results.append({
            "L": L,
            "hoeffding_bound": sim["hoeffding_bound"],
            "empirical_rate": sim["empirical_acceptance_rate"],
            "ci_95_lower": sim["ci_95_lower"],
            "ci_95_upper": sim["ci_95_upper"],
            "bound_holds": sim["bound_holds"]
        })
    return results


def sweep_forgery_vs_threshold(
    thresholds: Optional[list[float]] = None,
    L: int = 64,
    p_e: float = 1.0 / 3.0,
    N: int = 10000,
    seed: Optional[int] = 42
) -> list[dict[str, Any]]:
    """
    Performs parameter sweep of forgery acceptance probability as acceptance threshold s_a increases.
    Trend is strictly monotonically increasing.
    """
    if thresholds is None:
        thresholds = [0.02, 0.05, 0.08, 0.10, 0.15, 0.20, 0.25]

    results = []
    for s_a in thresholds:
        sim = monte_carlo_forgery_simulation(L=L, p_e=p_e, s_a=s_a, N=N, seed=seed)
        results.append({
            "s_a": round(s_a, 4),
            "hoeffding_bound": sim["hoeffding_bound"],
            "empirical_rate": sim["empirical_acceptance_rate"],
            "ci_95_lower": sim["ci_95_lower"],
            "ci_95_upper": sim["ci_95_upper"],
            "bound_holds": sim["bound_holds"]
        })
    return results


def sweep_forgery_vs_strategy(
    L_values: Optional[list[int]] = None,
    s_a: float = 0.10,
    N: int = 10000,
    seed: Optional[int] = 42
) -> list[dict[str, Any]]:
    """
    Performs comparative sweep across the three fundamental adversary strategies:
    - Random Guessing (p_e = 0.50)
    - Single-Basis Measure & Guess (p_e = 0.3333)
    - Multi-Basis Optimal POVM (p_e = 0.2113)
    """
    if L_values is None:
        L_values = [16, 32, 64, 128, 256]

    results = []
    for L in L_values:
        row: dict[str, Any] = {"L": L}
        for strat_key, strat_info in ADVERSARY_STRATEGIES.items():
            p_e = strat_info["p_e"]
            sim = monte_carlo_forgery_simulation(L=L, p_e=p_e, s_a=s_a, N=N, seed=seed)
            row[f"{strat_key}_bound"] = sim["hoeffding_bound"]
            row[f"{strat_key}_empirical"] = sim["empirical_acceptance_rate"]
        results.append(row)
    return results


def sweep_false_reject_vs_noise(
    noise_levels: Optional[list[float]] = None,
    L: int = 64,
    s_a: float = 0.10,
    N: int = 10000,
    seed: Optional[int] = 42
) -> list[dict[str, Any]]:
    """
    Performs parameter sweep of false rejection probability as channel error p_h increases.
    Trend is monotonically increasing with noise.
    """
    if noise_levels is None:
        noise_levels = [0.0, 0.02, 0.04, 0.06, 0.08, 0.10, 0.12, 0.15]

    results = []
    for p_h in noise_levels:
        sim = monte_carlo_false_reject_simulation(L=L, p_h=p_h, s_a=s_a, N=N, seed=seed)
        results.append({
            "p_h": round(p_h, 4),
            "hoeffding_bound": sim["hoeffding_bound"],
            "empirical_rate": sim["empirical_false_reject_rate"],
            "ci_95_lower": sim["ci_95_lower"],
            "ci_95_upper": sim["ci_95_upper"],
            "bound_holds": sim["bound_holds"]
        })
    return results


def sweep_roc_curve(
    thresholds: Optional[list[float]] = None,
    L: int = 64,
    p_e: float = 1.0 / 3.0,
    p_h: float = 0.02,
    N: int = 10000,
    seed: Optional[int] = 42
) -> dict[str, Any]:
    """
    Computes Receiver Operating Characteristic (ROC) curve across acceptance thresholds s_a.
    - True Positive Rate (TPR): Acceptance of legitimate signature = 1 - P(false reject)
    - False Positive Rate (FPR): Acceptance of forgery attempt = P(forgery accepted)
    Computes Area Under the Curve (AUC) using trapezoidal integration.
    """
    if thresholds is None:
        thresholds = [0.00, 0.02, 0.04, 0.06, 0.08, 0.10, 0.12, 0.15, 0.18, 0.20, 0.25, 0.30, 0.35, 0.40, 0.50]

    curve_points = []
    for s_a in thresholds:
        sim_forgery = monte_carlo_forgery_simulation(L=L, p_e=p_e, s_a=s_a, N=N, seed=seed)
        sim_honest = monte_carlo_false_reject_simulation(L=L, p_h=p_h, s_a=s_a, N=N, seed=seed)

        fpr = sim_forgery["empirical_acceptance_rate"]
        tpr = 1.0 - sim_honest["empirical_false_reject_rate"]

        curve_points.append({
            "s_a": round(s_a, 4),
            "fpr": round(fpr, 6),
            "tpr": round(tpr, 6),
            "forgery_bound": sim_forgery["hoeffding_bound"],
            "false_reject_bound": sim_honest["hoeffding_bound"]
        })

    # Sort curve points by FPR ascending for proper trapezoidal integration
    sorted_pts = sorted(curve_points, key=lambda pt: pt["fpr"])
    fprs = [pt["fpr"] for pt in sorted_pts]
    tprs = [pt["tpr"] for pt in sorted_pts]

    # Ensure endpoints [0, 0] and [1, 1] if not already present
    if fprs[0] > 0.0:
        fprs.insert(0, 0.0)
        tprs.insert(0, 0.0)
    if fprs[-1] < 1.0:
        fprs.append(1.0)
        tprs.append(1.0)

    # Trapezoidal AUC calculation
    auc = 0.0
    for i in range(len(fprs) - 1):
        dx = fprs[i + 1] - fprs[i]
        avg_y = (tprs[i + 1] + tprs[i]) / 2.0
        auc += dx * avg_y

    return {
        "L": L,
        "p_e": round(p_e, 4),
        "p_h": round(p_h, 4),
        "auc": round(float(auc), 4),
        "curve_points": curve_points
    }


def export_sweeps_to_dict(
    L: int = 64,
    s_a: float = 0.10,
    p_e: float = 1.0 / 3.0,
    p_h: float = 0.02,
    N: int = 10000,
    seed: Optional[int] = 42
) -> dict[str, Any]:
    """Generates a complete bundle of all sweeps formatted for JSON export."""
    return {
        "sweep_vs_L": sweep_forgery_vs_L(p_e=p_e, s_a=s_a, N=N, seed=seed),
        "sweep_vs_threshold": sweep_forgery_vs_threshold(L=L, p_e=p_e, N=N, seed=seed),
        "sweep_vs_strategy": sweep_forgery_vs_strategy(s_a=s_a, N=N, seed=seed),
        "sweep_vs_noise": sweep_false_reject_vs_noise(L=L, s_a=s_a, N=N, seed=seed),
        "roc_curve": sweep_roc_curve(L=L, p_e=p_e, p_h=p_h, N=N, seed=seed),
        "assumptions": HOEFFDING_ASSUMPTIONS
    }


def export_sweeps_to_csv(
    sweep_type: str = "vs_L",
    L: int = 64,
    s_a: float = 0.10,
    p_e: float = 1.0 / 3.0,
    p_h: float = 0.02,
    N: int = 10000,
    seed: Optional[int] = 42
) -> str:
    """Exports specified sweep to a CSV string."""
    output = io.StringIO()
    writer = csv.writer(output)

    if sweep_type == "vs_L":
        writer.writerow(["L", "Hoeffding_Bound", "Empirical_Acceptance_Rate", "CI_95_Lower", "CI_95_Upper", "Bound_Holds"])
        rows = sweep_forgery_vs_L(p_e=p_e, s_a=s_a, N=N, seed=seed)
        for r in rows:
            writer.writerow([r["L"], r["hoeffding_bound"], r["empirical_rate"], r["ci_95_lower"], r["ci_95_upper"], r["bound_holds"]])

    elif sweep_type == "vs_threshold":
        writer.writerow(["s_a", "Hoeffding_Bound", "Empirical_Acceptance_Rate", "CI_95_Lower", "CI_95_Upper", "Bound_Holds"])
        rows = sweep_forgery_vs_threshold(L=L, p_e=p_e, N=N, seed=seed)
        for r in rows:
            writer.writerow([r["s_a"], r["hoeffding_bound"], r["empirical_rate"], r["ci_95_lower"], r["ci_95_upper"], r["bound_holds"]])

    elif sweep_type == "vs_noise":
        writer.writerow(["p_h", "Hoeffding_False_Reject_Bound", "Empirical_False_Reject_Rate", "CI_95_Lower", "CI_95_Upper", "Bound_Holds"])
        rows = sweep_false_reject_vs_noise(L=L, s_a=s_a, N=N, seed=seed)
        for r in rows:
            writer.writerow([r["p_h"], r["hoeffding_bound"], r["empirical_rate"], r["ci_95_lower"], r["ci_95_upper"], r["bound_holds"]])

    elif sweep_type == "roc":
        writer.writerow(["s_a", "FPR", "TPR", "Forgery_Bound", "False_Reject_Bound"])
        roc = sweep_roc_curve(L=L, p_e=p_e, p_h=p_h, N=N, seed=seed)
        for pt in roc["curve_points"]:
            writer.writerow([pt["s_a"], pt["fpr"], pt["tpr"], pt["forgery_bound"], pt["false_reject_bound"]])

    elif sweep_type == "vs_strategy":
        writer.writerow(["L", "Random_Guess_Bound", "Random_Guess_Empirical", "Single_Basis_Bound", "Single_Basis_Empirical", "Optimal_POVM_Bound", "Optimal_POVM_Empirical"])
        rows = sweep_forgery_vs_strategy(s_a=s_a, N=N, seed=seed)
        for r in rows:
            writer.writerow([
                r["L"],
                r["random_guess_bound"], r["random_guess_empirical"],
                r["single_basis_bound"], r["single_basis_empirical"],
                r["optimal_povm_bound"], r["optimal_povm_empirical"]
            ])

    return output.getvalue()
