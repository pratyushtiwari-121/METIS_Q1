"""
Comprehensive Test Suite for Quantum Digital Signatures (QDS Step 2).

Tests cover:
  1. ALPHABET & KEYGEN:
     - The six Pauli eigenstates (|0>, |1>, |+>, |->, |+i>, |-i>)
     - Deterministic and random keypair generation for b in {0, 1}
  2. HONEST NOISELESS TRANSMISSION:
     - 100% acceptance with mismatch rate m = 0.0
  3. TWO-VERIFIER FLOW (Bob & Charlie):
     - Multi-party QPKD distribution via Bell pair teleportation
     - Both verifiers independently accept honest signatures
  4. NOISY TRANSMISSION ROBUSTNESS:
     - Honest signature mismatch under realistic noise stays below s_a
  5. ADVERSARIAL FORGERY & TAMPERING:
     - Forged keys yield mismatch m ~ 0.50 > s_v -> rejected
     - Message tampering detected by SHA-256 binding
  6. THRESHOLDS & MIDDLE ZONE:
     - Decision boundary tests (m <= s_a, s_a < m <= s_v, m > s_v)
     - Config validation (0 <= s_a < s_v < 0.5)
  7. REST API ENDPOINTS:
     - End-to-end HTTP API lifecycle: keygen -> distribute -> sign -> verify
  8. LEGACY ENDPOINTS COMPATIBILITY:
     - Legacy hash-to-state endpoints (/api/signatures/generate, /api/verification/verify)
       remain completely operational.
"""

import math
import pytest
import numpy as np
from fastapi.testclient import TestClient

from app.main import app
from app.qds import (
    QDSThresholds,
    QDSDecision,
    evaluate_mismatch,
    generate_qds_keypair,
    get_pauli_eigenstate,
    PAULI_ALPHABET,
    distribute_public_keys,
    sign_message,
    verify_signature,
    teleport_state,
    QuantumMemoryRegistry,
    QDSSignature,
)


@pytest.fixture
def client():
    return TestClient(app)


# ===========================================================================
# 1. ALPHABET & KEYGEN TESTS
# ===========================================================================

class TestQDSAlphabetAndKeygen:
    """Test Pauli alphabet definitions and keypair generation."""

    def test_pauli_eigenstates_normalization(self):
        """All six Pauli eigenstates must be normalized pure states."""
        for (basis, bit), data in PAULI_ALPHABET.items():
            sv = data["statevector"]
            norm = np.linalg.norm(sv)
            assert pytest.approx(norm, rel=1e-6) == 1.0

    def test_pauli_eigenstates_eigenvalues(self):
        """Verify each state is indeed an eigenstate of its respective Pauli operator."""
        _Z = np.array([[1, 0], [0, -1]], dtype=complex)
        _X = np.array([[0, 1], [1, 0]], dtype=complex)
        _Y = np.array([[0, -1j], [1j, 0]], dtype=complex)

        ops = {"Z": _Z, "X": _X, "Y": _Y}

        for (basis, bit), data in PAULI_ALPHABET.items():
            sv = data["statevector"]
            expected_eigenval = 1.0 if bit == 0 else -1.0
            actual = ops[basis] @ sv
            expected = expected_eigenval * sv
            np.testing.assert_allclose(actual, expected, atol=1e-6)

    def test_keygen_lengths_and_structure(self):
        """Keygen draws L Pauli-eigenstates per bit b in {0, 1}."""
        L = 24
        priv, pub = generate_qds_keypair(length=L, seed=42)

        assert priv.length == L
        assert pub.length == L
        assert len(priv.sk_0) == L
        assert len(priv.sk_1) == L
        assert len(pub.pk_0) == L
        assert len(pub.pk_1) == L

        for elem in priv.sk_0:
            assert elem.basis in ("Z", "X", "Y")
            assert elem.bit in (0, 1)

    def test_keygen_minimum_length(self):
        """Keygen rejects L < 4."""
        with pytest.raises(ValueError, match="at least 4"):
            generate_qds_keypair(length=2)


# ===========================================================================
# 2. HONEST NOISELESS ACCEPTANCE TESTS
# ===========================================================================

