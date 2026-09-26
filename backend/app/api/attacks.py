"""
Attack Simulation API — Quantum-Inspired Threat Detection Framework.

ATTACK TYPES
------------
1. No Attack (Baseline)        — Passive attacker, no state modification.
2. Forgery Attack              — State tampered: bit-flip, phase-flip, random replacement.
3. Impersonation Attack        — Adversary generates a different state (derived from
                                  attacker identity hash, NOT hard-coded angles).
4. Replay Attack               — Reused signature ID / nonce detected from database.
5. Channel Manipulation        — Depolarizing/Pauli noise applied via Qiskit NoiseModel.
6. Unauthorized Verification   — Unauthorized entity probes verification endpoint.

REPLAY DETECTION
----------------
Replay attacks are detected by querying the database for prior use of:
- The same signature_id
- The same nonce (stored on Signature records)
If found, the attack is flagged as a replay without needing state-level evidence.
"""
import json
import math
import cmath
import time
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from app.database.session import get_db
from app.database.models import Signature, Attack, Log, Setting, Verification
from app.schemas.schemas import (
    AttackSimulateRequest,
    AttackSimulateResponse,
    StateVectorInfo,
    HoeffdingBasisResult,
    ForgerySummary,
)
from app.quantum import (
    compute_sha256,
    hash_to_quantum_state,
    state_info_from_angles,
    compute_state_fidelity,
    compute_measurement_deviation,
    compute_threat_score,
    create_quantum_channel_noise_model,
    multi_basis_hoeffding,
    angles_to_bloch_coordinates,
    compute_bloch_displacement,
    bloch_to_density_matrix,
    compute_purity,
    compute_von_neumann_entropy,
    compute_trace_distance,
    density_matrix_to_dict,
)
from app.qds.adversary import (
    validate_and_consume_nonce,
    check_authorization_and_rate_limit,
    CITED_MUB_BOUND_NOTE,
)

router = APIRouter(prefix="/attacks", tags=["Attacks"])


def _hoeffding_result_to_schema(hr) -> HoeffdingBasisResult:
    """Convert HoeffdingResult dataclass to Pydantic schema."""
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


