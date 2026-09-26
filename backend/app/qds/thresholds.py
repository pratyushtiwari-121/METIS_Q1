"""
QDS Verification Thresholds & Decision Logic.

In Quantum Digital Signatures (QDS), verification utilizes dual thresholds:
    0 <= s_a < s_v < 0.5

Where:
    - s_a is the ACCEPTANCE threshold.
      If mismatch rate m <= s_a, the verifier accepts the signature as authentic.
      For honest noiseless transmissions, m = 0, ensuring 100% acceptance.
    - s_v is the VERIFICATION / REJECTION threshold.
      If mismatch rate m > s_v, the signature is definitively rejected as a forgery
      or tampered transmission.
    - The interval (s_a, s_v] is the MIDDLE ZONE (Arbitration / Inconclusive Zone).

Physical & Cryptographic Rationale of the Middle Zone:
------------------------------------------------------
The security of QDS against repudiation (Alice trying to sign a message such that
Bob accepts but Charlie rejects when Bob forwards it) relies on the gap (s_v - s_a).
By the Wootters-Zurek No-Cloning theorem and quantum measurement uncertainty, Alice
cannot prepare quantum states that yield a low mismatch rate (<= s_a) at Bob while
inducing a high mismatch rate (> s_v) when forwarded or cross-verified with Charlie.

When m falls in the middle zone (s_a < m <= s_v), the verification is inconclusive.
In standard QDS protocols (Gottesman-Chuang, Arrazola et al., Clarke et al.),
this triggers an arbitration/dispute resolution protocol where Bob and Charlie
compare symmetrized quantum or classical records to detect adversarial forging
or channel degradation before accepting or aborting.
"""

from dataclasses import dataclass
from enum import Enum


class QDSDecision(str, Enum):
    ACCEPT = "ACCEPT"
    REJECT = "REJECT"
    INCONCLUSIVE_ARBITRATION = "INCONCLUSIVE_ARBITRATION"


@dataclass(frozen=True)
class QDSThresholds:
    """Configurable dual thresholds for QDS verification."""
    s_a: float = 0.10  # Acceptance threshold
    s_v: float = 0.25  # Rejection threshold

    def __post_init__(self):
        if not (0.0 <= self.s_a < self.s_v < 0.5):
            raise ValueError(
                f"Invalid QDS thresholds: required 0.0 <= s_a < s_v < 0.5, "
                f"got s_a={self.s_a}, s_v={self.s_v}"
            )

    @property
    def middle_zone_width(self) -> float:
        """Width of the dispute resolution window."""
        return self.s_v - self.s_a


def evaluate_mismatch(
    mismatch_rate: float,
    thresholds: QDSThresholds | None = None
) -> tuple[QDSDecision, str]:
    """
    Evaluate the mismatch rate m against dual thresholds s_a and s_v.

    Returns:
        (decision, explanation_str)
    """
    if thresholds is None:
        thresholds = QDSThresholds()

    m = max(0.0, min(1.0, float(mismatch_rate)))

    if m <= thresholds.s_a:
        return (
            QDSDecision.ACCEPT,
            f"Accepted: mismatch rate m={m:.4f} <= s_a={thresholds.s_a:.4f}. "
            "Quantum state measurements match claimed private key with high statistical confidence."
        )
    elif m > thresholds.s_v:
        return (
            QDSDecision.REJECT,
            f"Rejected: mismatch rate m={m:.4f} > s_v={thresholds.s_v:.4f}. "
            "Excessive mismatch detected, indicating unauthorized tampering or forgery."
        )
    else:
        return (
            QDSDecision.INCONCLUSIVE_ARBITRATION,
            f"Middle Zone (Arbitration): s_a ({thresholds.s_a:.4f}) < m ({m:.4f}) <= s_v ({thresholds.s_v:.4f}). "
            "Dispute resolution protocol triggered. Verifiers must cross-check public key records "
            "to prevent signer repudiation."
        )
