"""
Quantum Public Key Distribution (QPKD) & Quantum Memory.

In QDS, the signer (Alice) distributes copies of her public key states
to each of K >= 2 verifiers (e.g., Bob and Charlie).

Distribution Protocol:
1. For each public key state |ψ⟩ (for both b=0 and b=1):
   - Alice and Verifier share an EPR Bell pair |Φ+⟩ = 1/√2 (|00⟩ + |11⟩).
   - Alice performs a Bell-state measurement on (|ψ⟩, Bell_Alice).
   - Alice transmits the two classical measurement bits (c1, c0) to the Verifier.
   - The Verifier applies the corresponding feed-forward Pauli correction (X^c1 · Z^c0).
   - The reconstructed state is placed into the Verifier's Quantum Memory.
2. Optional Channel Noise:
   - Simulates physical transmission impairments (depolarizing, bit-flip, phase-flip)
     using Kraus / stochastic Pauli error operators.
"""

import math
import secrets
import numpy as np
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Literal

from app.qds.keygen import (
    PauliEigenstate,
    QDSPublicKey,
    BasisType,
    get_pauli_eigenstate,
)

# Pauli matrices
_I = np.eye(2, dtype=complex)
_X = np.array([[0, 1], [1, 0]], dtype=complex)
_Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
_Z = np.array([[1, 0], [0, -1]], dtype=complex)

# Teleportation outcome maps (matching Step 1 teleportation protocol)
_BOB_COLLAPSED_MAP = {
    "00": _I,
    "01": _Z,
    "10": _X,
    "11": _X @ _Z,
}

_CORRECTION_MAP = {
    "00": _I,
    "01": _Z,        # c0=1, c1=0 -> Z
    "10": _X,        # c0=0, c1=1 -> X
    "11": _Z @ _X,   # c0=1, c1=1 -> apply X then Z (matrix Z @ X)
}

BELL_OUTCOMES = ["00", "01", "10", "11"]


@dataclass
class StoredQuantumState:
    """A single quantum state stored in a verifier's quantum memory."""
    position: int
    bit_label: int  # 0 or 1
    original_state_label: str
    original_basis: BasisType
    original_bit: int
    statevector: np.ndarray
    teleportation_outcome: str
    pauli_correction: str
    fidelity_with_original: float
    noise_applied: bool
    noise_details: str = "None (Noiseless)"

    def to_dict(self) -> dict:
        return {
            "position": self.position,
            "bit_label": self.bit_label,
            "original_state_label": self.original_state_label,
            "original_basis": self.original_basis,
            "original_bit": self.original_bit,
            "teleportation_outcome": self.teleportation_outcome,
            "pauli_correction": self.pauli_correction,
            "fidelity_with_original": round(self.fidelity_with_original, 4),
            "noise_applied": self.noise_applied,
            "noise_details": self.noise_details,
            "alpha": {"real": round(self.statevector[0].real, 4), "imag": round(self.statevector[0].imag, 4)},
            "beta": {"real": round(self.statevector[1].real, 4), "imag": round(self.statevector[1].imag, 4)},
        }


@dataclass
class VerifierMemory:
    """Modelled quantum memory for an individual verifier."""
    verifier_id: str
    key_id: str
    memory_0: list[StoredQuantumState] = field(default_factory=list)
    memory_1: list[StoredQuantumState] = field(default_factory=list)
    stored_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def get_states_for_bit(self, b: int) -> list[StoredQuantumState]:
        if b == 0:
            return self.memory_0
        elif b == 1:
            return self.memory_1
        raise ValueError(f"Bit must be 0 or 1, got {b}")

    @property
    def total_stored(self) -> int:
        return len(self.memory_0) + len(self.memory_1)

    @property
    def avg_fidelity(self) -> float:
        all_states = self.memory_0 + self.memory_1
        if not all_states:
            return 1.0
        return float(np.mean([s.fidelity_with_original for s in all_states]))

    def to_dict(self, include_states: bool = False) -> dict:
        data = {
            "verifier_id": self.verifier_id,
            "key_id": self.key_id,
            "total_states": self.total_stored,
            "avg_fidelity": round(self.avg_fidelity, 4),
            "stored_at": self.stored_at,
        }
        if include_states:
            data["states_0"] = [s.to_dict() for s in self.memory_0]
            data["states_1"] = [s.to_dict() for s in self.memory_1]
        return data


class QuantumMemoryRegistry:
    """Central registry tracking quantum memories for all active verifiers."""
    def __init__(self):
        # key: (key_id, verifier_id) -> VerifierMemory
        self._memories: dict[tuple[str, str], VerifierMemory] = {}

    def store_memory(self, memory: VerifierMemory) -> None:
        self._memories[(memory.key_id, memory.verifier_id)] = memory

    def get_memory(self, key_id: str, verifier_id: str) -> VerifierMemory | None:
        return self._memories.get((key_id, verifier_id))

    def list_verifiers_for_key(self, key_id: str) -> list[str]:
        return [vid for (kid, vid) in self._memories.keys() if kid == key_id]

    def clear(self) -> None:
        self._memories.clear()


# Global in-memory registry singleton
MEMORY_REGISTRY = QuantumMemoryRegistry()


def _state_fidelity(sv1: np.ndarray, sv2: np.ndarray) -> float:
    """Compute pure-state fidelity |<sv1|sv2>|^2."""
    inner = np.dot(sv1.conj(), sv2)
    return float(min(1.0, max(0.0, abs(inner) ** 2)))


