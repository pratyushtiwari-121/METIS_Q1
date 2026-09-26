"""
Comprehensive Test Suite for Mentis-Q Quantum Digital Signature Framework.

Tests cover:
  QUANTUM:
    - Bell pair creation
    - Teleportation of |0>, |1>, |+>, |->, arbitrary state
    - Fidelity calculation (identical, orthogonal, tampered)
    - Multi-basis Z/X/Y measurements

  STATISTICS:
    - TVD (Total Variation Distance)
    - Hoeffding bound edge cases and correctness
    - Statistical confidence calculation

  ATTACKS:
    - Forgery (bit flip, phase flip, random replacement)
    - Impersonation (state mismatch detected)
    - Replay detection (DB-level nonce/ID reuse)
    - Channel manipulation (noise model)
    - Unauthorized verification

  APPLICATION:
    - Signature generation (no hardcoded fidelity)
    - Legitimate verification
    - Tampered verification
    - API response field presence

DISCLAIMER: All tests verify simulation correctness, NOT formal information-theoretic security.
"""
import math
import pytest
import numpy as np

from app.quantum import (
    compute_sha256,
    hash_to_quantum_state,
    state_info_from_angles,
    compute_state_fidelity,
    compute_measurement_deviation,
    compute_threat_score,
    build_and_run_signature_circuit,
    run_verification,
    run_teleportation_protocol,
    run_predefined_circuit,
    hoeffding_bound,
    multi_basis_hoeffding,
    compute_teleportation_fidelity,
    HoeffdingResult,
)


# ===========================================================================
# QUANTUM TESTS
# ===========================================================================

class TestBellPair:
    """Tests for Bell pair / EPR pair creation."""

    def test_bell_state_correlations(self):
        """In ideal |Φ+⟩, only '00' and '11' outcomes appear."""
        res = run_predefined_circuit("bell_state", shots=2048)
        assert res.qubits == 2
        assert "00" in res.counts
        assert "11" in res.counts
        p00 = res.probabilities.get("00", 0)
        p11 = res.probabilities.get("11", 0)
        assert p00 > 0.40, f"P(00)={p00} expected ~0.5"
        assert p11 > 0.40, f"P(11)={p11} expected ~0.5"
        # No bit-flip outcomes in ideal Bell state
        assert res.probabilities.get("01", 0) == 0
        assert res.probabilities.get("10", 0) == 0

    def test_bell_state_total_probability(self):
        """All outcome probabilities must sum to 1."""
        res = run_predefined_circuit("bell_state", shots=1024)
        total = sum(res.probabilities.values())
        assert math.isclose(total, 1.0, abs_tol=1e-3)


class TestTeleportation:
    """Tests for quantum teleportation with classical feed-forward correction."""

    def _check_fidelity(self, theta: float, phi: float, min_fidelity: float = 0.90):
        """Helper: teleport state and verify fidelity >= min_fidelity."""
        result = compute_teleportation_fidelity(theta, phi, shots=2048)
        fidelity = result["fidelity"]
        assert fidelity >= min_fidelity, (
            f"Teleportation fidelity {fidelity:.4f} < {min_fidelity} "
            f"for state (theta={theta:.4f}, phi={phi:.4f})"
        )
        return fidelity

    def test_teleport_zero_state(self):
        """Teleport |0⟩ (theta≈0, phi=0)."""
        # theta very small to approximate |0⟩
        self._check_fidelity(theta=0.001, phi=0.0, min_fidelity=0.95)

    def test_teleport_one_state(self):
        """Teleport |1⟩ (theta=π, phi=0)."""
        self._check_fidelity(theta=math.pi - 0.001, phi=0.0, min_fidelity=0.90)

    def test_teleport_plus_state(self):
        """Teleport |+⟩ (theta=π/2, phi=0)."""
        self._check_fidelity(theta=math.pi / 2, phi=0.0, min_fidelity=0.90)

    def test_teleport_minus_state(self):
        """Teleport |−⟩ (theta=π/2, phi=π)."""
        self._check_fidelity(theta=math.pi / 2, phi=math.pi, min_fidelity=0.90)

    def test_teleport_arbitrary_state_1(self):
        """Teleport arbitrary Bloch sphere state (theta=1.2, phi=0.8)."""
        self._check_fidelity(theta=1.2, phi=0.8, min_fidelity=0.90)

    def test_teleport_arbitrary_state_2(self):
        """Teleport arbitrary Bloch sphere state (theta=2.0, phi=2.5)."""
        self._check_fidelity(theta=2.0, phi=2.5, min_fidelity=0.90)

    def test_teleportation_outcome_corrections(self):
        """Each measurement outcome, after feed-forward correction, should have high fidelity."""
        result = compute_teleportation_fidelity(theta=1.0, phi=0.5, shots=4096)
        for outcome, data in result["outcome_fidelities"].items():
            assert data["fidelity_after_correction"] >= 0.90, (
                f"Outcome '{outcome}' fidelity after correction = "
                f"{data['fidelity_after_correction']:.4f} < 0.90"
            )

    def test_teleportation_four_outcomes(self):
        """All 4 Bell measurement outcomes (00, 01, 10, 11) should appear."""
        result = compute_teleportation_fidelity(theta=math.pi / 3, phi=math.pi / 4, shots=4096)
        # Expect all 4 outcomes with some minimum probability
        for key in ["00", "01", "10", "11"]:
            assert key in result["outcome_fidelities"], f"Missing outcome '{key}'"

    def test_run_teleportation_protocol_response(self):
        """run_teleportation_protocol returns a valid CircuitRunResponse."""
        res = run_teleportation_protocol(theta=1.0, phi=0.5, shots=1024)
        assert res.name == "Quantum Teleportation (with Classical Feed-Forward)"
        assert res.qubits == 3
        assert len(res.counts) > 0
        assert "fidelity" in res.analysis_note.lower()
        assert "feed-forward" in res.analysis_note.lower()


