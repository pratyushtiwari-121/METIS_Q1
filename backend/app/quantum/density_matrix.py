"""
Density Matrix, Purity, von Neumann Entropy, and Trace Distance Module.

MATHEMATICAL FOUNDATION
-----------------------
1. Pure state density matrix:
       ρ = |ψ⟩⟨ψ|
2. Single-qubit Bloch parameterization:
       ρ = 1/2 · (I + x·X + y·Y + z·Z)
   where (x, y, z) are the Cartesian Bloch coordinates:
       x = sin(θ)cos(φ), y = sin(θ)sin(φ), z = cos(θ)
3. Hermiticity:
       ρ = ρ†  (verified numerically via ||ρ - ρ†||_F < 1e-6)
4. Unit Trace:
       Tr(ρ) = 1.0
5. Purity:
       P = Tr(ρ²) ∈ [0.5, 1.0]
       P = 1.0 for pure states, P = 0.5 for maximally mixed state
6. von Neumann Entropy:
       S(ρ) = -Tr(ρ log₂ ρ) = -Σ λᵢ log₂ λᵢ
       S = 0 for pure state, S = 1 for maximally mixed state
7. Trace Distance:
       D(ρ, σ) = 1/2 · ||ρ - σ||₁ = 1/2 · Σ |λᵢ(ρ - σ)|
8. Density Matrix Fidelity (Uhlmann-Jozsa):
       For single-qubit states:
       F(ρ, σ) = Tr(ρ·σ) + 2·√(det(ρ)·det(σ))

NO AI/ML DISCLAIMER
-------------------
All calculations in this module are exact linear algebra and spectral analysis
(eigendecomposition). Zero machine learning is involved.
"""

import math
import cmath
import numpy as np

# Pauli matrices
_I = np.array([[1, 0], [0, 1]], dtype=complex)
_X = np.array([[0, 1], [1, 0]], dtype=complex)
_Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
_Z = np.array([[1, 0], [0, -1]], dtype=complex)


def state_vector_to_density_matrix(alpha: complex, beta: complex) -> np.ndarray:
    """
    Constructs density matrix ρ = |ψ⟩⟨ψ| from state amplitudes.
    Normalizes amplitudes if needed.
    """
    norm = math.sqrt(abs(alpha) ** 2 + abs(beta) ** 2)
    if norm > 0:
        a = alpha / norm
        b = beta / norm
    else:
        a, b = 1.0 + 0j, 0.0 + 0j

    psi = np.array([[a], [b]], dtype=complex)
    rho = psi @ psi.conj().T
    return rho


def bloch_to_density_matrix(x: float, y: float, z: float) -> np.ndarray:
    """
    Constructs single-qubit density matrix from Bloch vector (x, y, z):
        ρ = 1/2 · (I + x·X + y·Y + z·Z)
    """
    # Clamp Bloch length to unit ball to guarantee positive semi-definiteness
    r_norm = math.sqrt(x * x + y * y + z * z)
    if r_norm > 1.0:
        x /= r_norm
        y /= r_norm
        z /= r_norm

    rho = 0.5 * (_I + x * _X + y * _Y + z * _Z)
    return rho


def validate_density_matrix(rho: np.ndarray, tol: float = 1e-5) -> dict:
    """
    Validates mathematical properties of density matrix:
      - Hermiticity: ρ = ρ†
      - Trace: Tr(ρ) = 1
      - Positivity: eigenvalues λᵢ ≥ 0
    """
    # 1. Hermiticity
    diff_herm = np.max(np.abs(rho - rho.conj().T))
    is_hermitian = bool(diff_herm < tol)

    # 2. Trace
    tr = float(np.trace(rho).real)
    is_unit_trace = bool(abs(tr - 1.0) < tol)

    # 3. Eigenvalues
    eigenvalues = np.linalg.eigvalsh(rho)
    eigenvalues = [float(round(val, 6)) for val in eigenvalues]
    is_positive = all(ev >= -tol for ev in eigenvalues)

    is_valid = is_hermitian and is_unit_trace and is_positive

    return {
        "is_valid": is_valid,
        "is_hermitian": is_hermitian,
        "is_unit_trace": is_unit_trace,
        "is_positive": is_positive,
        "trace": round(tr, 4),
        "hermitian_residual": round(float(diff_herm), 6),
        "eigenvalues": eigenvalues,
    }