def teleport_state(
    target_state: PauliEigenstate,
    position: int,
    bit_label: int,
    depolarizing_prob: float = 0.0,
    bit_flip_prob: float = 0.0,
    phase_flip_prob: float = 0.0,
    rng: np.random.Generator | None = None,
) -> StoredQuantumState:
    """
    Simulate Bell pair teleportation of a single public-key state with feed-forward Pauli correction.
    """
    psi_in = target_state.statevector.copy()

    # 1. Simulate Alice's Bell-state measurement (uniform probability 0.25 each)
    if rng is not None:
        outcome = rng.choice(BELL_OUTCOMES)
    else:
        outcome = secrets.choice(BELL_OUTCOMES)

    # 2. Bob's collapsed state before correction
    collapsed = _BOB_COLLAPSED_MAP[outcome] @ psi_in

    # 3. Apply Bob's classical feed-forward Pauli correction
    correction_matrix = _CORRECTION_MAP[outcome]
    reconstructed = correction_matrix @ collapsed

    # Normalize statevector
    norm = np.linalg.norm(reconstructed)
    if norm > 1e-9:
        reconstructed = reconstructed / norm

    # 4. Apply optional channel noise
    noise_applied = False
    noise_details = []

    # Stochastic bit flip (Pauli X)
    if bit_flip_prob > 0.0:
        roll = rng.random() if rng is not None else secrets.randbelow(10000) / 10000.0
        if roll < bit_flip_prob:
            reconstructed = _X @ reconstructed
            noise_applied = True
            noise_details.append(f"Bit-Flip (X, p={bit_flip_prob})")

    # Stochastic phase flip (Pauli Z)
    if phase_flip_prob > 0.0:
        roll = rng.random() if rng is not None else secrets.randbelow(10000) / 10000.0
        if roll < phase_flip_prob:
            reconstructed = _Z @ reconstructed
            noise_applied = True
            noise_details.append(f"Phase-Flip (Z, p={phase_flip_prob})")

    # Stochastic depolarizing error (replaces with X, Y, or Z error with p/3 each)
    if depolarizing_prob > 0.0:
        roll = rng.random() if rng is not None else secrets.randbelow(10000) / 10000.0
        if roll < depolarizing_prob:
            sub_roll = rng.random() if rng is not None else secrets.randbelow(3) / 3.0
            if sub_roll < 1.0 / 3.0:
                reconstructed = _X @ reconstructed
                noise_details.append("Depolarizing (X)")
            elif sub_roll < 2.0 / 3.0:
                reconstructed = _Y @ reconstructed
                noise_details.append("Depolarizing (Y)")
            else:
                reconstructed = _Z @ reconstructed
                noise_details.append("Depolarizing (Z)")
            noise_applied = True

    norm = np.linalg.norm(reconstructed)
    if norm > 1e-9:
        reconstructed = reconstructed / norm

    fidelity = _state_fidelity(psi_in, reconstructed)

    pauli_labels = {
        "00": "Identity (I)",
        "01": "Pauli-Z",
        "10": "Pauli-X",
        "11": "Pauli-X then Z (Z @ X)",
    }

    return StoredQuantumState(
        position=position,
        bit_label=bit_label,
        original_state_label=target_state.label,
        original_basis=target_state.basis,
        original_bit=target_state.bit,
        statevector=reconstructed,
        teleportation_outcome=outcome,
        pauli_correction=pauli_labels.get(outcome, "Identity"),
        fidelity_with_original=fidelity,
        noise_applied=noise_applied,
        noise_details=", ".join(noise_details) if noise_details else "None (Noiseless)",
    )


def distribute_public_keys(
    public_key: QDSPublicKey,
    verifiers: list[str] | None = None,
    depolarizing_prob: float = 0.0,
    bit_flip_prob: float = 0.0,
    phase_flip_prob: float = 0.0,
    seed: int | None = None,
    registry: QuantumMemoryRegistry | None = None,
) -> dict[str, VerifierMemory]:
    """
    Distribute public key states to K >= 2 verifiers via simulated Bell pairs & teleportation.

    Args:
        public_key: The signer's public key (L states for b=0 and L states for b=1).
        verifiers: List of verifier identifiers (defaults to ["Bob", "Charlie"]).
        depolarizing_prob: Optional channel depolarizing probability.
        bit_flip_prob: Optional channel bit-flip probability.
        phase_flip_prob: Optional channel phase-flip probability.
        seed: Optional RNG seed for deterministic testing.
        registry: Target memory registry (defaults to global singleton).

    Returns:
        Dictionary mapping verifier_id -> VerifierMemory.
    """
    if verifiers is None or len(verifiers) < 2:
        verifiers = ["Bob", "Charlie"]

    reg = registry if registry is not None else MEMORY_REGISTRY
    rng = np.random.default_rng(seed) if seed is not None else None

    result_memories: dict[str, VerifierMemory] = {}

    for verifier in verifiers:
        v_mem = VerifierMemory(verifier_id=verifier, key_id=public_key.key_id)

        # Teleport states for b=0
        for pos, state in enumerate(public_key.pk_0):
            stored = teleport_state(
                target_state=state,
                position=pos,
                bit_label=0,
                depolarizing_prob=depolarizing_prob,
                bit_flip_prob=bit_flip_prob,
                phase_flip_prob=phase_flip_prob,
                rng=rng,
            )
            v_mem.memory_0.append(stored)

        # Teleport states for b=1
        for pos, state in enumerate(public_key.pk_1):
            stored = teleport_state(
                target_state=state,
                position=pos,
                bit_label=1,
                depolarizing_prob=depolarizing_prob,
                bit_flip_prob=bit_flip_prob,
                phase_flip_prob=phase_flip_prob,
                rng=rng,
            )
            v_mem.memory_1.append(stored)

        reg.store_memory(v_mem)
        result_memories[verifier] = v_mem

    return result_memories