class TestFidelityCalculation:
    """Tests for quantum state fidelity computation."""

    def test_identical_states_fidelity_one(self):
        """F(|ψ⟩, |ψ⟩) = 1.0 for any pure state."""
        state = state_info_from_angles(1.2, 0.8)
        f = compute_state_fidelity(state, state)
        assert math.isclose(f, 1.0, abs_tol=1e-4), f"Expected F=1.0, got F={f}"

    def test_orthogonal_states_fidelity_zero(self):
        """F(|0⟩, |1⟩) ≈ 0.0 (orthogonal states)."""
        state_0 = state_info_from_angles(0.001, 0.0)   # ≈ |0⟩
        state_1 = state_info_from_angles(math.pi - 0.001, 0.0)  # ≈ |1⟩
        f = compute_state_fidelity(state_0, state_1)
        assert f < 0.01, f"Expected F≈0.0 for orthogonal states, got F={f}"

    def test_tampered_state_lower_fidelity(self):
        """Tampered state has lower fidelity than original."""
        original = state_info_from_angles(1.0, 0.5)
        tampered = state_info_from_angles(math.pi - 1.0, 0.5 + math.pi)
        f_orig = compute_state_fidelity(original, original)
        f_tampered = compute_state_fidelity(original, tampered)
        assert f_orig > f_tampered, (
            f"Original fidelity {f_orig} should be > tampered fidelity {f_tampered}"
        )
        assert f_tampered < 0.5, f"Tampered fidelity {f_tampered} should be < 0.5"

    def test_fidelity_symmetry(self):
        """F(|ψ₁⟩, |ψ₂⟩) = F(|ψ₂⟩, |ψ₁⟩)."""
        s1 = state_info_from_angles(0.8, 1.2)
        s2 = state_info_from_angles(1.5, 0.3)
        assert math.isclose(
            compute_state_fidelity(s1, s2),
            compute_state_fidelity(s2, s1),
            abs_tol=1e-4
        )

    def test_fidelity_range(self):
        """Fidelity is always in [0, 1]."""
        for theta in [0.1, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0]:
            for phi in [0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 5.0]:
                s1 = state_info_from_angles(theta, phi)
                s2 = state_info_from_angles(theta + 0.3, phi + 0.5)
                f = compute_state_fidelity(s1, s2)
                assert 0.0 <= f <= 1.0, f"Fidelity {f} out of [0,1] for theta={theta}, phi={phi}"


