"""
QDS Key Generation based on the Six Pauli Eigenstates.

Alphabet:
    Z basis:
      - |0⟩ : bit 0, θ=0,   φ=0,     statevector: [1, 0]^T
      - |1⟩ : bit 1, θ=π,   φ=0,     statevector: [0, 1]^T
    X basis:
      - |+⟩ : bit 0, θ=π/2, φ=0,     statevector: 1/√2 [1, 1]^T
      - |-⟩ : bit 1, θ=π/2, φ=π,     statevector: 1/√2 [1, -1]^T
    Y basis:
      - |+i⟩: bit 0, θ=π/2, φ=π/2,   statevector: 1/√2 [1, i]^T
      - |-i⟩: bit 1, θ=π/2, φ=3π/2,  statevector: 1/√2 [1, -i]^T

Keygen Protocol:
    For each message bit b ∈ {0, 1}:
      The signer draws L random Pauli-eigenstates from the 6-state alphabet.
      - Private key for b: sk_b = [(basis_i, bit_i)] for i = 0...L-1
      - Public key for b:  pk_b = [|ψ(basis_i, bit_i)⟩] for i = 0...L-1
"""

import math
import uuid
import secrets
import numpy as np
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Literal

BasisType = Literal["Z", "X", "Y"]

SQRT2_INV = 1.0 / math.sqrt(2.0)

# Exact definitions for the six Pauli eigenstates
PAULI_ALPHABET: dict[tuple[BasisType, int], dict] = {
    ("Z", 0): {
        "basis": "Z",
        "bit": 0,
        "label": "|0⟩",
        "theta": 0.0,
        "phi": 0.0,
        "statevector": np.array([1.0 + 0.0j, 0.0 + 0.0j], dtype=complex),
        "bloch": (0.0, 0.0, 1.0),
    },
    ("Z", 1): {
        "basis": "Z",
        "bit": 1,
        "label": "|1⟩",
        "theta": math.pi,
        "phi": 0.0,
        "statevector": np.array([0.0 + 0.0j, 1.0 + 0.0j], dtype=complex),
        "bloch": (0.0, 0.0, -1.0),
    },
    ("X", 0): {
        "basis": "X",
        "bit": 0,
        "label": "|+⟩",
        "theta": math.pi / 2.0,
        "phi": 0.0,
        "statevector": np.array([SQRT2_INV + 0.0j, SQRT2_INV + 0.0j], dtype=complex),
        "bloch": (1.0, 0.0, 0.0),
    },
    ("X", 1): {
        "basis": "X",
        "bit": 1,
        "label": "|-⟩",
        "theta": math.pi / 2.0,
        "phi": math.pi,
        "statevector": np.array([SQRT2_INV + 0.0j, -SQRT2_INV + 0.0j], dtype=complex),
        "bloch": (-1.0, 0.0, 0.0),
    },
    ("Y", 0): {
        "basis": "Y",
        "bit": 0,
        "label": "|+i⟩",
        "theta": math.pi / 2.0,
        "phi": math.pi / 2.0,
        "statevector": np.array([SQRT2_INV + 0.0j, 1j * SQRT2_INV], dtype=complex),
        "bloch": (0.0, 1.0, 0.0),
    },
    ("Y", 1): {
        "basis": "Y",
        "bit": 1,
        "label": "|-i⟩",
        "theta": math.pi / 2.0,
        "phi": 3.0 * math.pi / 2.0,
        "statevector": np.array([SQRT2_INV + 0.0j, -1j * SQRT2_INV], dtype=complex),
        "bloch": (0.0, -1.0, 0.0),
    },
}

ALPHABET_KEYS = list(PAULI_ALPHABET.keys())


@dataclass
class PauliEigenstate:
    """A single quantum state from the 6-state Pauli alphabet."""
    basis: BasisType
    bit: int
    label: str
    theta: float
    phi: float
    statevector: np.ndarray
    bloch: tuple[float, float, float]

    def to_dict(self) -> dict:
        return {
            "basis": self.basis,
            "bit": self.bit,
            "label": self.label,
            "theta": round(self.theta, 4),
            "phi": round(self.phi, 4),
            "bloch": [round(c, 4) for c in self.bloch],
            "alpha": {"real": round(self.statevector[0].real, 4), "imag": round(self.statevector[0].imag, 4)},
            "beta": {"real": round(self.statevector[1].real, 4), "imag": round(self.statevector[1].imag, 4)},
        }