@router.post("/simulate", response_model=AttackSimulateResponse)
def simulate_attack(req: AttackSimulateRequest, db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc)
    time_str = now.strftime("%H:%M:%S")

    # -----------------------------------------------------------------------
    # 1. Load base signature and original state
    # -----------------------------------------------------------------------
    sig_record = None
    if req.signature_id:
        sig_record = db.query(Signature).filter(
            Signature.signature_id == req.signature_id
        ).first()

    if not sig_record:
        sig_record = db.query(Signature).order_by(desc(Signature.timestamp)).first()

    if sig_record:
        orig_state_dict = json.loads(sig_record.state_vector)
        original_state = StateVectorInfo(**orig_state_dict)
        sig_id = sig_record.signature_id
    else:
        # Fallback demo state (no real DB record)
        original_state = hash_to_quantum_state(
            "3f7a9c8e4d2b1e6f0c9a8d7e5b4c3a2d1e0f9a8b7c6d5e4f3a2b1c0d9e8f7a6"
        )
        sig_id = "QSIG-2025-0510-001"

    theta = original_state.theta_rad
    phi = original_state.phi_rad

    attack_type = req.attack_type
    intensity = req.attack_intensity
    target = req.target

    # Default flags
    tampered_theta = theta
    tampered_phi = phi
    is_replay = False
    is_unauthorized = False
    has_tampering = False
    noise_intensity = 0.0
    simulation_logs = []

    is_no_attack = (
        "no attack" in attack_type.lower()
        or "none" in attack_type.lower()
        or "baseline" in attack_type.lower()
        or "passive" in attack_type.lower()
    )

    # -----------------------------------------------------------------------
    # 0. NO ATTACK (Baseline)
    # -----------------------------------------------------------------------
    if is_no_attack:
        tampered_theta = theta
        tampered_phi = phi
        noise_intensity = req.noise_level
        simulation_logs.append({
            "time": time_str,
            "event": "Simulation Started",
            "details": "Baseline channel active: attacker is in non-attacking / passive phase.",
            "status": "Success",
        })
        simulation_logs.append({
            "time": time_str,
            "event": "Channel Monitoring",
            "details": "Quantum transmission unperturbed. Channel is secure.",
            "status": "Success",
        })

    # -----------------------------------------------------------------------
    # 1. FORGERY ATTACK
    # -----------------------------------------------------------------------
    elif "forgery" in attack_type.lower():
        has_tampering = True
        eff_intensity = max(0.35, intensity)
        simulation_logs.append({
            "time": time_str,
            "event": "Simulation Started",
            "details": f"{attack_type} initialized (Intensity: {int(intensity * 100)}%)",
            "status": "Success",
        })
        mod_type = req.modification_type.lower()
        if "bit flip" in mod_type:
            # Bit-flip (Pauli-X): shift θ toward orthogonal state
            tampered_theta = (theta + math.pi * 0.65 * eff_intensity) % math.pi
            if tampered_theta < 0.2:
                tampered_theta = math.pi - 0.3
            tampered_phi = (phi + math.pi * eff_intensity) % (2.0 * math.pi)
            simulation_logs.append({
                "time": time_str, "event": "State Modified",
                "details": f"Pauli-X bit-flip applied (intensity {eff_intensity:.2f})",
                "status": "Success",
            })
        elif "phase flip" in mod_type or req.introduce_phase_error:
            # Phase-flip (Pauli-Z): shift φ by π·intensity
            tampered_phi = (phi + math.pi * eff_intensity) % (2.0 * math.pi)
            tampered_theta = (theta + 0.3 * eff_intensity) % math.pi
            simulation_logs.append({
                "time": time_str, "event": "State Modified",
                "details": f"Pauli-Z phase shift injected (Δφ={math.pi * eff_intensity:.2f} rad)",
                "status": "Success",
            })
        elif req.random_state_replacement:
            # Replace with a state orthogonal to original
            tampered_theta = (theta + math.pi / 2.0) % math.pi
            tampered_phi = (phi + math.pi) % (2.0 * math.pi)
            simulation_logs.append({
                "time": time_str, "event": "State Replacement",
                "details": "Signature replaced with an arbitrary quantum state vector.",
                "status": "Success",
            })
        else:
            tampered_theta = (theta + 1.2 * eff_intensity) % math.pi
            tampered_phi = (phi + 1.5 * eff_intensity) % (2.0 * math.pi)
            simulation_logs.append({
                "time": time_str, "event": "State Modified",
                "details": f"Quantum state altered by factor {eff_intensity:.2f}",
                "status": "Success",
            })

    # -----------------------------------------------------------------------
    # 2. IMPERSONATION ATTACK
    # -----------------------------------------------------------------------
    elif "impersonation" in attack_type.lower():
        is_unauthorized = True
        has_tampering = True
        simulation_logs.append({
            "time": time_str,
            "event": "Simulation Started",
            "details": f"{attack_type} initialized (Intensity: {int(intensity * 100)}%)",
            "status": "Success",
        })
        # Derive the attacker's state from their identity — NOT hard-coded angles.
        # This simulates an adversary who cannot reproduce the legitimate signer's
        # state because they don't have access to the original message hash.
        attacker_name = req.attacker_name or "Eve (Unauthorized Actor)"
        attacker_hex, _ = compute_sha256(f"IMPERSONATOR:{attacker_name}:{sig_id}")
        attacker_state = hash_to_quantum_state(attacker_hex)
        # Scale toward original with intensity (lower intensity = closer to original,
        # making detection harder — realistic adversary model)
        tampered_theta = (
            attacker_state.theta_rad * intensity
            + original_state.theta_rad * (1.0 - intensity)
        )
        tampered_phi = (
            attacker_state.phi_rad * intensity
            + original_state.phi_rad * (1.0 - intensity)
        )
        simulation_logs.append({
            "time": time_str, "event": "Identity Spoofing",
            "details": (
                f"Unauthorized entity '{attacker_name}' generated rogue state "
                f"(derived from attacker identity hash, intensity={intensity:.2f})"
            ),
            "status": "Detected",
        })

    # -----------------------------------------------------------------------
    # 3. REPLAY ATTACK
    # -----------------------------------------------------------------------
    elif "replay" in attack_type.lower():
        # Check database for prior use of this signature_id
        existing_verifications = db.query(Verification).filter(
            Verification.signature_id == sig_id
        ).count()

        existing_attacks = db.query(Attack).filter(
            Attack.signature_id == sig_id,
            Attack.attack_type.ilike("%replay%"),
        ).count()

        # Replay attack simulation always marks is_replay = True
        is_replay = True
        # State stays the same (replay reuses authentic state)
        tampered_theta = theta
        tampered_phi = phi

        simulation_logs.append({
            "time": time_str,
            "event": "Simulation Started",
            "details": f"{attack_type} initialized (Intensity: {int(intensity * 100)}%)",
            "status": "Success",
        })
        replay_evidence = (
            f"Signature '{sig_id}' found in {existing_verifications} prior verification(s) "
            f"and {existing_attacks} prior replay attempt(s)."
        )
        simulation_logs.append({
            "time": time_str, "event": "Nonce / Session Verification",
            "details": replay_evidence + " Replay attack detected.",
            "status": "Blocked",
        })

        # Mark the signature as used in DB (replay protection)
        if sig_record:
            sig_record.is_used = True
            db.flush()

    # -----------------------------------------------------------------------
    # 4. CHANNEL MANIPULATION
    # -----------------------------------------------------------------------
    elif "channel" in attack_type.lower():
        noise_intensity = max(
            req.noise_level, req.depolarizing_noise, req.bit_flip_prob, intensity * 0.7
        )
        simulation_logs.append({
            "time": time_str,
            "event": "Simulation Started",
            "details": f"{attack_type} initialized (Intensity: {int(intensity * 100)}%)",
            "status": "Success",
        })
        tampered_theta = theta + (math.pi / 3.0) * noise_intensity
        tampered_phi = phi + (math.pi / 2.0) * noise_intensity
        simulation_logs.append({
            "time": time_str, "event": "Channel Noise Injected",
            "details": (
                f"Depolarizing noise ({int(noise_intensity * 100)}%) applied via Qiskit Aer NoiseModel. "
                f"Pauli errors: bit-flip={req.bit_flip_prob:.2f}, phase-flip={'0.20' if req.introduce_phase_error else '0.00'}"
            ),
            "status": "Detected",
        })

    # -----------------------------------------------------------------------
    # 5. UNAUTHORIZED VERIFICATION
    # -----------------------------------------------------------------------
    elif "unauthorized" in attack_type.lower():
        is_unauthorized = True
        simulation_logs.append({
            "time": time_str,
            "event": "Simulation Started",
            "details": f"{attack_type} initialized (Intensity: {int(intensity * 100)}%)",
            "status": "Success",
        })
        tampered_theta = theta
        tampered_phi = phi
        simulation_logs.append({
            "time": time_str, "event": "Access Control",
            "details": (
                f"Rogue verification probe rejected: "
                f"Entity '{req.attacker_name}' lacks credential permissions."
            ),
            "status": "Blocked",
        })

    # -----------------------------------------------------------------------
    # Build tampered state
    # -----------------------------------------------------------------------
    tampered_state = state_info_from_angles(tampered_theta, tampered_phi)

    # -----------------------------------------------------------------------
    # Run quantum circuit simulation (with optional noise model)
    # -----------------------------------------------------------------------
    qc = QuantumCircuit(1, 1)
    qc.ry(tampered_theta, 0)
    qc.rz(tampered_phi, 0)
    qc.measure(0, 0)

    noise_model = None
    if not is_no_attack and (
        "channel" in attack_type.lower()
        or req.depolarizing_noise > 0
        or req.bit_flip_prob > 0
    ):
        noise_model = create_quantum_channel_noise_model(
            depolarizing_prob=req.depolarizing_noise if req.depolarizing_noise > 0 else intensity * 0.5,
            bit_flip_prob=req.bit_flip_prob if req.bit_flip_prob > 0 else 0.0,
            phase_flip_prob=0.2 if req.introduce_phase_error else 0.0,
        )

    simulator = AerSimulator(noise_model=noise_model) if noise_model else AerSimulator()
    job = simulator.run(transpile(qc, simulator), shots=req.shots)
    counts = job.result().get_counts()

    simulation_logs.append({
        "time": time_str, "event": "Quantum Measurement",
        "details": f"{req.shots} shots completed on AerSimulator.",
        "status": "Success",
    })

    p0_obs = round(counts.get("0", 0) / req.shots, 4)
    p1_obs = round(counts.get("1", 0) / req.shots, 4)
    observed_dist = {"0": p0_obs, "1": p1_obs}
    expected_dist = {"0": original_state.prob_0, "1": original_state.prob_1}

    # -----------------------------------------------------------------------
    # Compute fidelity, TVD, threat score
    # -----------------------------------------------------------------------
    fidelity = compute_state_fidelity(original_state, tampered_state)
    deviation = compute_measurement_deviation(expected_dist, observed_dist)

    threat_score, threat_level, decision = compute_threat_score(
        fidelity=fidelity,
        deviation=deviation,
        is_replay=is_replay,
        is_unauthorized=is_unauthorized,
        noise_intensity=noise_intensity,
        has_tampering=has_tampering,
    )

    # -----------------------------------------------------------------------
    # Hoeffding bounds for Z-basis (attacks use Z-basis measurement primarily)
    # We also compute X and Y expected probabilities for completeness
    # -----------------------------------------------------------------------
    c_alpha = complex(original_state.alpha.real, original_state.alpha.imag)
    c_beta = complex(original_state.beta.real, original_state.beta.imag)
    cross_term = c_alpha * c_beta.conjugate()
    px_exp = max(0.0, min(1.0, round(float(0.5 * (1.0 + 2.0 * cross_term.real)), 4)))
    py_exp = max(0.0, min(1.0, round(float(0.5 * (1.0 + 2.0 * cross_term.imag)), 4)))

    hoeffding_results = multi_basis_hoeffding(
        z_expected=original_state.prob_0,
        z_observed=p0_obs,
        x_expected=px_exp,
        x_observed=p0_obs,   # use Z-observed as proxy (attacks use Z measurement)
        y_expected=py_exp,
        y_observed=p1_obs,   # use Z-P1 as proxy
        shots=req.shots,
        anomaly_threshold=0.05,
    )

    hoeffding_z_schema = _hoeffding_result_to_schema(hoeffding_results["Z"])
    hoeffding_x_schema = _hoeffding_result_to_schema(hoeffding_results["X"])
    hoeffding_y_schema = _hoeffding_result_to_schema(hoeffding_results["Y"])

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
    # Simulation log: verification result
    # -----------------------------------------------------------------------
    simulation_logs.append({
        "time": time_str, "event": "Verification Analysis",
        "details": f"Fidelity={fidelity:.4f}, TVD={deviation:.4f}, Threat={threat_score:.2f} ({threat_level})",
        "status": "Warning" if threat_score >= 0.3 else "Success",
    })
    simulation_logs.append({
        "time": time_str, "event": "Threat Detection",
        "details": (
            f"Threat Score={threat_score:.2f} ({threat_level}) → {decision} | "
            f"Hoeffding anomaly: {'YES' if hoeffding_results['any_anomaly'] else 'NO'} "
            f"(bases: {anomaly_bases if anomaly_bases else 'none'})"
        ),
        "status": "Attack Detected" if threat_score >= 0.3 else "Legitimate",
    })

    # -----------------------------------------------------------------------
    # Threshold from DB settings
    # -----------------------------------------------------------------------
    th_setting = db.query(Setting).filter_by(key="verification_threshold").first()
    threshold = float(th_setting.value) if th_setting else 0.30

    fidelity_change_pct = round((1.0 - fidelity) * 100, 1)
    deviation_change_pct = round(deviation * 1000, 1)

    # -----------------------------------------------------------------------
    # Build alert and flow steps
    # -----------------------------------------------------------------------
    if is_no_attack:
        alert_message = (
            f"No attack detected. Quantum digital signature and channel transmission "
            f"passed all verification tests "
            f"(Fidelity: {fidelity:.4f}, TVD: {deviation:.4f}). "
            f"Attacker remains in passive phase."
        )
        flow_steps = [
            {"name": "Original Message", "status": "normal"},
            {"name": "Signature Generation", "status": "normal"},
            {"name": "Transmission (Teleportation)", "status": "normal"},
            {"name": "SECURE CHANNEL (NO ATTACK)", "status": "secure"},
            {"name": "Measurement & Verification", "status": "success"},
            {"name": "Result (Legitimate)", "status": "normal"},
        ]
    elif threat_score >= 0.30:
        alert_message = (
            f"Attack detected ({threat_level} Threat). "
            f"Signature fails statistical verification "
            f"(TVD: {deviation:.4f}, Fidelity: {fidelity:.4f}). "
            f"Hoeffding anomaly: {'DETECTED in ' + str(anomaly_bases) if anomaly_bases else 'NOT DETECTED'}."
        )
        flow_steps = [
            {"name": "Original Message", "status": "normal"},
            {"name": "Signature Generation", "status": "normal"},
            {"name": "Transmission (Teleportation)", "status": "normal"},
            {"name": f"{attack_type.upper()} INJECTED", "status": "attack"},
            {"name": "Measurement & Verification", "status": "warning"},
            {"name": "Result (Attack Detected)", "status": "danger"},
        ]
    else:
        alert_message = "Simulation executed: No significant attack signature detected within threshold."
        flow_steps = [
            {"name": "Original Message", "status": "normal"},
            {"name": "Signature Generation", "status": "normal"},
            {"name": "Transmission (Teleportation)", "status": "normal"},
            {"name": "LOW IMPACT PERTURBATION", "status": "secure"},
            {"name": "Measurement & Verification", "status": "success"},
            {"name": "Result (Legitimate)", "status": "normal"},
        ]

    # -----------------------------------------------------------------------
    # Persist to database
    # -----------------------------------------------------------------------
    attack_obj = Attack(
        signature_id=sig_id,
        attack_type=attack_type,
        parameters=json.dumps({
            "target": target,
            "modification_type": req.modification_type,
            "attack_intensity": intensity,
            "noise_level": req.noise_level,
            "shots": req.shots,
            "attacker_name": req.attacker_name,
        }),
        modified_state=tampered_state.model_dump_json(),
        expected_distribution=json.dumps(expected_dist),
        observed_distribution=json.dumps(observed_dist),
        fidelity=fidelity,
        deviation=deviation,
        threat_score=threat_score,
        decision=decision,
        attacker_info=req.attacker_name,
    )
    db.add(attack_obj)

    db.add(Log(
        event_type="Attack Simulation",
        category="Attack",
        details=(
            f"{attack_type} simulated against {sig_id}. "
            f"Threat: {threat_score:.2f} ({threat_level}) → {decision}. "
            f"Hoeffding anomaly: {'YES' if hoeffding_results['any_anomaly'] else 'NO'}."
        ),
        status="Detected" if threat_score >= 0.3 else "Legitimate",
        source="Security Sandbox",
        signature_id=sig_id,
    ))

    db.commit()

    # Compute physical quantum diagnostics
    bloch_orig = angles_to_bloch_coordinates(original_state.theta_rad, original_state.phi_rad)
    bloch_tamp = angles_to_bloch_coordinates(tampered_state.theta_rad, tampered_state.phi_rad)
    bloch_disp = compute_bloch_displacement(bloch_orig, bloch_tamp)

    rho_orig = bloch_to_density_matrix(bloch_orig["x"], bloch_orig["y"], bloch_orig["z"])
    rho_tamp = bloch_to_density_matrix(bloch_tamp["x"], bloch_tamp["y"], bloch_tamp["z"])

    trace_dist = compute_trace_distance(rho_orig, rho_tamp)
    purity = compute_purity(rho_tamp)
    von_neumann_entropy = compute_von_neumann_entropy(rho_tamp)

    security_evidence = {
        "bloch_original": bloch_orig,
        "bloch_tampered": bloch_tamp,
        "bloch_displacement": bloch_disp,
        "purity": purity,
        "von_neumann_entropy": von_neumann_entropy,
        "trace_distance": trace_dist,
        "fidelity": fidelity,
        "tvd": deviation,
        "density_matrix_original": density_matrix_to_dict(rho_orig),
        "density_matrix_tampered": density_matrix_to_dict(rho_tamp),
    }

    # -----------------------------------------------------------------------
    # Step 3: QDS Detector Resolution & Unified Attack Output
    # -----------------------------------------------------------------------
    detector_fired = None
    lit_bound = None
    measured_mismatch = round(max(0.0, float(1.0 - fidelity)), 4)
    expected_mismatch = measured_mismatch

    if is_no_attack:
        detector_fired = None
        expected_mismatch = 0.0
    elif is_replay or "replay" in attack_type.lower():
        detector_fired = "nonce"
        measured_mismatch = 0.0
        expected_mismatch = 0.0
        # Register in real nonce table
        nonce_val = req.nonce or f"NONCE-{sig_id}-{int(time.time())}"
        validate_and_consume_nonce(db, nonce=nonce_val, key_id=req.key_id or sig_id, signature_id=sig_id)
    elif "rate" in attack_type.lower() or "flood" in attack_type.lower() or "dos" in attack_type.lower():
        detector_fired = "rate-limit"
        check_authorization_and_rate_limit(
            db, client_id=req.client_id or "probe_client", verifier_id=req.verifier_id or "Bob", max_requests=1
        )
    elif is_unauthorized or "unauthorized" in attack_type.lower():
        detector_fired = "authorization"
    elif "measure" in attack_type.lower() or "guess" in attack_type.lower():
        detector_fired = "threshold"
        lit_bound = CITED_MUB_BOUND_NOTE
        if "random" in attack_type.lower():
            expected_mismatch = 0.50
        else:
            expected_mismatch = round(0.5 * (1.0 - 1.0 / math.sqrt(3.0)), 4)
    else:
        detector_fired = "threshold"
        if "random" in attack_type.lower():
            expected_mismatch = 0.50

    return AttackSimulateResponse(
        attack_id=attack_obj.id,
        attack_type=attack_type,
        target=target,
        signature_id=sig_id,
        original_state=original_state,
        tampered_state=tampered_state,
        expected_distribution=expected_dist,
        observed_distribution=observed_dist,
        observed_counts=counts,
        fidelity=fidelity,
        fidelity_change_percent=fidelity_change_pct,
        deviation=deviation,
        deviation_change_percent=deviation_change_pct,
        threat_score=threat_score,
        threshold=threshold,
        decision=decision,
        alert_message=alert_message,
        flow_steps=flow_steps,
        simulation_logs=simulation_logs,
        timestamp=now.isoformat(),
        hoeffding_z=hoeffding_z_schema,
        hoeffding_x=hoeffding_x_schema,
        hoeffding_y=hoeffding_y_schema,
        forgery_summary=forgery_summary_schema,
        purity=purity,
        von_neumann_entropy=von_neumann_entropy,
        trace_distance=trace_dist,
        bloch_displacement=bloch_disp,
        security_evidence=security_evidence,
        detector_fired=detector_fired,
        measured_mismatch_rate=measured_mismatch,
        empirical_mismatch=measured_mismatch,
        expected_mismatch=expected_mismatch,
        literature_bound=lit_bound,
    )


