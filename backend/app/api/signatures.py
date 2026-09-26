import json
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database.session import get_db
from app.database.models import Message, Signature, Log
from app.schemas.schemas import (
    SignatureGenerateRequest,
    SignatureGenerateResponse,
    SignatureListItem
)
from app.quantum import (
    compute_sha256,
    hash_to_quantum_state,
    build_and_run_signature_circuit
)

router = APIRouter(prefix="/signatures", tags=["Signatures (Legacy Hash-to-State Demo)"])

@router.post("/generate", response_model=SignatureGenerateResponse)
def generate_signature(req: SignatureGenerateRequest, db: Session = Depends(get_db)):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    # 1. Quantum circuit execution and signature synthesis
    res = build_and_run_signature_circuit(req.message.strip(), shots=req.shots)

    # 2. Persist in database
    msg_obj = Message(
        content=req.message.strip(),
        hash=res.message_hash
    )
    db.add(msg_obj)
    db.flush()

    sig_obj = Signature(
        signature_id=res.signature_id,
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
        nonce=f"NONCE-{uuid.uuid4().hex[:8].upper()}",
        is_used=False,
        status="generated"
    )
    db.add(sig_obj)

    # 3. Log event
    log_obj = Log(
        event_type="Signature Generation",
        category="Signature",
        details=f"Generated signature {res.signature_id} for hash: {res.message_hash[:16]}... (Shots: {res.shots})",
        status="Success",
        source="Quantum Lab (Alice)",
        signature_id=res.signature_id
    )
    db.add(log_obj)

    db.commit()

    return res

@router.get("", response_model=list[SignatureListItem])
def list_signatures(limit: int = 50, db: Session = Depends(get_db)):
    sigs = db.query(Signature).order_by(desc(Signature.timestamp)).limit(limit).all()
    results = []
    for s in sigs:
        msg_text = s.message.content if s.message else "Message payload"
        results.append(SignatureListItem(
            signature_id=s.signature_id,
            message_snippet=msg_text[:40] + ("..." if len(msg_text) > 40 else ""),
            hash=s.hash,
            shots=s.shots,
            fidelity=s.fidelity,
            status=s.status,
            timestamp=s.timestamp.isoformat() if s.timestamp else ""
        ))
    return results

@router.get("/{signature_id}")
def get_signature_details(signature_id: str, db: Session = Depends(get_db)):
    sig = db.query(Signature).filter(Signature.signature_id == signature_id).first()
    if not sig:
        raise HTTPException(status_code=404, detail=f"Signature {signature_id} not found.")

    state_dict = json.loads(sig.state_vector)
    counts_dict = json.loads(sig.measurement_counts)

    return {
        "signature_id": sig.signature_id,
        "message": sig.message.content if sig.message else "",
        "hash": sig.hash,
        "state_vector": state_dict,
        "theta": sig.theta,
        "phi": sig.phi,
        "circuit": sig.circuit,
        "measurement_counts": counts_dict,
        "shots": sig.shots,
        "fidelity": sig.fidelity,
        "correction": sig.correction,
        "nonce": sig.nonce,
        "is_used": sig.is_used,
        "status": sig.status,
        "timestamp": sig.timestamp.isoformat() if sig.timestamp else ""
    }
