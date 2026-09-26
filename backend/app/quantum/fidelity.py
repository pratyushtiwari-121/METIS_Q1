"""
Quantum State Fidelity, Measurement Deviation (TVD), and Threat Scoring Engine.

THREAT SCORE FORMULA (documented and implemented consistently)
--------------------------------------------------------------
T = 0.35·(1 - F) + 0.35·min(1, 2·Δ) + 0.30·AttackPenalty

Where:
    F             = quantum state fidelity ∈ [0, 1]
    Δ             = Total Variation Distance (TVD) ∈ [0, 1]
    AttackPenalty = normalized sum of attack-type flags ∈ [0, 1]

AttackPenalty breakdown (capped at 1.0 before the 0.30 weight):
    +0.45  if is_replay         (highest — reused nonce/ID is unambiguous)
    +0.40  if is_unauthorized   (unauthorized verifier probe)
    +0.35  if has_tampering     (quantum state modified)
    +0.30·noise_intensity  if noise present (proportional)

Threat Level Classification (HEURISTIC — not a cryptographic proof):
    T < 0.30   → LOW    → "LEGITIMATE"
    T < 0.60   → MEDIUM → "ATTACK DETECTED"
    T ≥ 0.60   → HIGH   → "ATTACK DETECTED"

DISCLAIMER
----------
The threat level is a heuristic classification based on statistical evidence.
It is NOT a formal cryptographic security guarantee or information-theoretic proof.
"""
import cmath
import math
from app.schemas.schemas import StateVectorInfo


def compute_state_fidelity(state1: StateVectorInfo, state2: StateVectorInfo) -> float:
    """
    Computes exact pure-state quantum fidelity:

        F(|ψ₁⟩, |ψ₂⟩) = |⟨ψ₁|ψ₂⟩|²
                       = |α₁* α₂ + β₁* β₂|²

    Parameters
    ----------
    state1, state2 : StateVectorInfo objects representing normalized pure states.

    Returns
    -------
    float in [0.0, 1.0].
      F ≈ 1.0  →  identical states
      F ≈ 0.0  →  orthogonal states (maximum distinguishability)
    """
    c_alpha1 = complex(state1.alpha.real, state1.alpha.imag)
    c_beta1 = complex(state1.beta.real, state1.beta.imag)
    c_alpha2 = complex(state2.alpha.real, state2.alpha.imag)
    c_beta2 = complex(state2.beta.real, state2.beta.imag)

    # Normalize vectors to eliminate rounding artifacts
    norm1 = math.sqrt(abs(c_alpha1) ** 2 + abs(c_beta1) ** 2)
    norm2 = math.sqrt(abs(c_alpha2) ** 2 + abs(c_beta2) ** 2)
    if norm1 > 0:
        c_alpha1 /= norm1
        c_beta1 /= norm1
    if norm2 > 0:
        c_alpha2 /= norm2
        c_beta2 /= norm2

    # Inner product ⟨ψ₁|ψ₂⟩ = conj(α₁)·α₂ + conj(β₁)·β₂
    inner_prod = (c_alpha1.conjugate() * c_alpha2) + (c_beta1.conjugate() * c_beta2)
    fidelity = abs(inner_prod) ** 2

    # Clamp to [0.0, 1.0] to guard against floating-point inaccuracies
    return max(0.0, min(1.0, round(float(fidelity), 4)))


def compute_measurement_deviation(
    expected_dist: dict[str, float],
    observed_dist: dict[str, float],
) -> float:
    """
    Computes the Total Variation Distance (TVD) between expected and observed
    measurement probability distributions.

        TVD = 0.5 · Σᵢ |P_exp(i) - P_obs(i)|

    TVD ∈ [0.0, 1.0]:
        0.0  →  distributions are identical
        1.0  →  distributions are completely disjoint

    Parameters
    ----------
    expected_dist : dict mapping outcome strings to expected probabilities.
    observed_dist : dict mapping outcome strings to observed probabilities.

    Returns
    -------
    float TVD ∈ [0.0, 1.0], rounded to 4 decimal places.
    """
    all_keys = set(expected_dist.keys()).union(set(observed_dist.keys()))
    if not all_keys:
        return 0.0

    total_diff = sum(
        abs(expected_dist.get(k, 0.0) - observed_dist.get(k, 0.0))
        for k in all_keys
    )
    tvd = 0.5 * total_diff
    return max(0.0, min(1.0, round(float(tvd), 4)))


