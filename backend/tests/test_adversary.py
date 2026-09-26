"""
Comprehensive Test Suite for QDS Adversary Simulation & Threat Detectors (Step 3).

Tests:
  1. Forgery by Random Guess (Expected mismatch 0.50, detector: 'threshold')
  2. Forgery by Measure-and-Guess (Single-basis and multi-basis; cited literature bound)
  3. Impersonation (Attacker with no key material rejected)
  4. Channel Manipulation & Intercept-Resend (Distribution channel noise detected)
  5. Replay Attack (Real nonce store: first submission accepted, second rejected, logged)
  6. Unauthorized Verification & Sliding-Window Rate Limiter (Token check, rate limit lockout)
  7. /api/attacks/simulate Endpoint Integration
"""

import math
import pytest
import numpy as np
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.database.session import SessionLocal
from app.database.models import QDSNonce, QDSVerifier, QDSClientRateLimit, Log
from app.qds import (
    generate_qds_keypair,
    distribute_public_keys,
    sign_message,
    QDSThresholds,
    QDSDecision,
    QuantumMemoryRegistry,
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


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


# ===========================================================================
# 1. FORGERY BY RANDOM GUESS
# ===========================================================================

class TestRandomGuessForgery:
    """Test random guess forgery has expected mismatch rate 0.50 and triggers threshold detector."""

    def test_random_guess_expected_mismatch_and_rejection(self):
        priv, pub = generate_qds_keypair(length=128, seed=42)
        reg = QuantumMemoryRegistry()
        memories = distribute_public_keys(pub, verifiers=["Bob", "Charlie"], registry=reg, seed=42)

        res = simulate_random_guess_forgery(
            public_key=pub,
            memory=memories["Bob"],
            verifier_id="Bob",
            bit=0,
            thresholds=QDSThresholds(s_a=0.10, s_v=0.25),
            seed=42,
        )

        assert res.detector_fired == "threshold"
        assert res.decision == "REJECT"
        assert res.expected_mismatch == 0.50
        # For L=128, empirical mismatch should be near 0.50 within statistical margin
        assert 0.40 <= res.measured_mismatch_rate <= 0.60
        assert "Threshold" in res.outcome


# ===========================================================================
# 2. FORGERY BY MEASURE-AND-GUESS ON PUBLIC-KEY COPIES
# ===========================================================================

class TestMeasureAndGuessForgery:
    """Test measure-and-guess strategies and cited literature bounds."""

    def test_single_basis_measure_and_guess(self):
        """Single-basis measurement gives expected mismatch ~33.33%."""
        priv, pub = generate_qds_keypair(length=96, seed=101)
        reg = QuantumMemoryRegistry()
        memories = distribute_public_keys(pub, verifiers=["Bob", "Charlie"], registry=reg, seed=101)

        res = simulate_measure_and_guess_forgery(
            public_key=pub,
            memory=memories["Bob"],
            verifier_id="Bob",
            strategy="single_basis",
            fixed_basis="Z",
            thresholds=QDSThresholds(s_a=0.10, s_v=0.25),
            seed=101,
        )

        assert res.detector_fired == "threshold"
        assert res.expected_mismatch == pytest.approx(1.0 / 3.0, rel=1e-3)
        # Measured mismatch rate should be near ~33%
        assert 0.20 <= res.measured_mismatch_rate <= 0.45
        assert res.decision in ("REJECT", "INCONCLUSIVE_ARBITRATION")

    def test_multi_basis_measure_and_guess_literature_bound(self):
        """Multi-basis strategy reports empirical mismatch and cites literature bound."""
        priv, pub = generate_qds_keypair(length=96, seed=202)
        reg = QuantumMemoryRegistry()
        memories = distribute_public_keys(pub, verifiers=["Bob", "Charlie"], registry=reg, seed=202)

        res = simulate_measure_and_guess_forgery(
            public_key=pub,
            memory=memories["Bob"],
            verifier_id="Bob",
            strategy="multi_basis",
            thresholds=QDSThresholds(s_a=0.10, s_v=0.25),
            seed=202,
        )

        assert res.detector_fired == "threshold"
        assert res.literature_bound is not None
        assert "Clarke et al." in res.literature_bound
        assert "Arrazola & Neduvath" in res.literature_bound
        # Bound is 1/2(1 - 1/√3) ≈ 21.13%
        assert res.expected_mismatch == pytest.approx(0.5 * (1.0 - 1.0 / math.sqrt(3.0)), rel=1e-3)
        assert res.measured_mismatch_rate >= 0.10  # exceeds acceptance threshold s_a


# ===========================================================================
# 3. IMPERSONATION ATTACK
# ===========================================================================

class TestImpersonationAttack:
    """Test attacker with no key material is detected and rejected."""

    def test_impersonation_detection(self):
        priv, pub = generate_qds_keypair(length=64, seed=303)
        reg = QuantumMemoryRegistry()
        memories = distribute_public_keys(pub, verifiers=["Bob", "Charlie"], registry=reg, seed=303)

        res = simulate_impersonation(
            public_key=pub,
            memory=memories["Bob"],
            verifier_id="Bob",
            attacker_name="Eve The Impersonator",
            seed=303,
        )

        assert res.detector_fired == "threshold"
        assert res.decision == "REJECT"
        assert res.measured_mismatch_rate > 0.25


# ===========================================================================
# 4. CHANNEL MANIPULATION & INTERCEPT-RESEND
# ===========================================================================

class TestChannelManipulationAttack:
    """Test channel noise and intercept-resend eavesdropping detection."""

    def test_intercept_resend_channel_attack(self):
        priv, pub = generate_qds_keypair(length=64, seed=404)

        res = simulate_channel_manipulation(
            public_key=pub,
            private_key=priv,
            depolarizing_prob=0.30,
            intercept_resend=True,
            thresholds=QDSThresholds(s_a=0.10, s_v=0.25),
            seed=404,
        )

        assert res.detector_fired == "threshold"
        assert res.decision in ("REJECT", "INCONCLUSIVE_ARBITRATION")
        assert "Intercept-Resend" in res.literature_bound
        assert res.measured_mismatch_rate > 0.10


# ===========================================================================
# 5. REPLAY ATTACK WITH REAL NONCE STORE
# ===========================================================================

class TestReplayAttackProtection:
    """Test real nonce database table, one-time use, and replay rejection on second submission."""

    def test_nonce_one_time_use_and_second_submission_rejection(self, db: Session):
        test_nonce = f"NONCE-TEST-{datetime.now(timezone.utc).timestamp()}"
        key_id = "QDS-KEY-TEST-001"
        sig_id = "QDSSIG-TEST-001"

        # 1. First submission: must succeed
        valid1, reason1, det1 = validate_and_consume_nonce(
            db=db, nonce=test_nonce, key_id=key_id, signature_id=sig_id, ttl_seconds=300
        )
        assert valid1 is True
        assert det1 is None

        # Verify in DB that it is marked consumed
        record = db.query(QDSNonce).filter(QDSNonce.nonce == test_nonce).first()
        assert record is not None
        assert record.is_consumed is True

        # 2. Second submission (Replay attempt): must be REJECTED
        valid2, reason2, det2 = validate_and_consume_nonce(
            db=db, nonce=test_nonce, key_id=key_id, signature_id=sig_id, ttl_seconds=300
        )
        assert valid2 is False
        assert det2 == "nonce"
        assert "already been consumed" in reason2

        # 3. High-severity log must be in `logs` table
        log_entry = db.query(Log).filter(
            Log.event_type == "Replay Attack",
            Log.signature_id == sig_id
        ).order_by(Log.timestamp.desc()).first()
        assert log_entry is not None
        assert log_entry.status == "Blocked"
        assert "Replay detected" in log_entry.details

    def test_simulate_replay_attack_helper(self, db: Session):
        nonce = f"NONCE-SIM-{datetime.now(timezone.utc).timestamp()}"
        res = simulate_replay_attack(
            db=db, nonce=nonce, key_id="KEY-1", signature_id="SIG-1", is_second_attempt=True
        )
        assert res.detector_fired == "nonce"
        assert res.decision == "REJECT"
        assert "Replay" in res.outcome


# ===========================================================================
# 6. UNAUTHORIZED VERIFICATION & SLIDING-WINDOW RATE LIMITER
# ===========================================================================

class TestUnauthorizedAndRateLimiter:
    """Test verifier token checks and sliding-window rate limit lockout."""

    def test_unauthorized_token_rejection(self, db: Session):
        client_id = f"client_unauth_{datetime.now(timezone.utc).timestamp()}"
        res = simulate_unauthorized_attack(
            db=db, client_id=client_id, verifier_id="Bob", auth_token="BAD_CREDENTIALS"
        )
        assert res.detector_fired == "authorization"
        assert res.decision == "REJECT"
        assert "Authorization" in res.outcome

    def test_sliding_window_rate_limit_lockout(self, db: Session):
        client_id = f"dos_flooder_{datetime.now(timezone.utc).timestamp()}"
        max_requests = 3
        window_seconds = 60

        res = simulate_rate_limit_attack(
            db=db, client_id=client_id, verifier_id="Bob", max_requests=max_requests, window_seconds=window_seconds
        )

        assert res.detector_fired == "rate-limit"
        assert res.decision == "REJECT"
        assert "Rate Limiter" in res.outcome

        # Check DB log for lockout event
        log_entry = db.query(Log).filter(
            Log.event_type == "Rate Limit Lockout",
            Log.details.like(f"%{client_id}%")
        ).first()
        assert log_entry is not None
        assert log_entry.status == "Blocked"


# ===========================================================================
# 7. /api/attacks/simulate ENDPOINT INTEGRATION
# ===========================================================================

class TestAttackSimulateApiIntegration:
    """Test updated /api/attacks/simulate endpoint returns detector_fired and QDS fields."""

    def test_api_simulate_forgery(self, client):
        res = client.post("/api/attacks/simulate", json={
            "attack_type": "Forgery Attack",
            "modification_type": "Alter Quantum State (Bit Flip)",
            "attack_intensity": 0.8,
            "shots": 512,
        })
        assert res.status_code == 200
        data = res.json()
        assert data["detector_fired"] == "threshold"
        assert "decision" in data

    def test_api_simulate_replay(self, client):
        res = client.post("/api/attacks/simulate", json={
            "attack_type": "Replay Attack",
            "nonce": f"NONCE-API-TEST-{datetime.now(timezone.utc).timestamp()}",
            "shots": 512,
        })
        assert res.status_code == 200
        data = res.json()
        assert data["detector_fired"] == "nonce"
        assert data["decision"] == "ATTACK DETECTED"

    def test_api_simulate_rate_limit(self, client):
        res = client.post("/api/attacks/simulate", json={
            "attack_type": "Rate Limit Flooding",
            "shots": 512,
        })
        assert res.status_code == 200
        data = res.json()
        assert data["detector_fired"] == "rate-limit"

    def test_api_simulate_unauthorized(self, client):
        res = client.post("/api/attacks/simulate", json={
            "attack_type": "Unauthorized Verification",
            "shots": 512,
        })
        assert res.status_code == 200
        data = res.json()
        assert data["detector_fired"] == "authorization"