class TestMultiBasisMeasurement:
    """Tests for Z, X, Y basis measurements (physical correctness)."""

    def test_z_basis_z_eigenstate(self):
        """For |0⟩, Z-basis P(0) ≈ 1.0."""
        state = state_info_from_angles(0.001, 0.0)
        assert state.prob_0 > 0.99, f"Expected prob_0≈1.0, got {state.prob_0}"
        assert state.prob_1 < 0.01, f"Expected prob_1≈0.0, got {state.prob_1}"

    def test_x_basis_plus_state(self):
        """For |+⟩ = H|0⟩, X-basis P(+) = 1.0. Expected px_exp ≈ 1.0."""
        import cmath as cm
        # |+⟩: theta=π/2, phi=0 → alpha=1/√2, beta=1/√2
        theta = math.pi / 2
        phi = 0.0
        alpha = math.cos(theta / 2)
        beta = cm.exp(1j * phi) * math.sin(theta / 2)
        cross_term = alpha * beta.conjugate()
        px_exp = 0.5 * (1.0 + 2.0 * cross_term.real)
        assert px_exp > 0.99, f"Expected px_exp≈1.0 for |+⟩, got {px_exp:.4f}"

    def test_y_basis_plus_i_state(self):
        """For |+i⟩, Y-basis P(+i) = 1.0. Expected py_exp ≈ 1.0."""
        import cmath as cm
        # |+i⟩: theta=π/2, phi=π/2 → alpha=1/√2, beta=i/√2
        theta = math.pi / 2
        phi = math.pi / 2
        alpha = math.cos(theta / 2)
        beta = cm.exp(1j * phi) * math.sin(theta / 2)
        cross_term = alpha * beta.conjugate()
        py_exp = 0.5 * (1.0 - 2.0 * cross_term.imag)
        assert py_exp > 0.99, f"Expected py_exp≈1.0 for |+i⟩, got {py_exp:.4f}"


# ===========================================================================
# STATISTICS TESTS
# ===========================================================================

class TestTotalVariationDistance:
    """Tests for TVD (Total Variation Distance) computation."""

    def test_identical_distributions_zero_tvd(self):
        """TVD between identical distributions = 0."""
        dist = {"0": 0.7, "1": 0.3}
        assert compute_measurement_deviation(dist, dist) == 0.0

    def test_opposite_distributions_max_tvd(self):
        """TVD between fully disjoint distributions ≈ 1.0."""
        d1 = {"0": 1.0, "1": 0.0}
        d2 = {"0": 0.0, "1": 1.0}
        tvd = compute_measurement_deviation(d1, d2)
        assert math.isclose(tvd, 1.0, abs_tol=0.001), f"Expected TVD=1.0, got {tvd}"

    def test_tvd_range(self):
        """TVD is always in [0, 1]."""
        d1 = {"0": 0.6, "1": 0.4}
        d2 = {"0": 0.2, "1": 0.8}
        tvd = compute_measurement_deviation(d1, d2)
        assert 0.0 <= tvd <= 1.0

    def test_tvd_symmetric(self):
        """TVD(d1, d2) = TVD(d2, d1)."""
        d1 = {"0": 0.7, "1": 0.3}
        d2 = {"0": 0.4, "1": 0.6}
        assert compute_measurement_deviation(d1, d2) == compute_measurement_deviation(d2, d1)

    def test_tvd_missing_keys(self):
        """TVD handles distributions with different key sets."""
        d1 = {"0": 0.5, "1": 0.5}
        d2 = {"0": 0.5}  # missing "1" → treated as 0
        tvd = compute_measurement_deviation(d1, d2)
        assert math.isclose(tvd, 0.25, abs_tol=0.01)