def compute_purity(rho: np.ndarray) -> float:
    """
    Computes state purity:
        P = Tr(ρ²)
    Range: [0.5, 1.0] for a single qubit.
      P = 1.0  → pure state
      P = 0.5  → maximally mixed state
    """
    rho_sq = rho @ rho
    purity = float(np.trace(rho_sq).real)
    return round(float(max(0.5, min(1.0, purity))), 4)


def compute_von_neumann_entropy(rho: np.ndarray) -> float:
    """
    Computes von Neumann entropy:
        S(ρ) = -Tr(ρ log₂ ρ) = -Σ λᵢ log₂ λᵢ
    For single-qubit states:
        S ∈ [0.0, 1.0]
        S = 0.0 for pure state
        S = 1.0 for maximally mixed state
    Safely handles λᵢ = 0: lim_{λ→0} λ log₂ λ = 0.
    """
    eigenvalues = np.linalg.eigvalsh(rho)
    entropy = 0.0
    for ev in eigenvalues:
        # Clamp tiny negatives from numerical precision
        val = max(0.0, float(ev))
        if val > 1e-12:
            entropy -= val * math.log2(val)

    return round(float(max(0.0, min(1.0, entropy))), 4)


def compute_trace_distance(rho: np.ndarray, sigma: np.ndarray) -> float:
    """
    Computes Trace Distance:
        D(ρ, σ) = 1/2 · ||ρ - σ||₁ = 1/2 · Tr(√((ρ - σ)†(ρ - σ)))
    For single-qubit states, this equals half the sum of absolute eigenvalues:
        D(ρ, σ) = 1/2 · Σ |λᵢ(ρ - σ)|
    Range: [0.0, 1.0]
        D = 0.0 → identical states
        D = 1.0 → orthogonal (completely distinguishable) states
    """
    diff = rho - sigma
    # For Hermitian diff, singular values are absolute eigenvalues
    eigenvals = np.linalg.eigvalsh(diff)
    trace_dist = 0.5 * sum(abs(ev) for ev in eigenvals)
    return round(float(max(0.0, min(1.0, trace_dist))), 4)


def compute_density_matrix_fidelity(rho: np.ndarray, sigma: np.ndarray) -> float:
    """
    Computes Uhlmann-Jozsa fidelity between two single-qubit density matrices:
        F(ρ, σ) = (Tr√(√ρ · σ · √ρ))²
    For 2×2 matrices, this has the explicit closed-form:
        F(ρ, σ) = Tr(ρ·σ) + 2·√(det(ρ)·det(σ))
    Range: [0.0, 1.0]
        F = 1.0 → identical states
        F = 0.0 → orthogonal states
    """
    tr_prod = float(np.trace(rho @ sigma).real)
    det_rho = max(0.0, float(np.linalg.det(rho).real))
    det_sigma = max(0.0, float(np.linalg.det(sigma).real))

    fidelity = tr_prod + 2.0 * math.sqrt(det_rho * det_sigma)
    return round(float(max(0.0, min(1.0, fidelity))), 4)


def compute_pauli_expectations(rho: np.ndarray) -> dict[str, float]:
    """
    Calculates Pauli expectation values:
        ⟨X⟩ = Tr(ρ·X)
        ⟨Y⟩ = Tr(ρ·Y)
        ⟨Z⟩ = Tr(ρ·Z)
    """
    exp_x = float(np.trace(rho @ _X).real)
    exp_y = float(np.trace(rho @ _Y).real)
    exp_z = float(np.trace(rho @ _Z).real)

    return {
        "X": round(exp_x, 4),
        "Y": round(exp_y, 4),
        "Z": round(exp_z, 4),
    }


def density_matrix_to_dict(rho: np.ndarray) -> list[list[dict[str, float]]]:
    """
    Converts 2x2 complex numpy array into JSON-serializable structure.
    """
    return [
        [
            {"real": round(float(rho[i, j].real), 4), "imag": round(float(rho[i, j].imag), 4)}
            for j in range(2)
        ]
        for i in range(2)
    ]
