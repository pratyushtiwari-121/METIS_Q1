"""
QDS Signature Verification Module.

Verification Protocol:
1. Verifier (e.g. Bob or Charlie) accesses their local Quantum Memory for the signed bit b.
2. The memory contains stored quantum states Q_0, Q_1, ..., Q_{L-1}.
3. The signature reveals Alice's claimed classical private key:
   sk_b = [(basis_0, bit_0), ..., (basis_{L-1}, bit_{L-1})].
4. Verifier performs projective measurement on Q_i in the claimed basis_i:
   - For basis 'Z': projective measurement onto {|0⟩, |1⟩}
   - For basis 'X': projective measurement onto {|+⟩, |-⟩}
   - For basis 'Y': projective measurement onto {|+i⟩, |-i⟩}
5. Each measurement yields observed bit obs_i ∈ {0, 1}.
   - Mismatch at position i occurs if obs_i != claimed_bit_i.
6. Mismatch Rate:
   m = (number of mismatches) / L
7. Decision via Dual Thresholds (0 <= s_a < s_v < 0.5):
   - m <= s_a: ACCEPT (honest noiseless gives m=0, accepted 100%)
   - m > s_v: REJECT (excessive mismatch, attack/forgery detected)
   - s_a < m <= s_v: INCONCLUSIVE / ARBITRATION (middle zone)
"""

import math
import hashlib
import numpy as np
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Literal

from app.qds.keygen import BasisType
from app.qds.distribution import StoredQuantumState, VerifierMemory, MEMORY_REGISTRY
from app.qds.signing import QDSSignature
from app.qds.thresholds import QDSThresholds, QDSDecision, evaluate_mismatch


@dataclass
class PositionVerificationResult:
    """Per-position verification diagnostic."""
    position: int
    claimed_basis: BasisType
    claimed_bit: int
    observed_bit: int
    mismatch: bool
    prob_0: float
    prob_1: float
    original_state_label: str

    def to_dict(self) -> dict:
        return {
            "position": self.position,
            "claimed_basis": self.claimed_basis,
            "claimed_bit": self.claimed_bit,
            "observed_bit": self.observed_bit,
            "mismatch": self.mismatch,
            "prob_0": round(self.prob_0, 4),
            "prob_1": round(self.prob_1, 4),
            "original_state_label": self.original_state_label,
        }


@dataclass
class QDSVerificationResult:
    """Complete verification outcome for a verifier."""
    verifier_id: str
    key_id: str
    signature_id: str
    message: str
    bit: int
    total_positions: int
    mismatch_count: int
    mismatch_rate: float
    s_a: float
    s_v: float
    decision: QDSDecision
    decision_reason: str
    binding_valid: bool
    positions: list[PositionVerificationResult]
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self, include_positions: bool = True) -> dict:
        data = {
            "verifier_id": self.verifier_id,
            "key_id": self.key_id,
            "signature_id": self.signature_id,
            "message": self.message,
            "bit": self.bit,
            "total_positions": self.total_positions,
            "mismatch_count": self.mismatch_count,
            "mismatch_rate": round(self.mismatch_rate, 4),
            "s_a": round(self.s_a, 4),
            "s_v": round(self.s_v, 4),
            "decision": self.decision.value,
            "decision_reason": self.decision_reason,
            "binding_valid": self.binding_valid,
            "timestamp": self.timestamp,
        }
        if include_positions:
            data["positions"] = [p.to_dict() for p in self.positions]
        return data


def _projective_measurement_probabilities(
    statevector: np.ndarray,
    basis: BasisType
) -> tuple[float, float]:
    """
    Compute projective measurement probabilities P(0) and P(1) in the specified basis.

    State: |ψ⟩ = [α, β]^T
    Z basis: P(0) = |α|², P(1) = |β|²
    X basis: P(0) = 1/2 |α + β|², P(1) = 1/2 |α - β|²
    Y basis: P(0) = 1/2 |α - iβ|², P(1) = 1/2 |α + iβ|²
    """
    alpha = complex(statevector[0])
    beta = complex(statevector[1])

    basis_upper = basis.upper()
    if basis_upper == "Z":
        p0 = abs(alpha) ** 2
        p1 = abs(beta) ** 2
    elif basis_upper == "X":
        p0 = 0.5 * abs(alpha + beta) ** 2
        p1 = 0.5 * abs(alpha - beta) ** 2
    elif basis_upper == "Y":
        p0 = 0.5 * abs(alpha - 1j * beta) ** 2
        p1 = 0.5 * abs(alpha + 1j * beta) ** 2
    else:
        raise ValueError(f"Unknown measurement basis '{basis}'. Expected 'Z', 'X', or 'Y'.")

    # Normalize in case of tiny numerical imprecision
    total = p0 + p1
    if total > 0:
        p0 = p0 / total
        p1 = p1 / total
    else:
        p0, p1 = 0.5, 0.5

    return float(p0), float(p1)