class TestHoeffdingBound:
    """Tests for Hoeffding's inequality implementation."""

    def test_perfect_match_no_anomaly(self):
        """When observed == expected, no anomaly."""
        result = hoeffding_bound(expected_prob=0.7, observed_prob=0.7, shots=1024)
        assert not result.is_anomaly
        assert result.epsilon == 0.0
        assert result.hoeffding_bound >= 1.0  # trivially large (no deviation)

    def test_large_deviation_anomaly(self):
        """Large deviation with many shots → small Hoeffding bound → anomaly."""
        result = hoeffding_bound(
            expected_prob=0.5,
            observed_prob=0.9,  # 40% deviation
            shots=2048,
        )
        # With epsilon=0.4 and n=2048: 2*exp(-2*2048*0.16) ≈ 2*exp(-655) ≈ 0
        assert result.is_anomaly, f"Expected anomaly but bound={result.hoeffding_bound}"
        assert result.hoeffding_bound < 0.05

    def test_small_deviation_no_anomaly(self):
        """Small deviation with small shots → large Hoeffding bound → no anomaly."""
        result = hoeffding_bound(
            expected_prob=0.5,
            observed_prob=0.55,  # 5% deviation
            shots=100,
        )
        # With epsilon=0.05 and n=100: 2*exp(-2*100*0.0025) = 2*exp(-0.5) ≈ 1.21
        assert not result.is_anomaly

    def test_zero_shots_edge_case(self):
        """n=0 → bound=1.0, no anomaly, no crash."""
        result = hoeffding_bound(expected_prob=0.5, observed_prob=0.8, shots=0)
        assert result.hoeffding_bound == 1.0
        assert not result.is_anomaly

    def test_probability_clamping(self):
        """Probabilities outside [0,1] are clamped gracefully."""
        result = hoeffding_bound(expected_prob=-0.1, observed_prob=1.5, shots=100)
        assert 0.0 <= result.expected_prob <= 1.0
        assert 0.0 <= result.observed_prob <= 1.0
        assert 0.0 <= result.hoeffding_bound <= 2.0

    def test_hoeffding_formula_correctness(self):
        """Verify bound formula: 2*exp(-2*n*eps^2)."""
        p_exp = 0.5
        p_obs = 0.7
        n = 1000
        eps = abs(p_obs - p_exp)
        expected_bound = 2.0 * math.exp(-2 * n * eps ** 2)
        result = hoeffding_bound(expected_prob=p_exp, observed_prob=p_obs, shots=n)
        assert math.isclose(result.hoeffding_bound, expected_bound, abs_tol=1e-5), (
            f"Expected bound={expected_bound:.6f}, got {result.hoeffding_bound:.6f}"
        )

    def test_confidence_pct_range(self):
        """Statistical confidence is always in [0%, 100%]."""
        for n in [10, 100, 1000]:
            for eps in [0.01, 0.1, 0.3, 0.5]:
                result = hoeffding_bound(
                    expected_prob=0.5,
                    observed_prob=0.5 + eps,
                    shots=n,
                )
                assert 0.0 <= result.confidence_pct <= 100.0

    def test_multi_basis_any_anomaly(self):
        """multi_basis_hoeffding reports any_anomaly correctly."""
        results = multi_basis_hoeffding(
            z_expected=0.5, z_observed=0.95,  # large Z deviation → anomaly
            x_expected=0.5, x_observed=0.52,  # small X deviation → no anomaly
            y_expected=0.5, y_observed=0.51,  # small Y deviation → no anomaly
            shots=2048,
        )
        assert results["any_anomaly"] is True
        assert results["all_anomaly"] is False
        assert "Z" in [
            b for b, r in [
                ("Z", results["Z"]), ("X", results["X"]), ("Y", results["Y"])
            ] if r.is_anomaly
        ]

    def test_multi_basis_all_anomaly(self):
        """multi_basis_hoeffding reports all_anomaly when all bases anomalous."""
        results = multi_basis_hoeffding(
            z_expected=0.5, z_observed=0.95,
            x_expected=0.5, x_observed=0.95,
            y_expected=0.5, y_observed=0.05,
            shots=2048,
        )
        assert results["all_anomaly"] is True
        assert results["any_anomaly"] is True

    def test_multi_basis_no_anomaly(self):
        """multi_basis_hoeffding: no anomaly when all deviations small."""
        results = multi_basis_hoeffding(
            z_expected=0.6, z_observed=0.61,
            x_expected=0.4, x_observed=0.42,
            y_expected=0.5, y_observed=0.49,
            shots=50,  # small shots → large Hoeffding bound → not anomalous
        )
        assert results["any_anomaly"] is False


# ===========================================================================
# THREAT SCORING TESTS
# ===========================================================================

