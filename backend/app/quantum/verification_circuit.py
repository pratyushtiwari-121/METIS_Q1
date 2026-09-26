"""
Quantum verification circuit reconstruction and basis-wise measurement verification.

VERIFICATION PIPELINE
---------------------
1. Reconstruct quantum state from signature parameters (θ, φ).
2. Run projective measurements in Z, X, and Y bases.
3. Compare observed vs expected statistics (TVD).
4. Compute state fidelity F = |⟨ψ_orig|ψ_active⟩|².
5. Compute Hoeffding bounds per basis for statistical anomaly detection.
6. Compute threat score T = 0.35(1-F) + 0.35·min(1,2Δ) + 0.30·AttackPenalty.
7. Return structured verification result.

MEASUREMENT BASES (physically correct implementations)
-------------------------------------------------------
Z-basis: Computational basis measurement — direct measure.
X-basis: Apply H before measurement.
         Expected P(+1) = |⟨+|ψ⟩|² = 0.5(1 + 2·Re(α·β*))
Y-basis: Apply S† then H before measurement.
         Expected P(+i) = |⟨+i|ψ⟩|² = 0.5(1 + 2·Im(α·β*))

DISCLAIMER
----------
This is a measurement-based threat detection mechanism inspired by QDS security
principles. It does NOT provide formal information-theoretic security guarantees.
"""
import time
import math
from datetime import datetime, timezone
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from app.schemas.schemas import (
    StateVectorInfo,
    VerificationResponse,
    BasisVerificationResult,
    HoeffdingBasisResult,
    ForgerySummary,
)
from app.quantum.state_encoding import hash_to_quantum_state, compute_sha256, state_info_from_angles
from app.quantum.fidelity import compute_state_fidelity, compute_measurement_deviation, compute_threat_score
from app.quantum.hoeffding import hoeffding_bound, multi_basis_hoeffding
from app.quantum.bloch import angles_to_bloch_coordinates, compute_bloch_displacement
from app.quantum.density_matrix import (
    bloch_to_density_matrix,
    compute_purity,
    compute_von_neumann_entropy,
    compute_trace_distance,
    density_matrix_to_dict,
)


def build_verification_qiskit_code(theta: float, phi: float, shots: int = 1024) -> str:
    return f'''from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

# Reconstruct state from signature parameters (theta={theta:.4f}, phi={phi:.4f})
# |psi> = cos(theta/2)|0> + exp(i*phi)*sin(theta/2)|1>

# --- Z-basis (Computational basis) measurement ---
qc_z = QuantumCircuit(1, 1)
qc_z.ry({theta:.4f}, 0)
qc_z.rz({phi:.4f}, 0)
qc_z.measure(0, 0)

# --- X-basis measurement (apply H before measuring) ---
qc_x = QuantumCircuit(1, 1)
qc_x.ry({theta:.4f}, 0)
qc_x.rz({phi:.4f}, 0)
qc_x.h(0)          # Rotates X-basis to Z-basis
qc_x.measure(0, 0)

# --- Y-basis measurement (apply Sdg then H before measuring) ---
qc_y = QuantumCircuit(1, 1)
qc_y.ry({theta:.4f}, 0)
qc_y.rz({phi:.4f}, 0)
qc_y.sdg(0)        # S-dagger: diagonalizes Y eigenstates
qc_y.h(0)          # Rotates Y-basis to Z-basis
qc_y.measure(0, 0)

simulator = AerSimulator()
for name, qc in [("Z", qc_z), ("X", qc_x), ("Y", qc_y)]:
    counts = simulator.run(transpile(qc, simulator), shots={shots}).result().get_counts()
    p0 = counts.get("0", 0) / {shots}
    p1 = counts.get("1", 0) / {shots}
    print(f"{{name}}-basis: P(0)={{p0:.4f}}, P(1)={{p1:.4f}}")
'''