class TestNoiselessHonestQDS:
    """Test that honest noiseless signatures achieve m = 0 and 100% acceptance."""

    @pytest.mark.parametrize("bit", [0, 1])
    def test_honest_noiseless_acceptance(self, bit):
        """Honest signature over noiseless channel yields mismatch = 0 and ACCEPT."""
        priv, pub = generate_qds_keypair(length=32, seed=123 + bit)

        # Distribute noiselessly
        reg = QuantumMemoryRegistry()
        memories = distribute_public_keys(
            public_key=pub,
            verifiers=["Bob", "Charlie"],
            depolarizing_prob=0.0,
            registry=reg,
            seed=10,
        )

        sig = sign_message(
            message=f"Authentic quantum message for bit {bit}",
            private_key=priv,
            bit=bit,
        )

        res_bob = verify_signature(
            signature=sig,
            verifier_id="Bob",
            memory=memories["Bob"],
            thresholds=QDSThresholds(s_a=0.10, s_v=0.25),
        )

        assert res_bob.mismatch_count == 0
        assert res_bob.mismatch_rate == 0.0
        assert res_bob.decision == QDSDecision.ACCEPT
        assert res_bob.binding_valid is True

    def test_honest_noiseless_across_multiple_runs(self):
        """Verify 100% acceptance over multiple distinct random keys."""
        for seed in range(10):
            priv, pub = generate_qds_keypair(length=16, seed=seed)
            reg = QuantumMemoryRegistry()
            memories = distribute_public_keys(
                public_key=pub,
                verifiers=["Bob", "Charlie"],
                registry=reg,
                seed=seed,
            )

            sig = sign_message(message="Transaction approval", private_key=priv, bit=0)
            res = verify_signature(signature=sig, verifier_id="Bob", memory=memories["Bob"])
            assert res.mismatch_rate == 0.0
            assert res.decision == QDSDecision.ACCEPT


# ===========================================================================
# 3. TWO-VERIFIER FLOW TESTS
# ===========================================================================

class TestTwoVerifierQDSFlow:
    """Test QPKD distribution to Bob and Charlie and dual verification."""

    def test_two_verifier_independent_verification(self):
        """Both Bob and Charlie receive states and both accept the signature."""
        priv, pub = generate_qds_keypair(length=32, seed=777)
        reg = QuantumMemoryRegistry()
        memories = distribute_public_keys(
            public_key=pub,
            verifiers=["Bob", "Charlie"],
            registry=reg,
            seed=777,
        )

        sig = sign_message(message="Transfer $10,000", private_key=priv, bit=1)

        # Bob verifies
        res_bob = verify_signature(sig, verifier_id="Bob", memory=memories["Bob"])
        assert res_bob.mismatch_rate == 0.0
        assert res_bob.decision == QDSDecision.ACCEPT

        # Charlie verifies
        res_charlie = verify_signature(sig, verifier_id="Charlie", memory=memories["Charlie"])
        assert res_charlie.mismatch_rate == 0.0
        assert res_charlie.decision == QDSDecision.ACCEPT

    def test_three_verifier_distribution(self):
        """Test with K = 3 verifiers (Bob, Charlie, David)."""
        priv, pub = generate_qds_keypair(length=16, seed=99)
        reg = QuantumMemoryRegistry()
        verifiers = ["Bob", "Charlie", "David"]
        memories = distribute_public_keys(pub, verifiers=verifiers, registry=reg)

        assert len(memories) == 3
        for v in verifiers:
            assert memories[v].total_stored == 32  # 16 for b=0, 16 for b=1


# ===========================================================================
# 4. NOISY CHANNEL ROBUSTNESS TESTS
# ===========================================================================

class TestNoisyChannelRobustness:
    """Test that realistic channel noise produces small mismatch below s_a."""

    def test_noisy_honest_signature_stays_below_s_a(self):
        """With modest depolarizing noise (p=0.02), mismatch rate stays below s_a=0.10."""
        priv, pub = generate_qds_keypair(length=64, seed=42)
        reg = QuantumMemoryRegistry()
        memories = distribute_public_keys(
            public_key=pub,
            verifiers=["Bob", "Charlie"],
            depolarizing_prob=0.02,
            registry=reg,
            seed=42,
        )

        sig = sign_message(message="Sensor Telemetry Payload", private_key=priv, bit=0)
        res = verify_signature(
            signature=sig,
            verifier_id="Bob",
            memory=memories["Bob"],
            thresholds=QDSThresholds(s_a=0.10, s_v=0.25),
            seed=42,
        )

        assert res.mismatch_rate <= 0.10
        assert res.decision == QDSDecision.ACCEPT