def get_pauli_eigenstate(basis: BasisType, bit: int) -> PauliEigenstate:
    """Retrieve canonical Pauli eigenstate for given basis and bit."""
    b_upper = basis.upper()
    if (b_upper, bit) not in PAULI_ALPHABET:
        raise ValueError(f"Invalid basis '{basis}' or bit '{bit}'. Expected basis in ('Z','X','Y'), bit in (0,1).")
    data = PAULI_ALPHABET[(b_upper, bit)]
    return PauliEigenstate(
        basis=data["basis"],
        bit=data["bit"],
        label=data["label"],
        theta=data["theta"],
        phi=data["phi"],
        statevector=data["statevector"].copy(),
        bloch=data["bloch"],
    )


@dataclass
class KeyElement:
    """Classical private key element (basis + bit) at a specific position."""
    position: int
    basis: BasisType
    bit: int
    state_label: str

    def to_dict(self) -> dict:
        return {
            "position": self.position,
            "basis": self.basis,
            "bit": self.bit,
            "state_label": self.state_label,
        }


@dataclass
class QDSPrivateKey:
    """Signer's private key for bits b=0 and b=1."""
    key_id: str
    length: int
    sk_0: list[KeyElement]
    sk_1: list[KeyElement]
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def get_sk_for_bit(self, b: int) -> list[KeyElement]:
        if b == 0:
            return self.sk_0
        elif b == 1:
            return self.sk_1
        raise ValueError(f"Bit must be 0 or 1, got {b}")

    def to_dict(self) -> dict:
        return {
            "key_id": self.key_id,
            "length": self.length,
            "created_at": self.created_at,
            "sk_0": [e.to_dict() for e in self.sk_0],
            "sk_1": [e.to_dict() for e in self.sk_1],
        }


@dataclass
class QDSPublicKey:
    """Public key consisting of L Pauli eigenstates for b=0 and b=1."""
    key_id: str
    length: int
    pk_0: list[PauliEigenstate]
    pk_1: list[PauliEigenstate]
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def get_pk_for_bit(self, b: int) -> list[PauliEigenstate]:
        if b == 0:
            return self.pk_0
        elif b == 1:
            return self.pk_1
        raise ValueError(f"Bit must be 0 or 1, got {b}")

    def to_dict(self) -> dict:
        return {
            "key_id": self.key_id,
            "length": self.length,
            "created_at": self.created_at,
            "pk_0": [s.to_dict() for s in self.pk_0],
            "pk_1": [s.to_dict() for s in self.pk_1],
        }


def generate_qds_keypair(
    length: int = 32,
    seed: int | None = None
) -> tuple[QDSPrivateKey, QDSPublicKey]:
    """
    Generate a QDS key pair of length L for message bits b ∈ {0, 1}.

    Args:
        length: Number of Pauli-eigenstates per bit (L >= 4).
        seed: Optional integer seed for reproducible testing.

    Returns:
        (private_key, public_key)
    """
    if length < 4:
        raise ValueError(f"Key length L must be at least 4, got {length}")

    rng = np.random.default_rng(seed) if seed is not None else None
    key_id = f"QDS-KEY-{uuid.uuid4().hex[:8].upper()}"

    def draw_sequence() -> tuple[list[KeyElement], list[PauliEigenstate]]:
        sk_seq = []
        pk_seq = []
        for i in range(length):
            if rng is not None:
                idx = int(rng.integers(0, len(ALPHABET_KEYS)))
            else:
                idx = secrets.randbelow(len(ALPHABET_KEYS))
            basis, bit = ALPHABET_KEYS[idx]
            state = get_pauli_eigenstate(basis, bit)
            sk_seq.append(KeyElement(position=i, basis=basis, bit=bit, state_label=state.label))
            pk_seq.append(state)
        return sk_seq, pk_seq

    sk_0, pk_0 = draw_sequence()
    sk_1, pk_1 = draw_sequence()

    priv = QDSPrivateKey(key_id=key_id, length=length, sk_0=sk_0, sk_1=sk_1)
    pub = QDSPublicKey(key_id=key_id, length=length, pk_0=pk_0, pk_1=pk_1)
    return priv, pub