def verify_signature(
    signature: QDSSignature,
    verifier_id: str,
    memory: VerifierMemory | None = None,
    thresholds: QDSThresholds | None = None,
    seed: int | None = None,
) -> QDSVerificationResult:
    """
    Perform projective measurement verification of a QDS signature against a verifier's memory.

    Args:
        signature: The QDSSignature to verify.
        verifier_id: Identifier of the verifying party (e.g. "Bob").
        memory: Optional VerifierMemory instance (if None, fetched from MEMORY_REGISTRY).
        thresholds: Dual threshold configuration (defaults to s_a=0.10, s_v=0.25).
        seed: Optional RNG seed for reproducible measurement sampling.

    Returns:
        QDSVerificationResult detailing mismatches, decision, and diagnostic analysis.
    """
    if thresholds is None:
        thresholds = QDSThresholds()

    # 1. Cryptographic binding check: verify SHA-256 of message and signature token
    expected_msg_hash = hashlib.sha256(signature.message.encode("utf-8")).hexdigest()
    if signature.message_hash != expected_msg_hash:
        return QDSVerificationResult(
            verifier_id=verifier_id,
            key_id=signature.key_id,
            signature_id=signature.signature_id,
            message=signature.message,
            bit=signature.bit,
            total_positions=0,
            mismatch_count=0,
            mismatch_rate=1.0,
            s_a=thresholds.s_a,
            s_v=thresholds.s_v,
            decision=QDSDecision.REJECT,
            decision_reason="Cryptographic hash mismatch: message payload does not match message_hash.",
            binding_valid=False,
            positions=[],
        )

    expected_binding = hashlib.sha256(
        f"{signature.message_hash}:{signature.bit}:{signature.key_id}:{signature.compact_string}".encode("utf-8")
    ).hexdigest()
    if signature.binding_token != expected_binding:
        return QDSVerificationResult(
            verifier_id=verifier_id,
            key_id=signature.key_id,
            signature_id=signature.signature_id,
            message=signature.message,
            bit=signature.bit,
            total_positions=0,
            mismatch_count=0,
            mismatch_rate=1.0,
            s_a=thresholds.s_a,
            s_v=thresholds.s_v,
            decision=QDSDecision.REJECT,
            decision_reason="Cryptographic binding token invalid: signature sequence does not match bound token.",
            binding_valid=False,
            positions=[],
        )

    # 2. Retrieve verifier memory
    v_mem = memory
    if v_mem is None:
        v_mem = MEMORY_REGISTRY.get_memory(signature.key_id, verifier_id)

    if v_mem is None:
        raise ValueError(
            f"Quantum memory for verifier '{verifier_id}' and key '{signature.key_id}' not found. "
            "Public keys must be distributed to verifier prior to verification."
        )

    stored_states = v_mem.get_states_for_bit(signature.bit)
    if len(stored_states) != len(signature.classical_signature):
        raise ValueError(
            f"Length mismatch: stored quantum states ({len(stored_states)}) != "
            f"signature elements ({len(signature.classical_signature)})."
        )

    rng = np.random.default_rng(seed) if seed is not None else None

    positions_res: list[PositionVerificationResult] = []
    mismatch_count = 0

    # 3. Projective measurement of each stored state in claimed basis
    for i, sig_elem in enumerate(signature.classical_signature):
        claimed_basis: BasisType = sig_elem["basis"]
        claimed_bit: int = sig_elem["bit"]
        stored_state: StoredQuantumState = stored_states[i]

        p0, p1 = _projective_measurement_probabilities(stored_state.statevector, claimed_basis)

        # Deterministic check for exact eigenstates
        if p0 >= 1.0 - 1e-7:
            obs_bit = 0
        elif p1 >= 1.0 - 1e-7:
            obs_bit = 1
        else:
            roll = rng.random() if rng is not None else np.random.random()
            obs_bit = 0 if roll < p0 else 1

        is_mismatch = (obs_bit != claimed_bit)
        if is_mismatch:
            mismatch_count += 1

        positions_res.append(PositionVerificationResult(
            position=i,
            claimed_basis=claimed_basis,
            claimed_bit=claimed_bit,
            observed_bit=obs_bit,
            mismatch=is_mismatch,
            prob_0=p0,
            prob_1=p1,
            original_state_label=stored_state.original_state_label,
        ))

    total = len(positions_res)
    mismatch_rate = mismatch_count / total if total > 0 else 0.0

    # 4. Evaluate decision via dual thresholds
    decision, reason = evaluate_mismatch(mismatch_rate, thresholds)

    return QDSVerificationResult(
        verifier_id=verifier_id,
        key_id=signature.key_id,
        signature_id=signature.signature_id,
        message=signature.message,
        bit=signature.bit,
        total_positions=total,
        mismatch_count=mismatch_count,
        mismatch_rate=mismatch_rate,
        s_a=thresholds.s_a,
        s_v=thresholds.s_v,
        decision=decision,
        decision_reason=reason,
        binding_valid=True,
        positions=positions_res,
    )
