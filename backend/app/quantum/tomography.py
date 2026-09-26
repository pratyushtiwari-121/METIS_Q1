"""
Quantum State Tomography (Single-Qubit Pauli Tomography).

MATHEMATICAL FOUNDATION
-----------------------
Single-qubit quantum state tomography reconstructs an unknown density matrix
by measuring Pauli expectation values along three mutually unbiased bases:
  1. Z-basis: Computational measurement {|0⟩, |1⟩}
       ⟨Z⟩ = P_z(0) - P_z(1)
  2. X-basis: Apply Hadamard H before measurement
       ⟨X⟩ = P_x(+) - P_x(-) = P_x(0) - P_x(1)
  3. Y-basis: Apply S† then H before measurement
       ⟨Y⟩ = P_y(+i) - P_y(-i) = P_y(0) - P_y(1)

Reconstruction Formula:
  ρ_tomo = 1/2 · (I + ⟨X⟩·X + ⟨Y⟩·Y + ⟨Z⟩·Z)

Validation:
  - Frobenius norm residual: ||ρ_expected - ρ_tomo||_F
  - Trace distance: D(ρ_expected, ρ_tomo) = 1/2 · ||ρ_expected - ρ_tomo||₁
  - State fidelity: F(ρ_expected, ρ_tomo)
  - Purity difference: |Tr(ρ_expected²) - Tr(ρ_tomo²)|
"""

import math
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

from app.quantum.density_matrix import (
    _I, _X, _Y, _Z,
    bloch_to_density_matrix,
    state_vector_to_density_matrix,
    compute_purity,
    compute_von_neumann_entropy,
    compute_trace_distance,
    compute_density_matrix_fidelity,
    validate_density_matrix,
    density_matrix_to_dict,
)


def run_single_qubit_tomography(
    theta: float,
    phi: float,
    shots: int = 1024,
    noise_model=None,
) -> dict:
    """
    Performs physical single-qubit Pauli tomography using Qiskit Aer simulation.

    Steps:
      1. Prepare state |ψ⟩ = cos(θ/2)|0⟩ + e^(iφ)sin(θ/2)|1⟩
      2. Run circuit in Z-basis (direct measurement)
      3. Run circuit in X-basis (Hadamard before measurement)
      4. Run circuit in Y-basis (S† then Hadamard before measurement)
      5. Extract observed outcome counts, compute empirical expectations:
           ⟨O⟩_emp = (N_0 - N_1) / N_shots
      6. Reconstruct ρ_tomo and compute distance/fidelity to theoretical state.
    """
    simulator = AerSimulator()

    # --- Circuit 1: Z basis ---
    qc_z = QuantumCircuit(1, 1)
    qc_z.ry(theta, 0)
    qc_z.rz(phi, 0)
    qc_z.measure(0, 0)

    # --- Circuit 2: X basis ---
    qc_x = QuantumCircuit(1, 1)
    qc_x.ry(theta, 0)
    qc_x.rz(phi, 0)
    qc_x.h(0)
    qc_x.measure(0, 0)

    # --- Circuit 3: Y basis ---
    qc_y = QuantumCircuit(1, 1)
    qc_y.ry(theta, 0)
    qc_y.rz(phi, 0)
    qc_y.sdg(0)
    qc_y.h(0)
    qc_y.measure(0, 0)

    # Execute on Aer
    kwargs = {"noise_model": noise_model} if noise_model else {}
    job_z = simulator.run(transpile(qc_z, simulator), shots=shots, **kwargs)
    job_x = simulator.run(transpile(qc_x, simulator), shots=shots, **kwargs)
    job_y = simulator.run(transpile(qc_y, simulator), shots=shots, **kwargs)

    counts_z = job_z.result().get_counts()
    counts_x = job_x.result().get_counts()
    counts_y = job_y.result().get_counts()

    # Empirical expectations: ⟨O⟩ = P(0) - P(1) = (counts['0'] - counts['1']) / shots
    n_z0 = counts_z.get("0", 0)
    n_z1 = counts_z.get("1", 0)
    exp_z_emp = (n_z0 - n_z1) / shots

    n_x0 = counts_x.get("0", 0)
    n_x1 = counts_x.get("1", 0)
    exp_x_emp = (n_x0 - n_x1) / shots

    n_y0 = counts_y.get("0", 0)
    n_y1 = counts_y.get("1", 0)
    exp_y_emp = (n_y0 - n_y1) / shots

    # Theoretical Bloch coordinates
    x_theory = math.sin(theta) * math.cos(phi)
    y_theory = math.sin(theta) * math.sin(phi)
    z_theory = math.cos(theta)

    # Theoretical density matrix
    rho_expected = bloch_to_density_matrix(x_theory, y_theory, z_theory)

    # Reconstructed density matrix from empirical expectations
    rho_reconstructed = bloch_to_density_matrix(exp_x_emp, exp_y_emp, exp_z_emp)

    # Comparisons
    trace_dist = compute_trace_distance(rho_expected, rho_reconstructed)
    fidelity = compute_density_matrix_fidelity(rho_expected, rho_reconstructed)
    purity_expected = compute_purity(rho_expected)
    purity_reconstructed = compute_purity(rho_reconstructed)
    entropy_expected = compute_von_neumann_entropy(rho_expected)
    entropy_reconstructed = compute_von_neumann_entropy(rho_reconstructed)

    # Frobenius norm of matrix difference
    matrix_residual = float(np.linalg.norm(rho_expected - rho_reconstructed, "fro"))

    val_res = validate_density_matrix(rho_reconstructed)

    return {
        "shots": shots,
        "measurements": {
            "Z": {
                "counts": counts_z,
                "p0": round(n_z0 / shots, 4),
                "p1": round(n_z1 / shots, 4),
                "observed_expectation": round(float(exp_z_emp), 4),
                "theoretical_expectation": round(float(z_theory), 4),
            },
            "X": {
                "counts": counts_x,
                "p0": round(n_x0 / shots, 4),
                "p1": round(n_x1 / shots, 4),
                "observed_expectation": round(float(exp_x_emp), 4),
                "theoretical_expectation": round(float(x_theory), 4),
            },
            "Y": {
                "counts": counts_y,
                "p0": round(n_y0 / shots, 4),
                "p1": round(n_y1 / shots, 4),
                "observed_expectation": round(float(exp_y_emp), 4),
                "theoretical_expectation": round(float(y_theory), 4),
            },
        },
        "reconstructed_bloch": {
            "x": round(float(exp_x_emp), 4),
            "y": round(float(exp_y_emp), 4),
            "z": round(float(exp_z_emp), 4),
            "length": round(float(math.sqrt(exp_x_emp**2 + exp_y_emp**2 + exp_z_emp**2)), 4),
        },
        "theoretical_bloch": {
            "x": round(float(x_theory), 4),
            "y": round(float(y_theory), 4),
            "z": round(float(z_theory), 4),
            "length": 1.0,
        },
        "reconstructed_density_matrix": density_matrix_to_dict(rho_reconstructed),
        "expected_density_matrix": density_matrix_to_dict(rho_expected),
        "fidelity": round(float(fidelity), 4),
        "trace_distance": round(float(trace_dist), 4),
        "frobenius_residual": round(float(matrix_residual), 4),
        "purity_expected": purity_expected,
        "purity_reconstructed": purity_reconstructed,
        "entropy_expected": entropy_expected,
        "entropy_reconstructed": entropy_reconstructed,
        "density_matrix_validation": val_res,
    }