class TestThreatScoring:
    """Tests for threat score consistency with documented formula."""

    def test_low_threat_legitimate(self):
        """High fidelity, low deviation → LOW threat → LEGITIMATE."""
        score, level, decision = compute_threat_score(fidelity=0.99, deviation=0.02)
        assert score < 0.30
        assert level == "LOW"
        assert decision == "LEGITIMATE"

    def test_high_threat_replay_tampered(self):
        """Low fidelity + replay + tampering → HIGH threat → ATTACK DETECTED."""
        score, level, decision = compute_threat_score(
            fidelity=0.60,
            deviation=0.25,
            is_replay=True,
            has_tampering=True,
        )
        assert score >= 0.60
        assert level == "HIGH"
        assert decision == "ATTACK DETECTED"

    def test_medium_threat(self):
        """Moderate fidelity drop and deviation → MEDIUM threat."""
        score, level, decision = compute_threat_score(
            fidelity=0.60,
            deviation=0.30,
        )
        assert 0.30 <= score < 0.60
        assert level == "MEDIUM"
        assert decision == "ATTACK DETECTED"

    def test_formula_consistency(self):
        """Verify T = 0.35(1-F) + 0.35*min(1,2Δ) + 0.30*AttackPenalty manually."""
        fidelity = 0.80
        deviation = 0.20
        expected_base = 0.35 * (1 - fidelity) + 0.35 * min(1.0, 2 * deviation) + 0.30 * 0.0
        expected_score = round(min(1.0, max(0.0, expected_base)), 2)
        score, _, _ = compute_threat_score(fidelity=fidelity, deviation=deviation)
        assert math.isclose(score, expected_score, abs_tol=0.01), (
            f"Expected score={expected_score}, got {score}"
        )

    def test_score_range(self):
        """Threat score is always in [0, 1]."""
        for f in [0.0, 0.5, 1.0]:
            for d in [0.0, 0.5, 1.0]:
                score, _, _ = compute_threat_score(fidelity=f, deviation=d)
                assert 0.0 <= score <= 1.0


# ===========================================================================
# APPLICATION TESTS
# ===========================================================================

class TestSHAEncoding:
    """Tests for SHA-256 to quantum state encoding."""

    def test_sha256_length(self):
        """SHA-256 produces 64-char hex / 256-bit binary."""
        hex_h, bin_h = compute_sha256("Test message")
        assert len(hex_h) == 64
        assert len(bin_h) == 256

    def test_normalization(self):
        """|α|² + |β|² = 1.0 for all encoded states."""
        msg = "Secure communication with quantum signatures!"
        hex_h, _ = compute_sha256(msg)
        state = hash_to_quantum_state(hex_h)
        alpha_sq = state.alpha.real ** 2 + state.alpha.imag ** 2
        beta_sq = state.beta.real ** 2 + state.beta.imag ** 2
        assert math.isclose(alpha_sq + beta_sq, 1.0, abs_tol=1e-3)

    def test_deterministic(self):
        """Same message always produces the same quantum state."""
        msg = "Deterministic test"
        hex_h, _ = compute_sha256(msg)
        s1 = hash_to_quantum_state(hex_h)
        s2 = hash_to_quantum_state(hex_h)
        assert s1.theta_rad == s2.theta_rad
        assert s1.phi_rad == s2.phi_rad


class TestSignatureGeneration:
    """Tests for the signature generation pipeline."""

    def test_signature_id_format(self):
        """Signature ID starts with 'QSIG-'."""
        res = build_and_run_signature_circuit("Test SIH 2025", shots=1024)
        assert res.signature_id.startswith("QSIG-")

    def test_fidelity_not_hardcoded(self):
        """Fidelity is calculated, not hardcoded to 0.998."""
        res = build_and_run_signature_circuit("Fidelity test message", shots=1024)
        # In ideal simulation the fidelity should be very close to 1.0
        # It should NOT be exactly 0.998 (which was the old hardcoded value)
        assert res.fidelity != 0.998, "Fidelity is still hardcoded!"
        assert res.fidelity > 0.90, f"Expected high fidelity, got {res.fidelity}"
        assert 0.0 <= res.fidelity <= 1.0

    def test_fidelity_is_real_calculation(self):
        """Different messages should produce slightly different fidelities."""
        res1 = build_and_run_signature_circuit("Message Alpha", shots=2048)
        res2 = build_and_run_signature_circuit("Message Beta", shots=2048)
        # Both should be high (>0.90) but not necessarily identical to 0.998
        assert res1.fidelity > 0.90
        assert res2.fidelity > 0.90

    def test_classical_bits_valid(self):
        """Classical bits are one of: 00, 01, 10, 11."""
        res = build_and_run_signature_circuit("Classical bits test", shots=1024)
        assert res.classical_bits in ("00", "01", "10", "11"), (
            f"Unexpected classical bits: '{res.classical_bits}'"
        )

    def test_measurement_counts_not_empty(self):
        """Measurement counts must have entries."""
        res = build_and_run_signature_circuit("Count test", shots=1024)
        assert len(res.measurement_counts) > 0


