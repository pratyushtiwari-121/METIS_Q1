"""
Quantum Physics Laboratory API — Interactive Physical & Mathematical QDS Diagnostics.

ENDPOINTS:
  1. POST /api/physics-lab/tomography         — Single-qubit Pauli state tomography
  2. POST /api/physics-lab/density-matrix     — Density matrix, purity, entropy, validation
  3. POST /api/physics-lab/channel-simulation — 6 quantum channel models (Kraus operators)
  4. POST /api/physics-lab/decoherence-sweep  — Dynamic parameter sweep curve for live charts
  5. POST /api/physics-lab/intercept-resend   — Physical eavesdropping measurement disturbance
  6. POST /api/physics-lab/no-cloning         — Wootters-Zurek no-cloning theorem demonstration
  7. POST /api/physics-lab/bell-states        — 4 Bell states generation & correlation analysis
  8. POST /api/physics-lab/chsh-test          — CHSH Bell inequality test (Classical vs Tsirelson bound)
"""

import math
from fastapi import APIRouter, HTTPException

from app.schemas.schemas import (
    TomographyRequest,
    DensityMatrixAnalysisRequest,
    ChannelSimulationRequest,
    DecoherenceSweepRequest,
    InterceptResendRequest,
    NoCloningRequest,
    BellStateRequest,
    ChshTestRequest,
)
from app.quantum.density_matrix import (
    bloch_to_density_matrix,
    validate_density_matrix,
    compute_purity,
    compute_von_neumann_entropy,
    compute_pauli_expectations,
    density_matrix_to_dict,
)
from app.quantum.tomography import run_single_qubit_tomography
from app.quantum.channels import simulate_channel_effect, compute_decoherence_sweep
from app.quantum.entanglement import analyze_bell_state, run_chsh_bell_test
from app.quantum.experiments import run_intercept_resend_experiment, run_no_cloning_experiment
from app.quantum.noise_models import create_quantum_channel_noise_model

router = APIRouter(prefix="/physics-lab", tags=["Quantum Physics Lab"])


@router.post("/tomography")
def state_tomography(req: TomographyRequest):
    """
    Executes single-qubit Pauli quantum state tomography using Qiskit Aer simulation.
    Reconstructs density matrix ρ_tomo from empirical Pauli expectations ⟨X⟩, ⟨Y⟩, ⟨Z⟩.
    """
    try:
        return run_single_qubit_tomography(req.theta, req.phi, shots=req.shots)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tomography execution failed: {str(e)}")


@router.post("/density-matrix")
def analyze_density_matrix(req: DensityMatrixAnalysisRequest):
    """
    Calculates density matrix ρ = 1/2(I + xX + yY + zZ) and validates Hermiticity,
    unit trace, purity Tr(ρ²), and von Neumann entropy S(ρ).
    """
    x = math.sin(req.theta) * math.cos(req.phi)
    y = math.sin(req.theta) * math.sin(req.phi)
    z = math.cos(req.theta)

    rho = bloch_to_density_matrix(x, y, z)
    val = validate_density_matrix(rho)
    purity = compute_purity(rho)
    entropy = compute_von_neumann_entropy(rho)
    pauli = compute_pauli_expectations(rho)

    return {
        "bloch": {"x": round(x, 4), "y": round(y, 4), "z": round(z, 4), "length": 1.0},
        "density_matrix": density_matrix_to_dict(rho),
        "validation": val,
        "purity": purity,
        "von_neumann_entropy": entropy,
        "pauli_expectations": pauli,
        "is_pure_state": bool(purity >= 0.999),
    }


@router.post("/channel-simulation")
def simulate_channel(req: ChannelSimulationRequest):
    """
    Simulates physical state modification under one of 6 quantum channels:
    bit_flip, phase_flip, bit_phase_flip, depolarizing, amplitude_damping, phase_damping.
    """
    try:
        return simulate_channel_effect(req.channel_name, req.theta, req.phi, req.parameter)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Channel simulation failed: {str(e)}")


@router.post("/decoherence-sweep")
def decoherence_sweep(req: DecoherenceSweepRequest):
    """
    Computes a curve of fidelity, purity, entropy, trace distance, and QBER vs noise
    parameter p ∈ [0, 1] for live plotting in the frontend.
    """
    try:
        sweep_data = compute_decoherence_sweep(req.channel_name, req.theta, req.phi, req.steps)
        return {"channel_name": req.channel_name, "sweep": sweep_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Decoherence sweep failed: {str(e)}")


@router.post("/intercept-resend")
def intercept_resend(req: InterceptResendRequest):
    """
    Simulates transmission with an optional intercept-resend eavesdropper (Eve)
    who measures in a randomly chosen basis {Z, X, Y} and resends the collapsed eigenstate.
    """
    try:
        return run_intercept_resend_experiment(req.theta, req.phi, shots=req.shots, eve_active=req.eve_active)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Intercept-resend experiment failed: {str(e)}")


@router.post("/no-cloning")
def no_cloning(req: NoCloningRequest):
    """
    Demonstrates Wootters-Zurek quantum no-cloning theorem and the optimal
    cloning fidelity upper bound F ≤ 5/6 ≈ 0.8333.
    """
    try:
        return run_no_cloning_experiment(req.theta, req.phi)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"No-cloning demonstration failed: {str(e)}")


@router.post("/bell-states")
def bell_state_analysis(req: BellStateRequest):
    """
    Generates and measures one of the 4 Bell states (|Φ+⟩, |Φ-⟩, |Ψ+⟩, |Ψ-⟩)
    and verifies two-qubit entanglement correlations.
    """
    try:
        return analyze_bell_state(req.bell_type, shots=req.shots)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bell state analysis failed: {str(e)}")


@router.post("/chsh-test")
def chsh_test(req: ChshTestRequest):
    """
    Executes the CHSH Bell inequality test:
      S = E(a, b) + E(a, b') + E(a', b) - E(a', b')
    Verifies violation of the classical bound |S| ≤ 2.0 up to Tsirelson's bound 2√2 ≈ 2.8284.
    """
    try:
        noise = None
        if req.noise_level > 0.0:
            noise = create_quantum_channel_noise_model(depolarizing_prob=req.noise_level)
        return run_chsh_bell_test(shots=req.shots, noise_model=noise)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CHSH Bell test failed: {str(e)}")
