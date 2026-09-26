"""
Database seed service to populate initial realistic demo data on startup.
"""
import json
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from app.database.models import Message, Signature, Verification, Attack, QuantumCircuitRecord, Log, Setting
from app.quantum import (
    compute_sha256,
    hash_to_quantum_state,
    build_and_run_signature_circuit,
    run_verification
)

def seed_initial_data(db: Session):
    """Populates database with initial demo data if empty."""
    if db.query(Signature).count() > 0:
        return  # already seeded

    now = datetime.now(timezone.utc)

    # 1. Default Settings
    default_settings = {
        "app_name": "Quantum Digital Signature Security",
        "theme": "dark-quantum",
        "language": "en",
        "timezone": "Asia/Kolkata",
        "default_shots": "1024",
        "default_qubits": "2",
        "simulator_backend": "Qiskit Aer Simulator (Local)",
        "measurement_basis": "Computational (Z-basis)",
        "verification_threshold": "0.100",
        "fidelity_threshold": "0.850",
        "max_verification_attempts": "5",
        "replay_protection": "true",
        "attack_detection_sensitivity": "High",
        "enable_logging": "true",
        "log_retention_days": "30",
        "security_alerts": "true",
        "alert_on_attack": "true",
        "alert_on_verification_failure": "true",
        "noise_model_enabled": "false",
        "debug_mode": "false",
        "simulation_seed": "42"
    }
    for k, v in default_settings.items():
        if not db.query(Setting).filter_by(key=k).first():
            db.add(Setting(key=k, value=v, description=f"System setting for {k}"))

    # 2. Seed Messages & Signatures
    demo_messages = [
        "Secure communication with quantum signatures!",
        "Smart India Hackathon 2025 - Mentis-Q Security",
        "Entangled photon transmission protocol initiated.",
        "Authorization token for quantum key exchange matrix."
    ]

    stored_sigs = []
    for i, msg in enumerate(demo_messages):
        res = build_and_run_signature_circuit(msg, shots=1024)
        msg_obj = Message(
            content=msg,
            hash=res.message_hash,
            created_at=now - timedelta(minutes=40 - i * 10)
        )
        db.add(msg_obj)
        db.flush()

        sig_obj = Signature(
            signature_id=f"QSIG-2025-0510-00{i+1}",
            message_id=msg_obj.id,
            hash=res.message_hash,
            state_vector=res.state_vector.model_dump_json(),
            theta=res.state_vector.theta_rad,
            phi=res.state_vector.phi_rad,
            circuit=res.circuit_ascii,
            measurement_counts=json.dumps(res.measurement_counts),
            shots=res.shots,
            fidelity=res.fidelity,
            correction=res.pauli_correction,
            nonce=f"NONCE-{1000 + i}",
            is_used=(i == 1),  # mark one as used for replay test
            status="generated",
            timestamp=now - timedelta(minutes=40 - i * 10)
        )
        db.add(sig_obj)
        db.flush()
        stored_sigs.append((msg, sig_obj, res.state_vector))

        # Add Log
        db.add(Log(
            timestamp=now - timedelta(minutes=40 - i * 10),
            event_type="Signature Generation",
            category="Signature",
            details=f"Generated quantum signature {sig_obj.signature_id} for message: '{msg[:30]}...'",
            status="Success",
            source="Quantum Lab (Alice)",
            signature_id=sig_obj.signature_id
        ))

    # 3. Seed Verifications (Legitimate)
    if stored_sigs:
        msg0, sig0, state0 = stored_sigs[0]
        v_res = run_verification(msg0, state0, sig0.signature_id, shots=1024, threshold=0.100)
        db.add(Verification(
            signature_id=sig0.signature_id,
            message_content=msg0,
            observed_counts=json.dumps(v_res.observed_counts),
            expected_distribution=json.dumps(v_res.expected_distribution),
            observed_distribution=json.dumps(v_res.observed_distribution),
            basis_distributions=json.dumps([b.model_dump() for b in v_res.basis_wise_results]),
            fidelity=v_res.fidelity,
            deviation=v_res.deviation,
            bit_error_rate=v_res.bit_error_rate,
            threat_score=v_res.threat_score,
            decision="LEGITIMATE",
            verification_time_ms=v_res.verification_time_ms,
            timestamp=now - timedelta(minutes=15)
        ))

        db.add(Log(
            timestamp=now - timedelta(minutes=15),
            event_type="Signature Verification",
            category="Verification",
            details=f"Message verified successfully. Fidelity: {v_res.fidelity}, Deviation: {v_res.deviation}",
            status="Legitimate",
            source="Verifier (Bob)",
            signature_id=sig0.signature_id
        ))

    # 4. Seed Attack Simulations (Forgery, Replay, Channel Noise)
    # NOTE: These initial static records are for bootstrap UI demonstration and are explicitly
    # labeled as [SYNTHETIC SEED DEMO]. Live evaluation should use /api/analysis/* or /api/attacks/simulate.
    # Attack 1: Forgery [SYNTHETIC SEED DEMO]
    db.add(Attack(
        signature_id=stored_sigs[0][1].signature_id,
        attack_type="[SYNTHETIC SEED DEMO] Forgery Attack",
        parameters=json.dumps({"modification_type": "Bit Flip", "attack_intensity": 0.5, "is_synthetic": True}),
        modified_state=json.dumps({"theta": 2.14, "phi": 1.57}),
        expected_distribution=json.dumps({"0": 0.50, "1": 0.50}),
        observed_distribution=json.dumps({"0": 0.72, "1": 0.28}),
        fidelity=0.612,
        deviation=0.22,
        threat_score=0.78,
        decision="ATTACK DETECTED",
        attacker_info="Eve (Adversary - Synthetic Seed)",
        timestamp=now - timedelta(minutes=10)
    ))
    db.add(Log(
        timestamp=now - timedelta(minutes=10),
        event_type="Attack Simulation",
        category="Attack",
        details="[SYNTHETIC SEED DEMO] Forgery attack simulated: Quantum state altered via Pauli-X bit flip. Threat Score: 0.78",
        status="Detected",
        source="Security Analyzer (Seed)",
        signature_id=stored_sigs[0][1].signature_id
    ))

    # Attack 2: Replay Attack [SYNTHETIC SEED DEMO]
    db.add(Attack(
        signature_id=stored_sigs[1][1].signature_id,
        attack_type="[SYNTHETIC SEED DEMO] Replay Attack",
        parameters=json.dumps({"replayed_signature_id": stored_sigs[1][1].signature_id, "nonce": "NONCE-1001", "is_synthetic": True}),
        modified_state=None,
        expected_distribution=json.dumps({"0": 0.50, "1": 0.50}),
        observed_distribution=json.dumps({"0": 0.50, "1": 0.50}),
        fidelity=1.0,
        deviation=0.0,
        threat_score=0.85,
        decision="REPLAY ATTACK DETECTED",
        attacker_info="Eve (Replay Proxy - Synthetic Seed)",
        timestamp=now - timedelta(minutes=8)
    ))
    db.add(Log(
        timestamp=now - timedelta(minutes=8),
        event_type="Replay Attack",
        category="Security",
        details=f"[SYNTHETIC SEED DEMO] Replay attack detected: Expired nonce/signature {stored_sigs[1][1].signature_id} submitted.",
        status="Blocked",
        source="Replay Protection Guard (Seed)",
        signature_id=stored_sigs[1][1].signature_id
    ))

    # Attack 3: Channel Manipulation [SYNTHETIC SEED DEMO]
    db.add(Attack(
        signature_id=stored_sigs[2][1].signature_id,
        attack_type="[SYNTHETIC SEED DEMO] Channel Manipulation",
        parameters=json.dumps({"noise_level": 0.40, "depolarizing_noise": 0.35, "is_synthetic": True}),
        modified_state=None,
        expected_distribution=json.dumps({"0": 0.65, "1": 0.35}),
        observed_distribution=json.dumps({"0": 0.52, "1": 0.48}),
        fidelity=0.745,
        deviation=0.13,
        threat_score=0.68,
        decision="CHANNEL NOISE ATTACK DETECTED",
        attacker_info="Noisy Quantum Fiber Eavesdropper (Synthetic Seed)",
        timestamp=now - timedelta(minutes=5)
    ))
    db.add(Log(
        timestamp=now - timedelta(minutes=5),
        event_type="Channel Manipulation",
        category="Attack",
        details="[SYNTHETIC SEED DEMO] Quantum channel noise introduced: Depolarizing noise 35%. State fidelity degraded to 0.745.",
        status="Detected",
        source="Channel Monitor (Seed)",
        signature_id=stored_sigs[2][1].signature_id
    ))

    # 5. Predefined Quantum Circuits
    circuits_to_seed = [
        ("Bell State Generation", "Creates entangled state |Phi+> = (|00> + |11>)/sqrt(2)", 2, 2, 2, "Entanglement"),
        ("Quantum Teleportation", "Transmits quantum state |psi> via shared Bell pair and classical feed-forward", 3, 4, 6, "Protocol"),
        ("Single Qubit Superposition", "Applies Hadamard gate to initialize equal superposition |+>", 1, 1, 1, "Superposition")
    ]
    for name, desc, q, depth, gates, ctype in circuits_to_seed:
        db.add(QuantumCircuitRecord(
            name=name,
            description=desc,
            qubits=q,
            depth=depth,
            gates=gates,
            circuit_type=ctype,
            qiskit_code="# Predefined Qiskit Circuit",
            created_at=now - timedelta(hours=1)
        ))

    db.commit()