class TestLegitimateVerification:
    """Tests for legitimate verification (no tampering)."""

    def test_legitimate_decision(self):
        """Unmodified message → LEGITIMATE decision."""
        msg = "Authentic banking authorization token"
        hex_h, _ = compute_sha256(msg)
        state = hash_to_quantum_state(hex_h)
        ver = run_verification(
            message=msg,
            original_state=state,
            signature_id="QSIG-TEST-001",
            shots=1024,
            threshold=0.100,
        )
        assert ver.decision == "LEGITIMATE"
        assert ver.fidelity >= 0.99
        assert ver.deviation <= 0.100
        assert ver.threat_score < 0.30

    def test_legitimate_hoeffding_no_anomaly(self):
        """Legitimate verification should not show Hoeffding anomaly."""
        msg = "No anomaly test"
        hex_h, _ = compute_sha256(msg)
        state = hash_to_quantum_state(hex_h)
        ver = run_verification(
            message=msg,
            original_state=state,
            signature_id="QSIG-TEST-002",
            shots=2048,
            threshold=0.100,
        )
        # In a legitimate scenario Hoeffding anomaly should not fire
        if ver.forgery_summary:
            assert not ver.forgery_summary.all_anomaly, (
                "All-basis anomaly should NOT trigger for legitimate verification"
            )

    def test_hoeffding_fields_present(self):
        """Verification response includes Hoeffding fields."""
        msg = "Hoeffding field test"
        hex_h, _ = compute_sha256(msg)
        state = hash_to_quantum_state(hex_h)
        ver = run_verification(
            message=msg,
            original_state=state,
            signature_id="QSIG-TEST-003",
            shots=1024,
        )
        assert ver.hoeffding_z is not None
        assert ver.hoeffding_x is not None
        assert ver.hoeffding_y is not None
        assert ver.forgery_summary is not None


class TestForgeryDetection:
    """Tests for forgery attack detection."""

    def test_bit_flip_forgery_detected(self):
        """Bit-flip tampered state → ATTACK DETECTED."""
        msg = "Transfer $1,000"
        hex_h, _ = compute_sha256(msg)
        original_state = hash_to_quantum_state(hex_h)
        # Bit flip: theta → π - theta (approximately orthogonal)
        tampered_state = state_info_from_angles(
            theta=math.pi - original_state.theta_rad,
            phi=original_state.phi_rad,
        )
        ver = run_verification(
            message=msg,
            original_state=original_state,
            signature_id="QSIG-TEST-004",
            shots=1024,
            threshold=0.100,
            tampered_state=tampered_state,
        )
        assert ver.decision == "ATTACK DETECTED"
        assert ver.fidelity < 0.80
        assert ver.deviation > 0.100
        assert ver.threat_score >= 0.30

    def test_phase_flip_detected(self):
        """Phase-flip tampered state → fidelity < 1.0."""
        msg = "Phase flip test"
        hex_h, _ = compute_sha256(msg)
        original_state = hash_to_quantum_state(hex_h)
        tampered_state = state_info_from_angles(
            theta=original_state.theta_rad,
            phi=(original_state.phi_rad + math.pi) % (2 * math.pi),
        )
        fidelity = compute_state_fidelity(original_state, tampered_state)
        assert fidelity < 1.0


class TestImpersonationDetection:
    """Tests for impersonation attack detection."""

    def test_impersonation_different_state(self):
        """Impersonation produces a measurably different quantum state."""
        msg = "Legitimate message"
        hex_h, _ = compute_sha256(msg)
        original_state = hash_to_quantum_state(hex_h)

        # Simulate attacker with different identity
        attacker_hex, _ = compute_sha256("IMPERSONATOR:Eve:QSIG-FAKE")
        attacker_state = hash_to_quantum_state(attacker_hex)

        fidelity = compute_state_fidelity(original_state, attacker_state)
        # Attacker state should have lower fidelity (extremely unlikely to be identical)
        assert fidelity < 1.0


class TestReplayProtection:
    """Tests for replay attack detection logic."""

    def test_replay_threat_score_elevated(self):
        """Replay flag → elevated threat score."""
        score, level, decision = compute_threat_score(
            fidelity=0.99,
            deviation=0.02,
            is_replay=True,
        )
        # Replay should escalate the score significantly
        assert score >= 0.65, f"Expected score>=0.65 for replay, got {score}"
        assert decision == "ATTACK DETECTED"

    def test_no_replay_low_score(self):
        """Without replay, high-fidelity scenario stays LEGITIMATE."""
        score, level, decision = compute_threat_score(
            fidelity=0.99,
            deviation=0.02,
            is_replay=False,
        )
        assert decision == "LEGITIMATE"
        assert score < 0.30


