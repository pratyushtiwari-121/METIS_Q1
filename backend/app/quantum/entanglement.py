"""
Entanglement Verification and CHSH Bell Inequality Test Module.

PHYSICAL THEORY
---------------
1. Bell States (Maximally Entangled Two-Qubit States):
       |Φ+⟩ = (|00⟩ + |11⟩) / √2
       |Φ-⟩ = (|00⟩ - |11⟩) / √2
       |Ψ+⟩ = (|01⟩ + |10⟩) / √2
       |Ψ-⟩ = (|01⟩ - |10⟩) / √2

2. CHSH (Clauser-Horne-Shimony-Holt) Bell Inequality:
   Alice chooses between two measurement settings: a, a'
   Bob chooses between two measurement settings: b, b'
   Standard optimal angles for maximal quantum violation on |Φ+⟩:
       a  = 0
       a' = π/2
       b  = π/4
       b' = 3π/4  (or -π/4)

   The correlation parameter is defined as:
       E(θ_A, θ_B) = P(same) - P(different)
                   = [N(00) + N(11) - N(01) - N(10)] / N_shots

   The CHSH Bell parameter:
       S = E(a, b) + E(a, b') + E(a', b) - E(a', b')

   BOUNDS:
       Classical Local Realism (Bell's theorem):  |S| ≤ 2.0
       Quantum Mechanics (Tsirelson's bound):     |S| ≤ 2√2 ≈ 2.8284

3. SECURITY RELEVANCE IN QDS / QUANTUM CRYPTOGRAPHY:
   Violation (|S| > 2.0) demonstrates verified non-local quantum entanglement
   across the pre-shared EPR distribution channel. Decoherence or eavesdropping
   lowers |S| toward or below the classical bound 2.0.

DISCLAIMER
----------
CHSH violation is used as a physical channel-quality and entanglement diagnostic.
It does NOT by itself constitute a mathematical proof of digital signature security.
"""

import math
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator


def build_bell_circuit(bell_type: str = "phi_plus") -> QuantumCircuit:
    """
    Builds a 2-qubit circuit preparing one of the 4 standard Bell states:
      - 'phi_plus'  (|Φ+⟩): H(0) → CX(0, 1)
      - 'phi_minus' (|Φ-⟩): X(0) → H(0) → CX(0, 1)
      - 'psi_plus'  (|Ψ+⟩): X(1) → H(0) → CX(0, 1)
      - 'psi_minus' (|Ψ-⟩): X(0) → X(1) → H(0) → CX(0, 1)
    """
    qc = QuantumCircuit(2, 2)
    b_type = bell_type.lower().replace(" ", "_").replace("-", "_")

    if b_type in ("phi_minus", "phi_neg"):
        qc.x(0)
    elif b_type in ("psi_plus", "psi_pos"):
        qc.x(1)
    elif b_type in ("psi_minus", "psi_neg"):
        qc.x(0)
        qc.x(1)

    qc.h(0)
    qc.cx(0, 1)
    return qc


def analyze_bell_state(bell_type: str = "phi_plus", shots: int = 2048) -> dict:
    """
    Measures a Bell state in the computational basis and computes its correlation.
    """
    qc = build_bell_circuit(bell_type)
    qc.measure([0, 1], [0, 1])

    simulator = AerSimulator()
    job = simulator.run(transpile(qc, simulator), shots=shots)
    counts = job.result().get_counts()

    # Calculate correlation E = (N_00 + N_11 - N_01 - N_10) / shots
    n00 = counts.get("00", 0)
    n11 = counts.get("11", 0)
    n01 = counts.get("01", 0)
    n10 = counts.get("10", 0)

    correlation = (n00 + n11 - n01 - n10) / shots

    # Theoretical expected probabilities
    expected_prob = {}
    if "phi" in bell_type.lower():
        expected_prob = {"00": 0.5, "11": 0.5, "01": 0.0, "10": 0.0}
    else:
        expected_prob = {"01": 0.5, "10": 0.5, "00": 0.0, "11": 0.0}

    # TVD
    tvd = 0.5 * sum(abs(counts.get(k, 0) / shots - expected_prob[k]) for k in ["00", "01", "10", "11"])

    return {
        "bell_state": bell_type,
        "shots": shots,
        "counts": counts,
        "probabilities": {k: round(v / shots, 4) for k, v in counts.items()},
        "correlation": round(float(correlation), 4),
        "tvd": round(float(tvd), 4),
        "circuit_ascii": qc.draw(output="text").single_string(),
        "entanglement_quality": "High" if tvd < 0.05 else "Degraded",
    }


def _measure_chsh_correlation(
    theta_a: float,
    theta_b: float,
    shots: int = 1024,
    noise_model=None,
) -> float:
    """
    Measures correlation E(θ_A, θ_B) = ⟨σ_θA ⊗ σ_θB⟩ on |Φ+⟩:
      1. Prepare |Φ+⟩ = (|00⟩ + |11⟩) / √2
      2. Alice rotates by -θ_A around Y axis
      3. Bob rotates by -θ_B around Y axis
      4. Measure in computational basis
      5. E = (N_00 + N_11 - N_01 - N_10) / shots
    """
    qc = QuantumCircuit(2, 2)
    # Prepare |Φ+⟩
    qc.h(0)
    qc.cx(0, 1)

    # Basis rotations: Ry(-2*theta) aligns measurement axis
    qc.ry(-2.0 * theta_a, 0)
    qc.ry(-2.0 * theta_b, 1)

    qc.measure([0, 1], [0, 1])

    simulator = AerSimulator()
    kwargs = {"noise_model": noise_model} if noise_model else {}
    job = simulator.run(transpile(qc, simulator), shots=shots, **kwargs)
    counts = job.result().get_counts()

    n00 = counts.get("00", 0)
    n11 = counts.get("11", 0)
    n01 = counts.get("01", 0)
    n10 = counts.get("10", 0)
    total = sum(counts.values())

    corr = (n00 + n11 - n01 - n10) / total
    return float(corr)


