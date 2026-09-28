"""
Quantum Digital Signature (QDS) REST API Router.

Endpoints:
- POST /api/qds/keygen: Generate Pauli-eigenstate key pairs for bits b ∈ {0, 1}.
- POST /api/qds/distribute: Simulate EPR Bell pairs & teleport public-key states to 2+ verifiers.
- POST /api/qds/sign: Sign message bit b with classical private key string bound via SHA-256.
- POST /api/qds/verify: Measure verifier's stored states, calculate mismatch rate m, and evaluate thresholds.
- GET  /api/qds/thresholds: Retrieve threshold definitions and middle-zone documentation.
- GET  /api/qds/memory/{verifier_id}: Inspect verifier's quantum memory status.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Any

from app.schemas.schemas import (
    QDSKeygenRequest,
    QDSKeygenResponse,
    QDSDistributeRequest,
    QDSDistributeResponse,
    QDSSignRequest,
    QDSSignResponse,
    QDSVerifyRequest,
    QDSVerifyResponse,
)
from app.qds.keygen import (
    generate_qds_keypair,
    QDSPrivateKey,
    QDSPublicKey,
)
from app.qds.distribution import (
    distribute_public_keys,
    MEMORY_REGISTRY,
)
from app.qds.signing import (
    sign_message,
    QDSSignature,
)
from app.qds.verification import (
    verify_signature,
)
from app.qds.thresholds import (
    QDSThresholds,
)

router = APIRouter(prefix="/qds", tags=["Quantum Digital Signatures (QDS Protocol)"])

# In-memory session stores for generated keys and signatures
_KEY_STORE: dict[str, tuple[QDSPrivateKey, QDSPublicKey]] = {}
_SIG_STORE: dict[str, QDSSignature] = {}


@router.post("/keygen", response_model=QDSKeygenResponse)
def keygen_endpoint(req: QDSKeygenRequest):
    """
    Generate a new QDS key pair.
    The signer draws L random Pauli-eigenstates from {|0⟩, |1⟩, |+⟩, |-⟩, |+i⟩, |-i⟩}
    for each message bit b ∈ {0, 1}.
    """
    try:
        priv_key, pub_key = generate_qds_keypair(length=req.length, seed=req.seed)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    _KEY_STORE[priv_key.key_id] = (priv_key, pub_key)

    # Summarize public key distributions
    def state_counts(pk_list):
        counts = {}
        for s in pk_list:
            counts[s.label] = counts.get(s.label, 0) + 1
        return counts

    pk_summary = {
        "b0_states_count": len(pub_key.pk_0),
        "b0_distribution": state_counts(pub_key.pk_0),
        "b1_states_count": len(pub_key.pk_1),
        "b1_distribution": state_counts(pub_key.pk_1),
        "alphabet": ["|0⟩ (Z0)", "|1⟩ (Z1)", "|+⟩ (X0)", "|-⟩ (X1)", "|+i⟩ (Y0)", "|-i⟩ (Y1)"],
    }

    preview = [e.to_dict() for e in priv_key.sk_0[:8]]

    return QDSKeygenResponse(
        key_id=priv_key.key_id,
        length=priv_key.length,
        created_at=priv_key.created_at,
        public_key_summary=pk_summary,
        private_key_preview=preview,
    )


@router.post("/distribute", response_model=QDSDistributeResponse)
def distribute_endpoint(req: QDSDistributeRequest):
    """
    Quantum Public Key Distribution (QPKD).
    Distributes public key states to 2+ verifiers using EPR Bell pairs and
    feed-forward Pauli corrections, storing them into the verifiers' quantum memories.
    """
    if req.key_id not in _KEY_STORE:
        raise HTTPException(status_code=404, detail=f"Key ID '{req.key_id}' not found. Run keygen first.")

    _, pub_key = _KEY_STORE[req.key_id]

    if len(req.verifiers) < 2:
        raise HTTPException(status_code=400, detail="QDS requires distribution to at least 2 verifiers (e.g. Bob, Charlie).")

    memories = distribute_public_keys(
        public_key=pub_key,
        verifiers=req.verifiers,
        depolarizing_prob=req.depolarizing_prob,
        bit_flip_prob=req.bit_flip_prob,
        phase_flip_prob=req.phase_flip_prob,
        seed=req.seed,
    )

    verifiers_status = {}
    for vid, vmem in memories.items():
        verifiers_status[vid] = {
            "total_stored_states": vmem.total_stored,
            "avg_teleportation_fidelity": round(vmem.avg_fidelity, 4),
            "stored_at": vmem.stored_at,
        }

    total_states = sum(vmem.total_stored for vmem in memories.values())
    noise_present = (req.depolarizing_prob > 0 or req.bit_flip_prob > 0 or req.phase_flip_prob > 0)

    return QDSDistributeResponse(
        key_id=req.key_id,
        verifiers=req.verifiers,
        total_states_teleported=total_states,
        teleportation_method="EPR Bell Pairs + Feed-Forward Pauli Correction",
        noise_applied=noise_present,
        verifiers_status=verifiers_status,
    )


@router.post("/sign", response_model=QDSSignResponse)
def sign_endpoint(req: QDSSignRequest):
    """
    Sign a message bit b ∈ {0, 1} associated with message M.
    The signature is the classical private key string for bit b, cryptographically
    bound to the message digest via SHA-256.
    """
    if req.key_id not in _KEY_STORE:
        raise HTTPException(status_code=404, detail=f"Key ID '{req.key_id}' not found. Run keygen first.")

    priv_key, _ = _KEY_STORE[req.key_id]

    try:
        sig = sign_message(message=req.message, private_key=priv_key, bit=req.bit)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    _SIG_STORE[sig.signature_id] = sig

    return QDSSignResponse(
        signature_id=sig.signature_id,
        key_id=sig.key_id,
        message=sig.message,
        message_hash=sig.message_hash,
        bit=sig.bit,
        compact_string=sig.compact_string,
        binding_token=sig.binding_token,
        classical_signature=sig.classical_signature,
        created_at=sig.created_at,
    )


@router.post("/verify", response_model=QDSVerifyResponse)
def verify_endpoint(req: QDSVerifyRequest):
    """
    Verify a signature at a specified verifier (e.g. Bob or Charlie).
    The verifier performs projective measurements on stored quantum states in the claimed bases,
    computes mismatch rate m, and applies dual thresholds s_a < s_v < 0.5.
    """
    # 1. Resolve signature object
    sig_obj = None
    if req.signature_id and req.signature_id in _SIG_STORE:
        sig_obj = _SIG_STORE[req.signature_id]
    elif req.classical_signature and req.binding_token and req.compact_string:
        import hashlib
        msg_hash = hashlib.sha256(req.message.strip().encode("utf-8")).hexdigest()
        sig_obj = QDSSignature(
            signature_id=req.signature_id or f"QDSSIG-ADHOC",
            key_id=req.key_id,
            message=req.message.strip(),
            message_hash=msg_hash,
            bit=req.bit,
            classical_signature=req.classical_signature,
            compact_string=req.compact_string,
            binding_token=req.binding_token,
        )
    elif req.signature_id:
        raise HTTPException(status_code=404, detail=f"Signature ID '{req.signature_id}' not found in active session.")
    else:
        raise HTTPException(
            status_code=400,
            detail="Either provide an existing signature_id or supply classical_signature, compact_string, and binding_token."
        )

    # 2. Validate thresholds
    s_a = req.s_a if req.s_a is not None else 0.10
    s_v = req.s_v if req.s_v is not None else 0.25
    try:
        thresholds = QDSThresholds(s_a=s_a, s_v=s_v)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 3. Perform projective measurement verification
    try:
        res = verify_signature(
            signature=sig_obj,
            verifier_id=req.verifier_id,
            thresholds=thresholds,
            seed=req.seed,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    sample_positions = [p.to_dict() for p in res.positions[:10]]

    return QDSVerifyResponse(
        verifier_id=res.verifier_id,
        key_id=res.key_id,
        signature_id=res.signature_id,
        message=res.message,
        bit=res.bit,
        total_positions=res.total_positions,
        mismatch_count=res.mismatch_count,
        mismatch_rate=res.mismatch_rate,
        s_a=res.s_a,
        s_v=res.s_v,
        decision=res.decision.value,
        decision_reason=res.decision_reason,
        binding_valid=res.binding_valid,
        timestamp=res.timestamp,
        sample_positions=sample_positions,
    )


@router.get("/thresholds")
def get_thresholds_info():
    """
    Retrieve default QDS dual threshold settings and middle-zone documentation.
    """
    default_th = QDSThresholds()
    return {
        "s_a_default": default_th.s_a,
        "s_v_default": default_th.s_v,
        "valid_range": "0.0 <= s_a < s_v < 0.5",
        "zones": {
            "accept_zone": f"m <= s_a ({default_th.s_a}) -> ACCEPT. Honest noiseless signatures achieve m = 0 (100% acceptance).",
            "middle_zone": f"s_a < m <= s_v ({default_th.s_a} < m <= {default_th.s_v}) -> INCONCLUSIVE_ARBITRATION. Dispute resolution window.",
            "reject_zone": f"m > s_v ({default_th.s_v}) -> REJECT. High mismatch rate confirms forgery or unauthorized tampering.",
        },
        "security_rationale": (
            "The gap (s_v - s_a) prevents signer repudiation: Alice cannot prepare states that cause "
            "Bob to accept (m_B <= s_a) while causing Charlie to reject (m_C > s_v) without violating "
            "the No-Cloning theorem and quantum uncertainty bounds."
        )
    }


@router.get("/memory/{key_id}/{verifier_id}")
@router.get("/memory/{verifier_id}")
def get_verifier_memory(
    verifier_id: str,
    key_id: str | None = None,
    key_id_query: str | None = Query(default=None, alias="key_id", description="Key ID to inspect")
):
    """
    Inspect the status of a verifier's stored quantum memory.
    Supports either /memory/{key_id}/{verifier_id} or /memory/{verifier_id}?key_id=...
    """
    effective_key_id = key_id or key_id_query
    if not effective_key_id:
        raise HTTPException(status_code=400, detail="Missing key_id.")

    mem = MEMORY_REGISTRY.get_memory(effective_key_id, verifier_id)
    if not mem:
        raise HTTPException(status_code=404, detail=f"No memory found for verifier '{verifier_id}' and key '{effective_key_id}'.")

    return mem.to_dict(include_states=True)
