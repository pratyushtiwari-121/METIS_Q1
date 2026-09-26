"""
Hoeffding's Inequality — Statistical Anomaly / Forgery Estimation Module.

PURPOSE
-------
This module provides a clean, reusable implementation of Hoeffding's inequality
for evaluating whether observed quantum measurement statistics are statistically
consistent with the expected distribution for a legitimate quantum state.

DISCLAIMER
----------
This is a statistical anomaly detection mechanism inspired by QDS security
principles. It does NOT constitute a formal proof of information-theoretic
security. It is a heuristic/statistical test to flag measurement deviations
that are unlikely under a legitimate signing scenario.

THEORY
------
Hoeffding's inequality (1963) gives an exponential bound on the probability
that the empirical mean of n i.i.d. bounded random variables deviates from
its expectation by more than ε:

    P(|p̂ - p| ≥ ε) ≤ 2 · exp(-2 · n · ε²)

Where:
    p     = expected (theoretical) probability
    p̂    = observed (empirical) probability from n shots
    ε     = deviation threshold / tolerance
    n     = number of measurement shots

The bound is conservative (one-sided exponential) and applies even without
assumptions about the distribution shape.

USAGE
-----
A small Hoeffding bound (close to 0.0) means the observed deviation would be
extremely unlikely if the state were legitimate — i.e., it is statistically
anomalous. A large bound (close to 1.0 or above) means the deviation is
plausible within statistical sampling noise.

INTERPRETATION
--------------
- bound ≤ 0.05  → statistically significant deviation (anomaly/forgery DETECTED)
- bound > 0.05  → deviation is within expected sampling noise (NOT DETECTED)
- confidence    → 1 - bound, clamped to [0%, 100%]
"""

import math
from dataclasses import dataclass


@dataclass
class HoeffdingResult:
    """
    Structured result from a single Hoeffding bound computation.

    Attributes
    ----------
    basis           : Measurement basis label (e.g. "Z", "X", "Y")
    expected_prob   : Theoretically expected probability p ∈ [0, 1]
    observed_prob   : Empirically observed probability p̂ ∈ [0, 1]
    shots           : Number of measurement shots n
    epsilon         : Observed absolute deviation |p̂ - p|
    hoeffding_bound : Upper bound P(|p̂-p| ≥ ε) ≤ 2·exp(-2·n·ε²)
    confidence_pct  : Statistical confidence = (1 - bound) × 100 [%]
    is_anomaly      : True if bound ≤ 0.05 (statistically significant deviation)
    interpretation  : Human-readable summary string
    """
    basis: str
    expected_prob: float
    observed_prob: float
    shots: int
    epsilon: float
    hoeffding_bound: float
    confidence_pct: float
    is_anomaly: bool
    interpretation: str