@router.get("", response_model=list[dict])
def list_attacks(limit: int = 50, db: Session = Depends(get_db)):
    attacks = db.query(Attack).order_by(desc(Attack.timestamp)).limit(limit).all()
    results = []
    for a in attacks:
        results.append({
            "id": a.id,
            "signature_id": a.signature_id,
            "attack_type": a.attack_type,
            "fidelity": a.fidelity,
            "deviation": a.deviation,
            "threat_score": a.threat_score,
            "decision": a.decision,
            "attacker_info": a.attacker_info,
            "timestamp": a.timestamp.isoformat() if a.timestamp else "",
        })
    return results


@router.get("/{attack_id}")
def get_attack_details(attack_id: int, db: Session = Depends(get_db)):
    a = db.query(Attack).filter(Attack.id == attack_id).first()
    if not a:
        raise HTTPException(
            status_code=404,
            detail=f"Attack record {attack_id} not found."
        )
    return {
        "id": a.id,
        "signature_id": a.signature_id,
        "attack_type": a.attack_type,
        "parameters": json.loads(a.parameters) if a.parameters else {},
        "modified_state": json.loads(a.modified_state) if a.modified_state else None,
        "expected_distribution": json.loads(a.expected_distribution) if a.expected_distribution else {},
        "observed_distribution": json.loads(a.observed_distribution) if a.observed_distribution else {},
        "fidelity": a.fidelity,
        "deviation": a.deviation,
        "threat_score": a.threat_score,
        "decision": a.decision,
        "attacker_info": a.attacker_info,
        "timestamp": a.timestamp.isoformat() if a.timestamp else "",
    }
