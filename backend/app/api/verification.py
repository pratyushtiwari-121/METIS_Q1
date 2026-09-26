import json
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.database.models import Signature, Verification, Log, Setting
from app.schemas.schemas import (
    VerificationRequest,
    VerificationResponse,
    StateVectorInfo
)
from app.quantum import (
    compute_sha256,
    hash_to_quantum_state,
    run_verification,
    state_info_from_angles
)

router = APIRouter(prefix="/verification", tags=["Verification (Legacy Hash-to-State Demo)"])

@router.post("/verify", response_model=VerificationResponse)
def verify_signature(req: VerificationRequest, db: Session = Depends(get_db)):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty for verification.")

    # 1. Fetch system default threshold if not provided
    threshold = req.threshold
    if threshold is None:
        th_setting = db.query(Setting).filter_by(key="verification_threshold").first()
        threshold = float(th_setting.value) if th_setting else 0.100

    # 2. Derive expected quantum state from the input message SHA-256
    calc_hex_hash, _ = compute_sha256(req.message.strip())
    expected_state = hash_to_quantum_state(calc_hex_hash)

    # 3. Locate signature record if signature_id is provided
    target_sig_id = req.signature_id or f"QSIG-VERIFY-{calc_hex_hash[:8].upper()}"
    tampered_state = None

    if req.tamper_state:
        tampered_state = req.tamper_state
    elif req.attack_scenario:
        scenario = req.attack_scenario.lower()
        if scenario in ["bit_flip", "channel", "channel manipulation"]:
            t_theta = (expected_state.theta_rad + 3.14159 * 0.65) % 3.14159
            t_phi = (expected_state.phi_rad + 3.14159 * 0.5) % (2 * 3.14159)
            tampered_state = state_info_from_angles(t_theta, t_phi)
        elif scenario in ["phase_flip", "phase"]:
            t_theta = expected_state.theta_rad
            t_phi = (expected_state.phi_rad + 3.14159 * 0.9) % (2 * 3.14159)
            tampered_state = state_info_from_angles(t_theta, t_phi)
        elif scenario in ["random_state", "impersonation", "impersonation attack", "unauthorized", "unauthorized verification"]:
            t_theta = 2.45
            t_phi = 1.25
            tampered_state = state_info_from_angles(t_theta, t_phi)
        elif scenario in ["forgery", "forgery attack", "tampered_message", "replay", "replay attack", "attack_injected"]:
            tampered_state = hash_to_quantum_state(f"FORGED_TAMPERED_{calc_hex_hash}")
        else:
            t_theta = (expected_state.theta_rad + 3.14159 * 0.65) % 3.14159
            t_phi = (expected_state.phi_rad + 3.14159 * 0.5) % (2 * 3.14159)
            tampered_state = state_info_from_angles(t_theta, t_phi)
    else:
        if req.signature_id:
            sig_record = db.query(Signature).filter(Signature.signature_id == req.signature_id).first()
            if sig_record:
                # Check if signature hash matches current message hash
                if sig_record.hash != calc_hex_hash:
                    # Tampered message or mismatched signature!
                    # We reconstruct state from signature, but expected state from message
                    sig_state_dict = json.loads(sig_record.state_vector)
                    tampered_state = StateVectorInfo(**sig_state_dict)

        # 4. If signature_hex was directly provided and differs from message hash:
        if req.signature_hex and req.signature_hex.strip() != calc_hex_hash:
            tampered_state = hash_to_quantum_state(req.signature_hex.strip())

    # 5. Run quantum multi-basis verification circuit
    res = run_verification(
        message=req.message.strip(),
        original_state=expected_state,
        signature_id=target_sig_id,
        shots=req.shots,
        threshold=threshold,
        tampered_state=tampered_state
    )

    # 6. Save verification to DB
    ver_obj = Verification(
        signature_id=target_sig_id,
        message_content=req.message.strip(),
        observed_counts=json.dumps(res.observed_counts),
        expected_distribution=json.dumps(res.expected_distribution),
        observed_distribution=json.dumps(res.observed_distribution),
        basis_distributions=json.dumps([b.model_dump() for b in res.basis_wise_results]),
        fidelity=res.fidelity,
        deviation=res.deviation,
        bit_error_rate=res.bit_error_rate,
        threat_score=res.threat_score,
        decision=res.decision,
        verification_time_ms=res.verification_time_ms
    )
    db.add(ver_obj)

    # 7. Log verification
    log_status = "Legitimate" if res.decision == "LEGITIMATE" else "Detected"
    db.add(Log(
        event_type="Signature Verification",
        category="Verification",
        details=f"Verification completed for {target_sig_id}. Decision: {res.decision} (Fidelity: {res.fidelity}, Deviation: {res.deviation})",
        status=log_status,
        source="Verifier (Bob)",
        signature_id=target_sig_id
    ))

    db.commit()

    return res

@router.get("/{verification_id}")
def get_verification_details(verification_id: int, db: Session = Depends(get_db)):
    ver = db.query(Verification).filter(Verification.id == verification_id).first()
    if not ver:
        raise HTTPException(status_code=404, detail=f"Verification record {verification_id} not found.")

    return {
        "id": ver.id,
        "signature_id": ver.signature_id,
        "message_content": ver.message_content,
        "observed_counts": json.loads(ver.observed_counts),
        "expected_distribution": json.loads(ver.expected_distribution),
        "observed_distribution": json.loads(ver.observed_distribution),
        "basis_distributions": json.loads(ver.basis_distributions) if ver.basis_distributions else [],
        "fidelity": ver.fidelity,
        "deviation": ver.deviation,
        "bit_error_rate": ver.bit_error_rate,
        "threat_score": ver.threat_score,
        "decision": ver.decision,
        "verification_time_ms": ver.verification_time_ms,
        "timestamp": ver.timestamp.isoformat() if ver.timestamp else ""
    }