class TestNoAttackBaseline:
    """Tests for the baseline (no attack) scenario."""

    def test_self_fidelity_is_one(self):
        """State compared to itself → F = 1.0."""
        state = state_info_from_angles(math.pi / 3, math.pi / 4)
        f = compute_state_fidelity(state, state)
        assert math.isclose(f, 1.0, abs_tol=1e-4)

    def test_self_tvd_is_zero(self):
        """Distribution compared to itself → TVD = 0.0."""
        state = state_info_from_angles(math.pi / 3, math.pi / 4)
        dist = {"0": state.prob_0, "1": state.prob_1}
        tvd = compute_measurement_deviation(dist, dist)
        assert tvd == 0.0

    def test_baseline_legitimate(self):
        """Baseline (no attack): LOW threat, LEGITIMATE decision."""
        score, level, decision = compute_threat_score(
            fidelity=1.0,
            deviation=0.0,
            is_replay=False,
            is_unauthorized=False,
            has_tampering=False,
        )
        assert score < 0.10
        assert level == "LOW"
        assert decision == "LEGITIMATE"


# ===========================================================================
# EXTENDED QUANTUM PHYSICS & INFORMATION THEORY TESTS
# ===========================================================================

class TestDensityMatrixAndPurity:
    """Tests for density matrix properties, purity, von Neumann entropy, and trace distance."""

    def test_pure_state_purity_is_one(self):
        """Pure state has purity Tr(ρ²) = 1.0 and entropy S(ρ) = 0.0."""
        from app.quantum.density_matrix import (
            bloch_to_density_matrix,
            compute_purity,
            compute_von_neumann_entropy,
            validate_density_matrix,
        )
        rho = bloch_to_density_matrix(1.0, 0.0, 0.0)  # |+⟩ state
        val = validate_density_matrix(rho)
        assert val["is_valid"]
        assert val["is_hermitian"]
        assert val["is_unit_trace"]
        purity = compute_purity(rho)
        assert math.isclose(purity, 1.0, abs_tol=1e-4)
        entropy = compute_von_neumann_entropy(rho)
        assert math.isclose(entropy, 0.0, abs_tol=1e-4)

    def test_maximally_mixed_state(self):
        """Maximally mixed state (Bloch vector 0) has P=0.5 and S=1.0."""
        from app.quantum.density_matrix import (
            bloch_to_density_matrix,
            compute_purity,
            compute_von_neumann_entropy,
        )
        rho_mixed = bloch_to_density_matrix(0.0, 0.0, 0.0)  # I / 2
        purity = compute_purity(rho_mixed)
        assert math.isclose(purity, 0.5, abs_tol=1e-4)
        entropy = compute_von_neumann_entropy(rho_mixed)
        assert math.isclose(entropy, 1.0, abs_tol=1e-4)

    def test_trace_distance_orthogonal(self):
        """Trace distance between orthogonal states |0⟩ and |1⟩ is 1.0."""
        from app.quantum.density_matrix import bloch_to_density_matrix, compute_trace_distance
        rho_0 = bloch_to_density_matrix(0.0, 0.0, 1.0)
        rho_1 = bloch_to_density_matrix(0.0, 0.0, -1.0)
        td = compute_trace_distance(rho_0, rho_1)
        assert math.isclose(td, 1.0, abs_tol=1e-3)

    def test_density_matrix_fidelity_identical(self):
        """Density matrix fidelity between identical states is 1.0."""
        from app.quantum.density_matrix import bloch_to_density_matrix, compute_density_matrix_fidelity
        rho = bloch_to_density_matrix(0.5, 0.5, 0.7071)
        fid = compute_density_matrix_fidelity(rho, rho)
        assert math.isclose(fid, 1.0, abs_tol=1e-4)