def run_verification(
    message: str,
    original_state: StateVectorInfo,
    signature_id: str,
    shots: int = 1024,
    threshold: float = 0.100,
    tampered_state: StateVectorInfo | None = None,
) -> VerificationResponse:
    """
    Executes the multi-basis quantum verification protocol.

    Steps:
      1. Determine active state (tampered or original).
      2. Run Z, X, Y basis measurements.
      3. Compute expected probabilities analytically.
      4. Compute fidelity and TVD.
      5. Compute per-basis Hoeffding bounds.
      6. Compute threat score.
      7. Return VerificationResponse.
    """
    start_time = time.perf_counter()

    # If tampered_state provided (attack simulation), measure that state
    active_state = tampered_state if tampered_state is not None else original_state

    # -----------------------------------------------------------------------
    # 1. Build circuits for Z, X, Y bases
    # -----------------------------------------------------------------------

    # Z-basis: Computational basis measurement
    qc_z = QuantumCircuit(1, 1)
    qc_z.ry(active_state.theta_rad, 0)
    qc_z.rz(active_state.phi_rad, 0)
    qc_z.measure(0, 0)

    # X-basis: Apply H before measurement
    # H rotates: |+⟩ → |0⟩, |−⟩ → |1⟩
    qc_x = QuantumCircuit(1, 1)
    qc_x.ry(active_state.theta_rad, 0)
    qc_x.rz(active_state.phi_rad, 0)
    qc_x.h(0)
    qc_x.measure(0, 0)

    # Y-basis: Apply S† then H before measurement
    # S†H rotates: |+i⟩ → |0⟩, |−i⟩ → |1⟩
    qc_y = QuantumCircuit(1, 1)
    qc_y.ry(active_state.theta_rad, 0)
    qc_y.rz(active_state.phi_rad, 0)
    qc_y.sdg(0)
    qc_y.h(0)
    qc_y.measure(0, 0)

    # -----------------------------------------------------------------------
    # 2. Execute all three bases
    # -----------------------------------------------------------------------
    simulator = AerSimulator()
    job_z = simulator.run(transpile(qc_z, simulator), shots=shots)
    job_x = simulator.run(transpile(qc_x, simulator), shots=shots)
    job_y = simulator.run(transpile(qc_y, simulator), shots=shots)

    counts_z = job_z.result().get_counts()
    counts_x = job_x.result().get_counts()
    counts_y = job_y.result().get_counts()

    # -----------------------------------------------------------------------
    # 3. Compute observed probabilities
    # -----------------------------------------------------------------------
    p0_obs_z = round(counts_z.get("0", 0) / shots, 4)
    p1_obs_z = round(counts_z.get("1", 0) / shots, 4)
    observed_dist = {"0": p0_obs_z, "1": p1_obs_z}

    # X-basis: P(0) corresponds to measuring in +X eigenstate
    px_obs = round(counts_x.get("0", 0) / shots, 4)

    # Y-basis: P(0) corresponds to measuring in +Y eigenstate
    py_obs = round(counts_y.get("0", 0) / shots, 4)

    # -----------------------------------------------------------------------
    # 4. Compute expected probabilities analytically (from ORIGINAL state)
    # -----------------------------------------------------------------------
    # Z-basis expected: P(0) = |α|²
    expected_dist = {"0": original_state.prob_0, "1": original_state.prob_1}

    # X-basis expected: |⟨+|ψ⟩|² = 0.5(1 + 2·Re(α·β*))
    # where |+⟩ = (|0⟩ + |1⟩)/√2
    c_alpha = complex(original_state.alpha.real, original_state.alpha.imag)
    c_beta = complex(original_state.beta.real, original_state.beta.imag)
    norm_orig = math.sqrt(abs(c_alpha) ** 2 + abs(c_beta) ** 2)
    if norm_orig > 0:
        c_alpha /= norm_orig
        c_beta /= norm_orig
    cross_term = c_alpha * c_beta.conjugate()
    px_exp = round(float(0.5 * (1.0 + 2.0 * cross_term.real)), 4)
    px_exp = max(0.0, min(1.0, px_exp))

    # Y-basis expected: |⟨+i|ψ⟩|² = 0.5(1 - 2·Im(α·β*))
    # where |+i⟩ = (|0⟩ + i|1⟩)/√2 and measurement basis applies S† then H
    py_exp = round(float(0.5 * (1.0 - 2.0 * cross_term.imag)), 4)
    py_exp = max(0.0, min(1.0, py_exp))

    # -----------------------------------------------------------------------
    # 5. Compute fidelity and TVD
    # -----------------------------------------------------------------------
    fidelity = compute_state_fidelity(original_state, active_state)
    deviation = compute_measurement_deviation(expected_dist, observed_dist)
    bit_error_rate = round(deviation, 4)

    # -----------------------------------------------------------------------
    # 6. Hoeffding bounds per basis (FIX 3 & 4)
    # -----------------------------------------------------------------------
    hoeffding_results = multi_basis_hoeffding(
        z_expected=original_state.prob_0,
        z_observed=p0_obs_z,
        x_expected=px_exp,
        x_observed=px_obs,
        y_expected=py_exp,
        y_observed=py_obs,
        shots=shots,
        anomaly_threshold=0.05,
    )

    def _to_schema(hr) -> HoeffdingBasisResult:
        return HoeffdingBasisResult(
            basis=hr.basis,
            expected_prob=hr.expected_prob,
            observed_prob=hr.observed_prob,
            shots=hr.shots,
            epsilon=hr.epsilon,
            hoeffding_bound=hr.hoeffding_bound,
            confidence_pct=hr.confidence_pct,
            is_anomaly=hr.is_anomaly,
            interpretation=hr.interpretation,
        )

    hoeffding_z_schema = _to_schema(hoeffding_results["Z"])
    hoeffding_x_schema = _to_schema(hoeffding_results["X"])
    hoeffding_y_schema = _to_schema(hoeffding_results["Y"])

    anomaly_bases = [
        b for b, r in [
            ("Z", hoeffding_results["Z"]),
            ("X", hoeffding_results["X"]),
            ("Y", hoeffding_results["Y"]),
        ]
        if r.is_anomaly
    ]
    forgery_summary_schema = ForgerySummary(
        any_anomaly=hoeffding_results["any_anomaly"],
        all_anomaly=hoeffding_results["all_anomaly"],
        anomaly_bases=anomaly_bases,
        summary=hoeffding_results["summary"],
    )

    # -----------------------------------------------------------------------
    # 7. Basis-wise verification results
    # -----------------------------------------------------------------------
    basis_results = [
        BasisVerificationResult(
            basis="Z-basis",
            expected=original_state.prob_0,
            observed=p0_obs_z,
            deviation=round(abs(original_state.prob_0 - p0_obs_z), 4),
            status="Valid" if abs(original_state.prob_0 - p0_obs_z) <= threshold else "Deviation Detected",
        ),
        BasisVerificationResult(
            basis="X-basis",
            expected=px_exp,
            observed=px_obs,
            deviation=round(abs(px_exp - px_obs), 4),
            status="Valid" if abs(px_exp - px_obs) <= threshold else "Deviation Detected",
        ),
        BasisVerificationResult(
            basis="Y-basis",
            expected=py_exp,
            observed=py_obs,
            deviation=round(abs(py_exp - py_obs), 4),
            status="Valid" if abs(py_exp - py_obs) <= threshold else "Deviation Detected",
        ),
    ]

    # -----------------------------------------------------------------------
    # 8. Threat scoring
    # -----------------------------------------------------------------------
    threat_score, threat_level, decision = compute_threat_score(
        fidelity=fidelity,
        deviation=deviation,
        has_tampering=(tampered_state is not None and fidelity < 0.95),
    )

    # Override decision if Hoeffding anomaly detected across multiple bases
    if hoeffding_results["all_anomaly"] and decision == "LEGITIMATE":
        decision = "ATTACK DETECTED"

    # Override if pure TVD threshold exceeded
    if deviation > threshold and decision == "LEGITIMATE":
        decision = "ATTACK DETECTED"

    # Physical quantum state metrics
    bloch_orig = angles_to_bloch_coordinates(original_state.theta_rad, original_state.phi_rad)
    bloch_active = angles_to_bloch_coordinates(active_state.theta_rad, active_state.phi_rad)
    bloch_disp = compute_bloch_displacement(bloch_orig, bloch_active)

    rho_orig = bloch_to_density_matrix(bloch_orig["x"], bloch_orig["y"], bloch_orig["z"])
    rho_active = bloch_to_density_matrix(bloch_active["x"], bloch_active["y"], bloch_active["z"])

    trace_dist = compute_trace_distance(rho_orig, rho_active)
    purity = compute_purity(rho_active)
    von_neumann_entropy = compute_von_neumann_entropy(rho_active)

    security_evidence = {
        "bloch_original": bloch_orig,
        "bloch_received": bloch_active,
        "bloch_displacement": bloch_disp,
        "purity": purity,
        "von_neumann_entropy": von_neumann_entropy,
        "trace_distance": trace_dist,
        "fidelity": fidelity,
        "tvd": deviation,
        "qber": bit_error_rate,
        "density_matrix_original": density_matrix_to_dict(rho_orig),
        "density_matrix_received": density_matrix_to_dict(rho_active),
    }

    elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
    circuit_ascii = qc_z.draw(output="text").single_string()
    qiskit_code = build_verification_qiskit_code(active_state.theta_rad, active_state.phi_rad, shots)

    details = (
        "The message and quantum signature are authentic. "
        "All basis measurements are statistically consistent with the expected state."
        if decision == "LEGITIMATE"
        else (
            "Statistical anomaly detected in measurement distribution. "
            "Quantum signature verification FAILED. "
            f"Forgery indicator: {'DETECTED' if forgery_summary_schema.any_anomaly else 'NOT DETECTED'}."
        )
    )

    return VerificationResponse(
        signature_id=signature_id,
        message=message,
        expected_state=original_state,
        reconstructed_state=active_state,
        circuit_ascii=circuit_ascii,
        qiskit_code=qiskit_code,
        expected_distribution=expected_dist,
        observed_distribution=observed_dist,
        observed_counts=counts_z,
        basis_wise_results=basis_results,
        fidelity=fidelity,
        deviation=deviation,
        bit_error_rate=bit_error_rate,
        threat_score=threat_score,
        threshold=threshold,
        decision=decision,
        verification_time_ms=elapsed_ms,
        timestamp=datetime.now(timezone.utc).isoformat(),
        details=details,
        hoeffding_z=hoeffding_z_schema,
        hoeffding_x=hoeffding_x_schema,
        hoeffding_y=hoeffding_y_schema,
        forgery_summary=forgery_summary_schema,
        shots=shots,
        purity=purity,
        von_neumann_entropy=von_neumann_entropy,
        trace_distance=trace_dist,
        bloch_displacement=bloch_disp,
        security_evidence=security_evidence,
    )
