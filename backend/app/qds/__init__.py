"""
Quantum Digital Signature (QDS) Module.

Provides physics-based quantum digital signature generation, distribution,
signing, verification, and threshold decision logic based on the six Pauli
eigenstates (|0⟩, |1⟩, |+⟩, |-⟩, |+i⟩, |-i⟩).
"""

from app.qds.thresholds import (
    QDSThresholds,
    QDSDecision,
    evaluate_mismatch,
)
from app.qds.keygen import (
    BasisType,
    PauliEigenstate,
    KeyElement,
    QDSPrivateKey,
    QDSPublicKey,
    generate_qds_keypair,
    get_pauli_eigenstate,
    PAULI_ALPHABET,
)
from app.qds.distribution import (
    StoredQuantumState,
    VerifierMemory,
    QuantumMemoryRegistry,
    MEMORY_REGISTRY,
    teleport_state,
    distribute_public_keys,
)
from app.qds.signing import (
    QDSSignature,
    sign_message,
)
from app.qds.verification import (
    PositionVerificationResult,
    QDSVerificationResult,
    verify_signature,
)
from app.qds.adversary import (
    QDSAttackResult,
    simulate_random_guess_forgery,
    simulate_measure_and_guess_forgery,
    simulate_impersonation,
    simulate_channel_manipulation,
    validate_and_consume_nonce,
    simulate_replay_attack,
    check_authorization_and_rate_limit,
    simulate_unauthorized_attack,
    simulate_rate_limit_attack,
    CITED_MUB_BOUND_NOTE,
)

__all__ = [
    "QDSThresholds",
    "QDSDecision",
    "evaluate_mismatch",
    "BasisType",
    "PauliEigenstate",
    "KeyElement",
    "QDSPrivateKey",
    "QDSPublicKey",
    "generate_qds_keypair",
    "get_pauli_eigenstate",
    "PAULI_ALPHABET",
    "StoredQuantumState",
    "VerifierMemory",
    "QuantumMemoryRegistry",
    "MEMORY_REGISTRY",
    "teleport_state",
    "distribute_public_keys",
    "QDSSignature",
    "sign_message",
    "PositionVerificationResult",
    "QDSVerificationResult",
    "verify_signature",
    "QDSAttackResult",
    "simulate_random_guess_forgery",
    "simulate_measure_and_guess_forgery",
    "simulate_impersonation",
    "simulate_channel_manipulation",
    "validate_and_consume_nonce",
    "simulate_replay_attack",
    "check_authorization_and_rate_limit",
    "simulate_unauthorized_attack",
    "simulate_rate_limit_attack",
    "CITED_MUB_BOUND_NOTE",
]

