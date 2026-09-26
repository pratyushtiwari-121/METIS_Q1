"""
Quantum Channels and Decoherence Simulation Module.

KRAUS REPRESENTATION & DENSITY MATRIX OPERATORS
-----------------------------------------------
A quantum channel E(ρ) maps density matrices to density matrices:
    E(ρ) = Σₖ Eₖ · ρ · Eₖ†
satisfying the completeness relation:
    Σₖ Eₖ† · Eₖ = I

IMPLEMENTED CHANNELS:
1. Bit-Flip Channel (Pauli-X error):
       E₀ = √(1 - p) · I
       E₁ = √p · X
       ρ' = (1 - p)ρ + p·XρX

2. Phase-Flip Channel (Pauli-Z error):
       E₀ = √(1 - p) · I
       E₁ = √p · Z
       ρ' = (1 - p)ρ + p·ZρZ

3. Bit-Phase-Flip Channel (Pauli-Y error):
       E₀ = √(1 - p) · I
       E₁ = √p · Y
       ρ' = (1 - p)ρ + p·YρY

4. Depolarizing Channel (Isotropic decoherence):
       E₀ = √(1 - 3p/4) · I
       E₁ = √(p/4) · X
       E₂ = √(p/4) · Y
       E₃ = √(p/4) · Z
       ρ' = (1 - p)ρ + (p/3)(XρX + YρY + ZρZ)

5. Amplitude Damping Channel (Energy relaxation / T₁ decay):
       Models spontaneous emission |1⟩ → |0⟩ with transition probability γ ∈ [0, 1]:
       E₀ = [[1, 0], [0, √(1 - γ)]]
       E₁ = [[0, √γ], [0, 0]]
       E₀†E₀ + E₁†E₁ = I

6. Phase Damping Channel (Pure dephasing / T₂ decay):
       Models loss of quantum coherence without energy loss (decay parameter λ ∈ [0, 1]):
       E₀ = [[1, 0], [0, √(1 - λ)]]
       E₁ = [[0, 0], [0, √λ]]
       E₀†E₀ + E₁†E₁ = I
"""

import math
import numpy as np
from app.quantum.density_matrix import (
    _I, _X, _Y, _Z,
    bloch_to_density_matrix,
    compute_purity,
    compute_von_neumann_entropy,
    compute_trace_distance,
    compute_density_matrix_fidelity,
    compute_pauli_expectations,
    density_matrix_to_dict,
)


def apply_kraus_channel(rho: np.ndarray, kraus_ops: list[np.ndarray]) -> np.ndarray:
    """
    Applies Kraus operators {Eₖ} to density matrix ρ:
        E(ρ) = Σₖ Eₖ · ρ · Eₖ†
    """
    rho_out = np.zeros_like(rho, dtype=complex)
    for E_k in kraus_ops:
        rho_out += E_k @ rho @ E_k.conj().T
    return rho_out


def apply_channel(
    channel_name: str,
    rho: np.ndarray,
    param: float,
) -> np.ndarray:
    """
    Applies one of the 6 supported quantum channels with parameter param ∈ [0, 1].
    """
    p = max(0.0, min(1.0, float(param)))
    name = channel_name.lower().replace(" ", "_").replace("-", "_")

    if name in ("bit_flip", "bitflip"):
        e0 = math.sqrt(1.0 - p) * _I
        e1 = math.sqrt(p) * _X
        return apply_kraus_channel(rho, [e0, e1])

    elif name in ("phase_flip", "phaseflip"):
        e0 = math.sqrt(1.0 - p) * _I
        e1 = math.sqrt(p) * _Z
        return apply_kraus_channel(rho, [e0, e1])

    elif name in ("bit_phase_flip", "bitphaseflip", "y_flip"):
        e0 = math.sqrt(1.0 - p) * _I
        e1 = math.sqrt(p) * _Y
        return apply_kraus_channel(rho, [e0, e1])

    elif name in ("depolarizing", "depolarization"):
        # Parameterized such that at p=1.0, state is completely mixed (ρ = I/2)
        # Using standard: (1 - p)ρ + p/2 * I
        return (1.0 - p) * rho + (p * 0.5) * _I

    elif name in ("amplitude_damping", "amplitude", "t1_relaxation"):
        # E0 = [[1, 0], [0, sqrt(1-p)]], E1 = [[0, sqrt(p)], [0, 0]]
        e0 = np.array([[1.0, 0.0], [0.0, math.sqrt(1.0 - p)]], dtype=complex)
        e1 = np.array([[0.0, math.sqrt(p)], [0.0, 0.0]], dtype=complex)
        return apply_kraus_channel(rho, [e0, e1])

    elif name in ("phase_damping", "phase", "t2_dephasing"):
        # E0 = [[1, 0], [0, sqrt(1-p)]], E1 = [[0, 0], [0, sqrt(p)]]
        e0 = np.array([[1.0, 0.0], [0.0, math.sqrt(1.0 - p)]], dtype=complex)
        e1 = np.array([[0.0, 0.0], [0.0, math.sqrt(p)]], dtype=complex)
        return apply_kraus_channel(rho, [e0, e1])

    else:
        # Default fallback: identity (no noise)
        return rho.copy()