def compute_qber(expected_bits: str, observed_bits: str) -> float:
    """
    Computes Quantum Bit Error Rate (QBER):
        QBER = (Number of differing bits) / (Total compared bits)
    Range: [0.0, 1.0]
    """
    if not expected_bits or not observed_bits:
        return 0.0
    min_len = min(len(expected_bits), len(observed_bits))
    if min_len == 0:
        return 0.0
    errors = sum(1 for i in range(min_len) if expected_bits[i] != observed_bits[i])
    return round(float(errors / min_len), 4)


def compute_threat_score(
    fidelity: float,
    deviation: float,
    is_replay: bool = False,
    is_unauthorized: bool = False,
    noise_intensity: float = 0.0,
    has_tampering: bool = False,
) -> tuple[float, str, str]:
    """
    Calculates a normalized threat score T ∈ [0.0, 1.0], threat category,
    and final verification decision.

    Formula (consistent across backend, frontend, and documentation):
    ---------------------------------------------------------------
    T = 0.35·(1 - F)
      + 0.35·min(1.0, 2·Δ)
      + 0.30·min(1.0, AttackPenalty)

    AttackPenalty = replay(0.45) + unauthorized(0.40) + tampering(0.35) + noise(0.30·η)

    Parameters
    ----------
    fidelity         : State fidelity F ∈ [0, 1].
    deviation        : TVD Δ ∈ [0, 1].
    is_replay        : True if nonce/signature ID was reused.
    is_unauthorized  : True if verifier is not authorized.
    noise_intensity  : Noise level η ∈ [0, 1].
    has_tampering    : True if quantum state was modified.

    Returns
    -------
    (threat_score, threat_level, decision)
        threat_score : float ∈ [0.0, 1.0]
        threat_level : "LOW" | "MEDIUM" | "HIGH"
        decision     : "LEGITIMATE" | "ATTACK DETECTED"

    DISCLAIMER: This classification is a HEURISTIC RISK INDICATOR based on
    statistical evidence. It is not a formal cryptographic security proof.
    """
    # Component 1: fidelity drop penalty (weight 0.35)
    fidelity_penalty = max(0.0, 1.0 - fidelity)

    # Component 2: statistical deviation penalty (weight 0.35)
    # Multiply TVD by 2 to give full weight at Δ=0.5 (typical mid-range)
    deviation_penalty = min(1.0, deviation * 2.0)

    # Component 3: attack-type penalty (weight 0.30, capped at 1.0)
    attack_bonus = 0.0
    if is_replay:
        attack_bonus += 0.45
    if is_unauthorized:
        attack_bonus += 0.40
    if has_tampering:
        attack_bonus += 0.35
    if noise_intensity > 0.0:
        attack_bonus += 0.30 * float(noise_intensity)

    attack_penalty = min(1.0, attack_bonus)

    # Weighted combination: exactly matching documented formula
    base_score = (
        0.35 * fidelity_penalty
        + 0.35 * deviation_penalty
        + 0.30 * attack_penalty
    )

    # Escalation rule for confirmed high-confidence attacks:
    # If replay or tampering with severely degraded fidelity, floor the score
    # to ensure it enters HIGH territory. This is a heuristic override.
    if is_replay or (has_tampering and fidelity < 0.85):
        base_score = max(base_score, 0.65 + 0.35 * fidelity_penalty)

    threat_score = round(max(0.0, min(1.0, float(base_score))), 2)

    # Heuristic risk classification (NOT a cryptographic proof)
    if threat_score < 0.30:
        threat_level = "LOW"
        decision = "LEGITIMATE"
    elif threat_score < 0.60:
        threat_level = "MEDIUM"
        decision = "ATTACK DETECTED"
    else:
        threat_level = "HIGH"
        decision = "ATTACK DETECTED"

    return threat_score, threat_level, decision