# ===========================================================================
# 5. ADVERSARIAL FORGERY & TAMPERING TESTS
# ===========================================================================

class TestAdversarialDetection:
    """Test rejection of forged signatures and tampered messages."""

    def test_wrong_bit_signature_rejected(self):
        """Signing with the wrong bit's key produces high mismatch rate (~0.50 > s_v)."""
        priv, pub = generate_qds_keypair(length=64, seed=123)
        reg = QuantumMemoryRegistry()
        memories = distribute_public_keys(pub, verifiers=["Bob", "Charlie"], registry=reg, seed=123)

        # Attacker claims bit 0, but supplies private key for bit 1
        sig_wrong = sign_message("Legitimate message", private_key=priv, bit=1)
        # Attacker manipulates bit field to 0
        sig_forged = QDSSignature(
            signature_id=sig_wrong.signature_id,
            key_id=sig_wrong.key_id,
            message=sig_wrong.message,
            message_hash=sig_wrong.message_hash,
            bit=0,  # claim bit 0 with bit 1 keys
            classical_signature=sig_wrong.classical_signature,
            compact_string=sig_wrong.compact_string,
            binding_token=sig_wrong.binding_token,
        )

        res = verify_signature(sig_forged, verifier_id="Bob", memory=memories["Bob"], seed=10)
        assert res.decision == QDSDecision.REJECT

    def test_tampered_message_digest_rejected(self):
        """Altering the message payload invalidates the SHA-256 binding token."""
        priv, pub = generate_qds_keypair(length=32, seed=456)
        reg = QuantumMemoryRegistry()
        memories = distribute_public_keys(pub, verifiers=["Bob", "Charlie"], registry=reg, seed=456)

        sig = sign_message("Original Payment: $100", private_key=priv, bit=0)

        # Tampered message
        tampered_sig = QDSSignature(
            signature_id=sig.signature_id,
            key_id=sig.key_id,
            message="Tampered Payment: $100,000",
            message_hash=sig.message_hash,  # stale hash
            bit=sig.bit,
            classical_signature=sig.classical_signature,
            compact_string=sig.compact_string,
            binding_token=sig.binding_token,
        )

        res = verify_signature(tampered_sig, verifier_id="Bob", memory=memories["Bob"])
        assert res.binding_valid is False
        assert res.decision == QDSDecision.REJECT


# ===========================================================================
# 6. THRESHOLDS & MIDDLE ZONE TESTS
# ===========================================================================

class TestQDSThresholdsAndDecisions:
    """Test dual threshold configuration and middle-zone decision logic."""

    def test_threshold_validation(self):
        """Enforces 0.0 <= s_a < s_v < 0.5."""
        # Valid
        th = QDSThresholds(s_a=0.05, s_v=0.20)
        assert th.s_a == 0.05
        assert th.s_v == 0.20
        assert th.middle_zone_width == pytest.approx(0.15)

        # Invalid: s_a >= s_v
        with pytest.raises(ValueError, match="0.0 <= s_a < s_v < 0.5"):
            QDSThresholds(s_a=0.30, s_v=0.20)

        # Invalid: s_v >= 0.5
        with pytest.raises(ValueError, match="0.0 <= s_a < s_v < 0.5"):
            QDSThresholds(s_a=0.10, s_v=0.55)

        # Invalid: negative s_a
        with pytest.raises(ValueError, match="0.0 <= s_a < s_v < 0.5"):
            QDSThresholds(s_a=-0.05, s_v=0.25)

    def test_evaluate_mismatch_zones(self):
        """Test accept, middle zone (arbitration), and reject zones."""
        th = QDSThresholds(s_a=0.10, s_v=0.25)

        # Accept zone (m <= s_a)
        dec, _ = evaluate_mismatch(0.0, th)
        assert dec == QDSDecision.ACCEPT

        dec, _ = evaluate_mismatch(0.10, th)
        assert dec == QDSDecision.ACCEPT

        # Middle zone (s_a < m <= s_v)
        dec, reason = evaluate_mismatch(0.15, th)
        assert dec == QDSDecision.INCONCLUSIVE_ARBITRATION
        assert "Arbitration" in reason

        dec, reason = evaluate_mismatch(0.25, th)
        assert dec == QDSDecision.INCONCLUSIVE_ARBITRATION

        # Reject zone (m > s_v)
        dec, _ = evaluate_mismatch(0.26, th)
        assert dec == QDSDecision.REJECT

        dec, _ = evaluate_mismatch(0.50, th)
        assert dec == QDSDecision.REJECT