def run_chsh_bell_test(shots: int = 2048, noise_model=None) -> dict:
    """
    Executes complete CHSH Bell test across the 4 angle combinations:
      - (a, b)   = (0, π/4)
      - (a, b')  = (0, 3π/4)
      - (a', b)  = (π/2, π/4)
      - (a', b') = (π/2, 3π/4)

    Theoretical quantum value on |Φ+⟩:
      E(a, b)   = cos(2(0 - π/4))     = cos(-π/2) wait:
      In standard Bell test:
      For |Φ+⟩, E(a, b) = cos(2(a - b))
      With a=0, a'=π/4, b=π/8, b'=3π/8:
        2*(a - b) = -π/4 → cos(-π/4) = 1/√2
      With standard convention:
        a = 0, a' = π/2, b = π/4, b' = -π/4:
        E(0, π/4) = cos(-π/2)? Wait!
    Let's check the exact optimal angle set for Ry rotations:
    For |Φ+⟩ state:
      E(a, b) = cos(a - b) if we rotate by θ around Y:
      Let's use a = 0, a' = π/2, b = π/4, b' = -π/4
    """
    # Optimal CHSH angles where E(θ_A, θ_B) = cos(2*(θ_A - θ_B)):
    # To get 1/√2 ≈ 0.7071 on each term:
    # 2*(θ_A - θ_B) = π/4 → (θ_A - θ_B) = π/8
    # Let:
    #   a  = 0
    #   a' = π/4
    #   b  = π/8
    #   b' = -π/8
    # Then:
    #   a - b   = -π/8   → 2*(a-b) = -π/4   → cos(-π/4) = +1/√2 ≈ +0.7071
    #   a - b'  = +π/8   → 2*(a-b') = +π/4  → cos(+π/4) = +1/√2 ≈ +0.7071
    #   a' - b  = +π/8   → 2*(a'-b) = +π/4  → cos(+π/4) = +1/√2 ≈ +0.7071
    #   a' - b' = +3π/8  → 2*(a'-b') = +3π/4→ cos(+3π/4)= -1/√2 ≈ -0.7071
    # S = E(a,b) + E(a,b') + E(a',b) - E(a',b')
    #   = 1/√2 + 1/√2 + 1/√2 - (-1/√2) = 4 / √2 = 2√2 ≈ 2.8284 !
    a = 0.0
    a_prime = math.pi / 4.0
    b = math.pi / 8.0
    b_prime = -math.pi / 8.0

    e_ab = _measure_chsh_correlation(a, b, shots, noise_model)
    e_ab_prime = _measure_chsh_correlation(a, b_prime, shots, noise_model)
    e_a_prime_b = _measure_chsh_correlation(a_prime, b, shots, noise_model)
    e_a_prime_b_prime = _measure_chsh_correlation(a_prime, b_prime, shots, noise_model)

    # S = E(a, b) + E(a, b') + E(a', b) - E(a', b')
    s_value = e_ab + e_ab_prime + e_a_prime_b - e_a_prime_b_prime

    classical_bound = 2.0
    tsirelson_bound = 2.0 * math.sqrt(2.0)  # 2.8284

    violates_classical = bool(abs(s_value) > classical_bound)

    return {
        "shots_per_setting": shots,
        "total_shots": shots * 4,
        "angles": {
            "a": 0.0,
            "a_prime": round(a_prime, 4),
            "b": round(b, 4),
            "b_prime": round(b_prime, 4),
        },
        "correlations": {
            "E(a, b)": round(e_ab, 4),
            "E(a, b')": round(e_ab_prime, 4),
            "E(a', b)": round(e_a_prime_b, 4),
            "E(a', b')": round(e_a_prime_b_prime, 4),
        },
        "chsh_s_value": round(float(s_value), 4),
        "classical_bound": classical_bound,
        "tsirelson_bound": round(float(tsirelson_bound), 4),
        "violates_classical_bound": violates_classical,
        "quantum_violation_margin": round(float(abs(s_value) - classical_bound), 4) if violates_classical else 0.0,
        "channel_verdict": (
            f"Quantum non-locality confirmed (S = {s_value:.4f} > 2.0). "
            f"Entangled EPR channel is verified intact and free from classical local hidden-variable eavesdropping."
            if violates_classical else
            f"Classical bound not violated (S = {s_value:.4f} ≤ 2.0). "
            f"Entanglement is severely degraded by noise, loss of coherence, or interception."
        ),
        "disclaimer": (
            "CHSH violation is used as an entanglement/channel-quality diagnostic. "
            "It does NOT by itself constitute a formal cryptographic digital signature proof."
        ),
    }