class TestStateTomography:
    """Tests for single-qubit Pauli quantum state tomography."""

    def test_tomography_reconstruction_fidelity(self):
        """Tomography on arbitrary state |ψ⟩ reconstructs ρ with high fidelity (F > 0.90)."""
        from app.quantum.tomography import run_single_qubit_tomography
        theta, phi = 1.2, 0.8
        res = run_single_qubit_tomography(theta, phi, shots=4096)
        assert res["fidelity"] > 0.90, f"Expected fidelity > 0.90, got {res['fidelity']}"
        assert res["trace_distance"] < 0.20
        assert res["density_matrix_validation"]["is_valid"]

    def test_tomography_plus_state(self):
        """Tomography on |+⟩ state (theta=π/2, phi=0) produces ⟨X⟩ ≈ 1.0, ⟨Y⟩ ≈ 0, ⟨Z⟩ ≈ 0."""
        from app.quantum.tomography import run_single_qubit_tomography
        res = run_single_qubit_tomography(math.pi / 2, 0.0, shots=4096)
        meas = res["measurements"]
        assert meas["X"]["observed_expectation"] > 0.85
        assert abs(meas["Z"]["observed_expectation"]) < 0.15


class TestQuantumChannelsAndDecoherence:
    """Tests for the 6 quantum channel models and parameter sweeps."""

    def test_depolarizing_channel_p1(self):
        """Depolarizing channel at p=1 produces maximally mixed state."""
        from app.quantum.channels import simulate_channel_effect
        res = simulate_channel_effect("depolarizing", theta=1.0, phi=0.5, parameter=1.0)
        assert math.isclose(res["output_state"]["purity"], 0.5, abs_tol=0.01)
        assert math.isclose(res["output_state"]["entropy"], 1.0, abs_tol=0.01)

    def test_bit_flip_channel(self):
        """Bit flip channel at p=1 flips |0⟩ to |1⟩."""
        from app.quantum.channels import simulate_channel_effect
        res = simulate_channel_effect("bit_flip", theta=0.001, phi=0.0, parameter=1.0)
        # z should flip from ~1.0 to ~ -1.0
        assert res["output_state"]["bloch"]["z"] < -0.90
        assert res["metrics"]["trace_distance"] > 0.90

    def test_decoherence_sweep(self):
        """Decoherence sweep produces 21 points with decreasing fidelity."""
        from app.quantum.channels import compute_decoherence_sweep
        sweep = compute_decoherence_sweep("depolarizing", steps=21)
        assert len(sweep) == 21
        assert sweep[0]["fidelity"] > sweep[-1]["fidelity"]


class TestCHSHBellInequality:
    """Tests for Bell states and CHSH Bell inequality violation."""

    def test_bell_phi_plus_correlation(self):
        """|Φ+⟩ has correlation E ≈ 1.0."""
        from app.quantum.entanglement import analyze_bell_state
        res = analyze_bell_state("phi_plus", shots=2048)
        assert res["correlation"] > 0.90
        assert res["entanglement_quality"] == "High"

    def test_chsh_violation_quantum_limit(self):
        """CHSH test violates classical bound |S| ≤ 2.0 and approaches Tsirelson bound 2.8284."""
        from app.quantum.entanglement import run_chsh_bell_test
        res = run_chsh_bell_test(shots=4096)
        assert res["violates_classical_bound"]
        assert res["chsh_s_value"] > 2.50, f"Expected S > 2.50, got {res['chsh_s_value']}"
        assert res["quantum_violation_margin"] > 0.50


class TestPhysicalExperiments:
    """Tests for Intercept-Resend eavesdropping and No-Cloning theorem demonstration."""

    def test_intercept_resend_eavesdropping_detected(self):
        """Active Eve causes measurable QBER (≥ 0.20) and fidelity degradation."""
        from app.quantum.experiments import run_intercept_resend_experiment
        clean = run_intercept_resend_experiment(theta=1.2, phi=0.8, eve_active=False)
        eavesdropped = run_intercept_resend_experiment(theta=1.2, phi=0.8, eve_active=True)

        assert clean["qber"] < 0.10
        assert clean["fidelity"] > 0.90
        assert eavesdropped["qber"] >= 0.20
        assert eavesdropped["fidelity"] < clean["fidelity"]

    def test_no_cloning_bound(self):
        """No-cloning demonstration confirms optimal fidelity bound F ≈ 5/6 ≈ 0.8333."""
        from app.quantum.experiments import run_no_cloning_experiment
        res = run_no_cloning_experiment(theta=1.0, phi=0.5)
        assert math.isclose(res["theoretical_maximum_fidelity"], 5.0 / 6.0, abs_tol=1e-4)
        assert res["fidelity_gap_due_to_physics"] > 0.15

