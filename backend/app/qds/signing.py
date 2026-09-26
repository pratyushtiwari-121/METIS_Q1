"""
QDS Signing Protocol.

Signing Mechanism:
1. To sign a message bit b ∈ {0, 1} associated with message M:
   - The signer computes the cryptographic digest H = SHA-256(M).
   - The signature for bit b is the signer's classical private key sequence for b:
     Sig(b) = sk_b = [(basis_0, bit_0), (basis_1, bit_1), ..., (basis_{L-1}, bit_{L-1})]
2. SHA-256 Message Binding:
   - To cryptographically bind the message M and bit b to the classical sequence sk_b,
     a SHA-256 signature binding token is generated:
     T = SHA-256(H || b || key_id || Sig(b))
   - This ensures the signature cannot be detached from M or transposed to another bit.
"""

import uuid
import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.qds.keygen import QDSPrivateKey, KeyElement


@dataclass
class QDSSignature:
    """A signed QDS message package."""
    signature_id: str
    key_id: str
    message: str
    message_hash: str
    bit: int
    classical_signature: list[dict]
    compact_string: str
    binding_token: str
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return {
            "signature_id": self.signature_id,
            "key_id": self.key_id,
            "message": self.message,
            "message_hash": self.message_hash,
            "bit": self.bit,
            "compact_string": self.compact_string,
            "binding_token": self.binding_token,
            "classical_signature": self.classical_signature,
            "created_at": self.created_at,
        }


def sign_message(
    message: str,
    private_key: QDSPrivateKey,
    bit: int = 0,
) -> QDSSignature:
    """
    Generate a QDS signature for bit b bound to message M via SHA-256.

    Args:
        message: The plaintext message string.
        private_key: The signer's private key.
        bit: The message bit to sign (0 or 1).

    Returns:
        QDSSignature object containing classical private key string and SHA-256 binding.
    """
    if bit not in (0, 1):
        raise ValueError(f"Message bit must be 0 or 1, got {bit}")

    clean_msg = message.strip()
    if not clean_msg:
        raise ValueError("Message cannot be empty.")

    # 1. SHA-256 of the message payload
    msg_hash = hashlib.sha256(clean_msg.encode("utf-8")).hexdigest()

    # 2. Extract classical private key sequence for bit b
    sk_elements = private_key.get_sk_for_bit(bit)
    classical_sig = [e.to_dict() for e in sk_elements]

    # Compact representation: e.g. "Z0,X1,Y0,Z1,..."
    compact_str = ",".join(f"{e.basis}{e.bit}" for e in sk_elements)

    # 3. SHA-256 binding token: binds message_hash, bit, key_id, and signature sequence
    binding_payload = f"{msg_hash}:{bit}:{private_key.key_id}:{compact_str}"
    binding_token = hashlib.sha256(binding_payload.encode("utf-8")).hexdigest()

    sig_id = f"QDSSIG-{uuid.uuid4().hex[:8].upper()}"

    return QDSSignature(
        signature_id=sig_id,
        key_id=private_key.key_id,
        message=clean_msg,
        message_hash=msg_hash,
        bit=bit,
        classical_signature=classical_sig,
        compact_string=compact_str,
        binding_token=binding_token,
    )