def simulate_channel_effect(
    channel_name: str,
    theta: float,
    phi: float,
    parameter: float,
) -> dict:
    """
    Computes complete physical state modification under a given quantum channel:
      - Initial vs Output density matrix
      - Initial vs Output Bloch vector
      - State Fidelity, Trace Distance, Purity change, von Neumann Entropy, QBER
    """
    # Initial state
    x0 = math.sin(theta) * math.cos(phi)
    y0 = math.sin(theta) * math.sin(phi)
    z0 = math.cos(theta)
    rho_in = bloch_to_density_matrix(x0, y0, z0)

    # Output state through channel
    rho_out = apply_channel(channel_name, rho_in, parameter)

    # Output Bloch coordinates
    pauli_exp = compute_pauli_expectations(rho_out)
    x1, y1, z1 = pauli_exp["X"], pauli_exp["Y"], pauli_exp["Z"]
    bloch_length = math.sqrt(x1**2 + y1**2 + z1**2)
    bloch_disp = math.sqrt((x1 - x0)**2 + (y1 - y0)**2 + (z1 - z0)**2)

    # Physical metrics
    fidelity = compute_density_matrix_fidelity(rho_in, rho_out)
    trace_dist = compute_trace_distance(rho_in, rho_out)
    purity_in = compute_purity(rho_in)
    purity_out = compute_purity(rho_out)
    entropy_in = compute_von_neumann_entropy(rho_in)
    entropy_out = compute_von_neumann_entropy(rho_out)

    # QBER estimation: computational basis error probability
    # Initial P(0) = (1 + z0)/2, P(1) = (1 - z0)/2
    # Output P_out(0) = rho_out[0,0].real, P_out(1) = rho_out[1,1].real
    # Ideal outcome expectation compared to disturbed outcome:
    p0_in = 0.5 * (1.0 + z0)
    p1_in = 0.5 * (1.0 - z0)
    p0_out = float(rho_out[0, 0].real)
    p1_out = float(rho_out[1, 1].real)
    qber = 0.5 * (abs(p0_in - p0_out) + abs(p1_in - p1_out))

    return {
        "channel_name": channel_name,
        "parameter": round(parameter, 4),
        "initial_state": {
            "bloch": {"x": round(x0, 4), "y": round(y0, 4), "z": round(z0, 4), "length": 1.0},
            "purity": purity_in,
            "entropy": entropy_in,
            "density_matrix": density_matrix_to_dict(rho_in),
        },
        "output_state": {
            "bloch": {"x": round(x1, 4), "y": round(y1, 4), "z": round(z1, 4), "length": round(bloch_length, 4)},
            "purity": purity_out,
            "entropy": entropy_out,
            "density_matrix": density_matrix_to_dict(rho_out),
        },
        "metrics": {
            "fidelity": round(fidelity, 4),
            "trace_distance": round(trace_dist, 4),
            "bloch_displacement": round(bloch_disp, 4),
            "qber": round(qber, 4),
            "purity_drop": round(purity_in - purity_out, 4),
            "entropy_increase": round(entropy_out - entropy_in, 4),
        }
    }


def compute_decoherence_sweep(
    channel_name: str,
    theta: float = 1.0,
    phi: float = 0.5,
    steps: int = 21,
) -> list[dict]:
    """
    Computes physical curve of metrics vs noise parameter p ∈ [0, 1] for live plotting.
    Returns array of {p, fidelity, purity, entropy, bloch_length, qber}.
    """
    x0 = math.sin(theta) * math.cos(phi)
    y0 = math.sin(theta) * math.sin(phi)
    z0 = math.cos(theta)
    rho_in = bloch_to_density_matrix(x0, y0, z0)
    p0_in = 0.5 * (1.0 + z0)

    sweep_data = []
    p_values = np.linspace(0.0, 1.0, steps)

    for p in p_values:
        param = float(p)
        rho_out = apply_channel(channel_name, rho_in, param)

        pauli = compute_pauli_expectations(rho_out)
        bx, by, bz = pauli["X"], pauli["Y"], pauli["Z"]
        r_len = math.sqrt(bx**2 + by**2 + bz**2)

        fid = compute_density_matrix_fidelity(rho_in, rho_out)
        pur = compute_purity(rho_out)
        ent = compute_von_neumann_entropy(rho_out)
        td = compute_trace_distance(rho_in, rho_out)

        p0_out = float(rho_out[0, 0].real)
        qber = abs(p0_in - p0_out)

        sweep_data.append({
            "noise_parameter": round(param, 3),
            "fidelity": round(fid, 4),
            "purity": round(pur, 4),
            "entropy": round(ent, 4),
            "trace_distance": round(td, 4),
            "bloch_length": round(r_len, 4),
            "qber": round(qber, 4),
        })

    return sweep_data