# ===========================================================================
# 7. REST API ENDPOINT TESTS
# ===========================================================================

class TestQDSRestEndpoints:
    """Test FastAPI endpoints for the QDS protocol."""

    def test_full_qds_api_flow(self, client):
        """Complete REST flow: keygen -> distribute -> sign -> verify."""
        # 1. Keygen
        kg_res = client.post("/api/qds/keygen", json={"length": 16, "seed": 42})
        assert kg_res.status_code == 200
        kg_data = kg_res.json()
        key_id = kg_data["key_id"]
        assert kg_data["length"] == 16
        assert len(kg_data["private_key_preview"]) > 0

        # 2. Distribute to Bob and Charlie
        dist_res = client.post("/api/qds/distribute", json={
            "key_id": key_id,
            "verifiers": ["Bob", "Charlie"],
            "depolarizing_prob": 0.0,
            "seed": 42
        })
        assert dist_res.status_code == 200
        dist_data = dist_res.json()
        assert dist_data["total_states_teleported"] == 64  # 16 states * 2 bits * 2 verifiers
        assert "Bob" in dist_data["verifiers_status"]
        assert "Charlie" in dist_data["verifiers_status"]

        # 3. Sign message
        sign_res = client.post("/api/qds/sign", json={
            "key_id": key_id,
            "message": "Approved Quantum Transfer",
            "bit": 0
        })
        assert sign_res.status_code == 200
        sign_data = sign_res.json()
        sig_id = sign_data["signature_id"]
        assert sign_data["bit"] == 0
        assert len(sign_data["classical_signature"]) == 16

        # 4. Verify at Bob
        ver_res = client.post("/api/qds/verify", json={
            "key_id": key_id,
            "signature_id": sig_id,
            "message": "Approved Quantum Transfer",
            "bit": 0,
            "verifier_id": "Bob",
            "s_a": 0.10,
            "s_v": 0.25
        })
        assert ver_res.status_code == 200
        ver_data = ver_res.json()
        assert ver_data["decision"] == "ACCEPT"
        assert ver_data["mismatch_rate"] == 0.0
        assert ver_data["binding_valid"] is True

        # 5. Verify at Charlie
        ver_charlie = client.post("/api/qds/verify", json={
            "key_id": key_id,
            "signature_id": sig_id,
            "message": "Approved Quantum Transfer",
            "bit": 0,
            "verifier_id": "Charlie",
            "s_a": 0.10,
            "s_v": 0.25
        })
        assert ver_charlie.status_code == 200
        assert ver_charlie.json()["decision"] == "ACCEPT"

        # 6. Thresholds info
        th_res = client.get("/api/qds/thresholds")
        assert th_res.status_code == 200
        assert th_res.json()["s_a_default"] == 0.10

        # 7. Verifier memory status
        mem_res = client.get(f"/api/qds/memory/Bob?key_id={key_id}")
        assert mem_res.status_code == 200
        assert mem_res.json()["total_states"] == 32


# ===========================================================================
# 8. LEGACY ENDPOINTS COMPATIBILITY TESTS
# ===========================================================================

class TestLegacyEndpointsCompatibility:
    """Ensure existing hash-to-state legacy demo endpoints still respond."""

    def test_legacy_signature_generation(self, client):
        """Legacy /api/signatures/generate still functions."""
        res = client.post("/api/signatures/generate", json={
            "message": "Legacy educational message payload",
            "shots": 512
        })
        assert res.status_code == 200
        data = res.json()
        assert "signature_id" in data
        assert "message_hash" in data
        assert "state_vector" in data

    def test_legacy_verification(self, client):
        """Legacy /api/verification/verify still functions."""
        res = client.post("/api/verification/verify", json={
            "message": "Legacy educational message payload",
            "shots": 512
        })
        assert res.status_code == 200
        data = res.json()
        assert "decision" in data
        assert "fidelity" in data
        assert "threat_score" in data