def hoeffding_bound(
    expected_prob: float,
    observed_prob: float,
    shots: int,
    basis: str = "Z",
    anomaly_threshold: float = 0.05,
) -> HoeffdingResult:
    """
    Compute Hoeffding's inequality bound for a single measurement basis.

    Parameters
    ----------
    expected_prob     : Theoretical probability p for the '0' outcome (or '+' outcome).
    observed_prob     : Observed empirical frequency p̂ from `shots` measurements.
    shots             : Number of measurement shots n (must be > 0).
    basis             : Label for the basis (e.g. "Z", "X", "Y"). Used only in output.
    anomaly_threshold : Hoeffding bound below which deviation is declared anomalous.
                        Default 0.05 (5% significance level).

    Returns
    -------
    HoeffdingResult dataclass with all computed values.

    Edge Cases Handled
    ------------------
    - shots ≤ 0           → bound set to 1.0 (no information)
    - probability < 0     → clamped to 0.0
    - probability > 1     → clamped to 1.0
    - epsilon == 0        → bound is 2.0 (any deviation accepted); not anomalous
    - floating-point drift in bound (> 2.0 or < 0.0) → clamped
    """

    # --- Input sanitisation ---
    p_exp = max(0.0, min(1.0, float(expected_prob)))
    p_obs = max(0.0, min(1.0, float(observed_prob)))
    n = int(shots)

    if n <= 0:
        # No shots — cannot draw any statistical conclusion
        return HoeffdingResult(
            basis=basis,
            expected_prob=p_exp,
            observed_prob=p_obs,
            shots=n,
            epsilon=0.0,
            hoeffding_bound=1.0,
            confidence_pct=0.0,
            is_anomaly=False,
            interpretation="Insufficient shots (n ≤ 0). No statistical conclusion possible.",
        )

    # Absolute deviation ε = |p̂ - p|
    epsilon = abs(p_obs - p_exp)

    if epsilon == 0.0:
        # Perfect match — bound trivially 2 (not informative; definitely not anomalous)
        return HoeffdingResult(
            basis=basis,
            expected_prob=p_exp,
            observed_prob=p_obs,
            shots=n,
            epsilon=0.0,
            hoeffding_bound=2.0,
            confidence_pct=100.0,
            is_anomaly=False,
            interpretation=(
                f"[{basis}] Perfect match: observed == expected ({p_obs:.4f}). "
                "No deviation detected."
            ),
        )

    # Hoeffding bound: P(|p̂ - p| ≥ ε) ≤ 2·exp(-2·n·ε²)
    exponent = -2.0 * n * (epsilon ** 2)

    # Guard against extreme exponents to avoid overflow/underflow
    exponent_clamped = max(-700.0, exponent)  # exp(-700) ≈ 0
    raw_bound = 2.0 * math.exp(exponent_clamped)

    # Clamp bound to [0.0, 2.0] (theoretical maximum is 2.0 when epsilon=0)
    bound = max(0.0, min(2.0, round(raw_bound, 6)))

    # Statistical confidence: how confident are we the state is legitimate?
    # confidence = 1 - bound, mapped to [0%, 100%]
    confidence_pct = round(max(0.0, min(100.0, (1.0 - bound) * 100.0)), 2)

    # Anomaly flag: if the bound is ≤ threshold, the deviation is statistically
    # unlikely under a legitimate distribution → flag as ANOMALY / FORGERY INDICATOR
    is_anomaly = (bound <= anomaly_threshold)

    # Produce human-readable interpretation
    if is_anomaly:
        interpretation = (
            f"[{basis}] ANOMALY DETECTED. Observed deviation ε={epsilon:.4f} "
            f"is statistically significant (Hoeffding bound={bound:.4f} ≤ {anomaly_threshold}). "
            f"Probability that deviation occurred by chance ≤ {bound:.4f}. "
            f"Statistical confidence: {confidence_pct:.2f}%. "
            f"This deviation is unlikely under a legitimate quantum state."
        )
    else:
        interpretation = (
            f"[{basis}] No anomaly. Observed deviation ε={epsilon:.4f} "
            f"is within expected statistical sampling noise "
            f"(Hoeffding bound={bound:.4f} > {anomaly_threshold}). "
            f"Statistical confidence: {confidence_pct:.2f}%."
        )

    return HoeffdingResult(
        basis=basis,
        expected_prob=p_exp,
        observed_prob=p_obs,
        shots=n,
        epsilon=round(epsilon, 6),
        hoeffding_bound=round(bound, 6),
        confidence_pct=confidence_pct,
        is_anomaly=is_anomaly,
        interpretation=interpretation,
    )


def multi_basis_hoeffding(
    z_expected: float,
    z_observed: float,
    x_expected: float,
    x_observed: float,
    y_expected: float,
    y_observed: float,
    shots: int,
    anomaly_threshold: float = 0.05,
) -> dict:
    """
    Compute Hoeffding bounds for all three measurement bases (Z, X, Y) and
    produce an aggregate forgery/anomaly indication.

    Parameters
    ----------
    z_expected, z_observed : Expected and observed probabilities in Z-basis.
    x_expected, x_observed : Expected and observed probabilities in X-basis.
    y_expected, y_observed : Expected and observed probabilities in Y-basis.
    shots                  : Number of measurement shots per basis.
    anomaly_threshold      : Bound below which anomaly is declared (default 0.05).

    Returns
    -------
    dict with keys:
        "Z"           : HoeffdingResult
        "X"           : HoeffdingResult
        "Y"           : HoeffdingResult
        "any_anomaly" : bool — True if ANY basis shows anomaly
        "all_anomaly" : bool — True if ALL three bases show anomaly
        "summary"     : str — Overall interpretation string
    """
    z_result = hoeffding_bound(z_expected, z_observed, shots, "Z", anomaly_threshold)
    x_result = hoeffding_bound(x_expected, x_observed, shots, "X", anomaly_threshold)
    y_result = hoeffding_bound(y_expected, y_observed, shots, "Y", anomaly_threshold)

    any_anomaly = z_result.is_anomaly or x_result.is_anomaly or y_result.is_anomaly
    all_anomaly = z_result.is_anomaly and x_result.is_anomaly and y_result.is_anomaly

    anomaly_bases = [
        b for b, r in [("Z", z_result), ("X", x_result), ("Y", y_result)]
        if r.is_anomaly
    ]

    if not any_anomaly:
        summary = (
            "All three measurement bases (Z, X, Y) show deviations within "
            "expected statistical sampling noise. No forgery indicator detected."
        )
    elif all_anomaly:
        summary = (
            "STRONG FORGERY INDICATOR: All three bases (Z, X, Y) show statistically "
            "significant deviations. The quantum state is highly unlikely to be legitimate."
        )
    else:
        summary = (
            f"PARTIAL ANOMALY: Statistically significant deviations detected in "
            f"{anomaly_bases} basis/bases. Possible quantum channel manipulation or "
            f"partial state tampering."
        )

    return {
        "Z": z_result,
        "X": x_result,
        "Y": y_result,
        "any_anomaly": any_anomaly,
        "all_anomaly": all_anomaly,
        "summary": summary,
    }
