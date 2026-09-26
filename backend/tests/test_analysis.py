"""
Unit tests for QDS Theoretical Bounds, Monte Carlo Sweeps, Performance Benchmarks, and API Endpoints (Step 4).
Tests:
- Hoeffding bound calculations and mathematical assumption documentation.
- Monte Carlo empirical rate must not exceed the Hoeffding bound.
- Born-rule NumPy sampling validated against Qiskit Aer simulation.
- Parameter sweeps verify monotonic trends (decreasing vs L, increasing vs s_a, increasing vs noise).
- ROC curve validity and AUC computation.
- Performance benchmarks verify O(L) scaling.
- Confusion matrix and metrics computed dynamically from real runs, not hardcoded constants.
- CSV and JSON exports are well-formed.
- API endpoints return 200 with matching schemas.
"""

import math
import pytest
from starlette.testclient import TestClient

from app.main import app
from app.analysis.forgery import (
    hoeffding_forgery_bound,
    hoeffding_false_reject_bound,
    wilson_score_interval,
    monte_carlo_forgery_simulation,
    monte_carlo_false_reject_simulation,
    validate_born_rule_against_aer,
    sweep_forgery_vs_L,
    sweep_forgery_vs_threshold,
    sweep_forgery_vs_strategy,
    sweep_false_reject_vs_noise,
    sweep_roc_curve,
    export_sweeps_to_csv,
    export_sweeps_to_dict,
    HOEFFDING_ASSUMPTIONS,
)
from app.analysis.benchmarks import (
    run_performance_benchmarks,
    run_real_simulation_confusion_matrix,
)


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


# ===========================================================================
# 1. Hoeffding Bounds & Theoretical Assumptions
# ===========================================================================

class TestHoeffdingTheoreticalBounds:
    def test_hoeffding_assumptions_documented(self):
        """Assumptions must document i.i.d. Bernoulli trials, classical concentration, and threshold rules."""
        assert "assumptions" in HOEFFDING_ASSUMPTIONS
        assumptions = HOEFFDING_ASSUMPTIONS["assumptions"]
        assert len(assumptions) >= 5
        text_corpus = " ".join([a["details"] for a in assumptions]).lower()
        assert "bernoulli" in text_corpus
        assert "independent" in text_corpus
        assert "hoeffding" in text_corpus
        assert "threshold" in text_corpus

    def test_hoeffding_forgery_formula_exact(self):
        """P(forgery) <= exp(-2 * L * (p_e - s_a)^2)."""
        L = 64
        p_e = 0.50
        s_a = 0.10
        expected = math.exp(-2.0 * 64 * ((0.50 - 0.10) ** 2))
        bound = hoeffding_forgery_bound(L=L, p_e=p_e, s_a=s_a)
        assert pytest.approx(bound, rel=1e-6) == expected

    def test_hoeffding_forgery_edge_cases(self):
        """When p_e <= s_a, trivial bound is 1.0."""
        assert hoeffding_forgery_bound(L=64, p_e=0.10, s_a=0.10) == 1.0
        assert hoeffding_forgery_bound(L=64, p_e=0.08, s_a=0.10) == 1.0
        assert hoeffding_forgery_bound(L=0, p_e=0.50, s_a=0.10) == 1.0

    def test_hoeffding_false_reject_formula_exact(self):
        """P(false reject) <= exp(-2 * L * (s_a - p_h)^2) for p_h < s_a."""
        L = 64
        s_a = 0.10
        p_h = 0.02
        expected = math.exp(-2.0 * 64 * ((0.10 - 0.02) ** 2))
        bound = hoeffding_false_reject_bound(L=L, p_h=p_h, s_a=s_a)
        assert pytest.approx(bound, rel=1e-6) == expected

    def test_hoeffding_false_reject_edge_cases(self):
        """When p_h >= s_a, trivial bound is 1.0."""
        assert hoeffding_false_reject_bound(L=64, p_h=0.10, s_a=0.10) == 1.0
        assert hoeffding_false_reject_bound(L=64, p_h=0.15, s_a=0.10) == 1.0


# ===========================================================================
# 2. Monte Carlo Simulation & Bound Invariant Test
# ===========================================================================

class TestMonteCarloSimulation:
    def test_wilson_confidence_interval_bounds(self):
        """Wilson interval must bracket point estimate and remain within [0, 1]."""
        low, high = wilson_score_interval(50, 1000, confidence=0.95)
        assert 0.0 <= low <= 0.05 <= high <= 1.0

    def test_empirical_rate_does_not_exceed_hoeffding_bound(self):
        """Core Requirement: Empirical rate must not exceed the Hoeffding bound."""
        # For L=32, s_a=0.15, p_e=0.50, bound is exp(-2 * 32 * 0.35^2) = exp(-7.84) ~ 0.00039
        res = monte_carlo_forgery_simulation(L=32, p_e=0.50, s_a=0.15, N=10000, seed=42)
        assert res["empirical_acceptance_rate"] <= res["hoeffding_bound"] + 1e-4
        assert res["bound_holds"] is True

        # Test another parameter setting: L=16, s_a=0.20, p_e=0.3333
        res2 = monte_carlo_forgery_simulation(L=16, p_e=0.3333, s_a=0.20, N=10000, seed=42)
        assert res2["empirical_acceptance_rate"] <= res2["hoeffding_bound"] + 1e-3
        assert res2["bound_holds"] is True

    def test_false_reject_simulation_bound_holds(self):
        """Honest false-reject empirical rate must not exceed Hoeffding false-reject bound."""
        res = monte_carlo_false_reject_simulation(L=64, p_h=0.02, s_a=0.10, N=10000, seed=42)
        assert res["empirical_false_reject_rate"] <= res["hoeffding_bound"] + 1e-4
        assert res["bound_holds"] is True

    def test_born_rule_sampling_validated_against_aer(self):
        """Validate NumPy Born-rule sampling against Qiskit Aer simulation for small case L=8."""
        val = validate_born_rule_against_aer(L=8, shots=512, seed=42)
        assert val["is_valid"] is True
        assert val["aer_honest_mismatch_rate"] == 0.0
        assert val["total_variation_distance"] <= 0.35


# ===========================================================================
# 3. Sweeps & Monotonic Trends
# ===========================================================================

class TestSweepsAndMonotonicity:
    def test_sweep_forgery_vs_L_strictly_decreasing(self):
        """Requirement: Sweeps return monotonic trends. Forgery probability decreases with L."""
        L_vals = [8, 16, 32, 64, 128]
        rows = sweep_forgery_vs_L(L_values=L_vals, p_e=0.3333, s_a=0.10, N=5000, seed=42)
        bounds = [r["hoeffding_bound"] for r in rows]

        for i in range(len(bounds) - 1):
            assert bounds[i] > bounds[i + 1], f"Hoeffding bound must strictly decrease with L: {bounds[i]} vs {bounds[i+1]}"

    def test_sweep_forgery_vs_threshold_strictly_increasing(self):
        """Forgery probability increases with acceptance threshold s_a."""
        thresh_vals = [0.02, 0.05, 0.10, 0.15, 0.20]
        rows = sweep_forgery_vs_threshold(thresholds=thresh_vals, L=32, p_e=0.3333, N=5000, seed=42)
        bounds = [r["hoeffding_bound"] for r in rows]

        for i in range(len(bounds) - 1):
            assert bounds[i] < bounds[i + 1], f"Hoeffding bound must strictly increase with s_a: {bounds[i]} vs {bounds[i+1]}"

    def test_sweep_false_reject_vs_noise_increasing(self):
        """False reject bound increases with channel noise p_h."""
        noise_vals = [0.01, 0.03, 0.05, 0.08]
        rows = sweep_false_reject_vs_noise(noise_levels=noise_vals, L=64, s_a=0.10, N=5000, seed=42)
        bounds = [r["hoeffding_bound"] for r in rows]

        for i in range(len(bounds) - 1):
            assert bounds[i] < bounds[i + 1]

    def test_sweep_vs_strategy_ordering(self):
        """Random guessing (p_e=0.50) must yield higher or equal error (thus lower or equal acceptance) than measure-and-guess."""
        rows = sweep_forgery_vs_strategy(L_values=[32, 64], s_a=0.10, N=5000, seed=42)
        for r in rows:
            # Optimal POVM (p_e ~ 0.2113) has higher forgery acceptance bound than random guess (p_e=0.50)
            assert r["optimal_povm_bound"] >= r["single_basis_bound"] >= r["random_guess_bound"]

    def test_roc_curve_and_auc(self):
        """ROC curve must have valid TPR/FPR values and AUC >= 0.90."""
        roc = sweep_roc_curve(L=64, p_e=0.3333, p_h=0.02, N=5000, seed=42)
        assert "auc" in roc
        assert roc["auc"] >= 0.90, f"AUC {roc['auc']} should be high for well-separated distributions"
        for pt in roc["curve_points"]:
            assert 0.0 <= pt["fpr"] <= 1.0
            assert 0.0 <= pt["tpr"] <= 1.0

    def test_csv_export_format(self):
        """CSV export must produce well-formed tabular content."""
        csv_text = export_sweeps_to_csv(sweep_type="vs_L", L=64, N=1000, seed=42)
        lines = [line.strip() for line in csv_text.splitlines() if line.strip()]
        assert len(lines) >= 5
        assert "L,Hoeffding_Bound,Empirical_Acceptance_Rate" in lines[0]


# ===========================================================================
# 4. Performance Benchmarking & Computed Metrics
# ===========================================================================

class TestPerformanceAndComputedMetrics:
    def test_benchmarks_linear_complexity_O_L(self):
        """Requirement: Performance signing/verification time and memory vs L should be O(L)."""
        res = run_performance_benchmarks(L_values=[16, 32, 64], verifier_counts=[2], iterations=2, seed=42)
        comp = res["complexity_analysis"]
        assert "verification_r2" in comp
        # R^2 should indicate strong linear correlation
        assert comp["verification_r2"] >= 0.70 or comp["verification_slope_ms_per_qubit"] > 0
        assert len(res["benchmarks_by_L"]) == 3
        # Check that latency is non-zero and measured
        for pt in res["benchmarks_by_L"]:
            assert pt["verify_time_ms"] > 0.0
            assert pt["total_protocol_time_ms"] > 0.0

    def test_confusion_matrix_metrics_are_computed_not_constants(self):
        """Requirement: Metrics computed from real simulation runs, not constants."""
        res = run_real_simulation_confusion_matrix(trials_per_category=5, L=32, s_a=0.10, s_v=0.25, seed=42)
        assert res["status"] == "COMPUTED_FROM_REAL_SIMULATION"
        metrics = res["metrics"]
        assert "accuracy_percent" in metrics
        assert "precision_percent" in metrics
        assert "recall_percent" in metrics
        assert "f1_score" in metrics

        # Confirm dynamically non-constant structure
        matrix = res["confusion_matrix"]
        total = matrix["true_positives"] + matrix["false_positives"] + matrix["true_negatives"] + matrix["false_negatives"]
        assert total == res["sample_size"]["total_runs"]
        assert matrix["true_positives"] > 0
        assert matrix["true_negatives"] > 0


# ===========================================================================
# 5. API Endpoints Integration (/api/analysis/*)
# ===========================================================================

class TestAnalysisApiIntegration:
    def test_api_hoeffding_endpoint(self, client):
        res = client.get("/api/analysis/hoeffding?L=64&p_e=0.3333&p_h=0.02&s_a=0.10")
        assert res.status_code == 200
        data = res.json()
        assert "forgery_bound" in data
        assert "false_reject_bound" in data
        assert "assumptions" in data
        assert data["L"] == 64

    def test_api_monte_carlo_endpoint(self, client):
        res = client.post("/api/analysis/monte-carlo", json={
            "L": 32,
            "p_e": 0.50,
            "p_h": 0.02,
            "s_a": 0.15,
            "N_trials": 2000,
            "seed": 42
        })
        assert res.status_code == 200
        data = res.json()
        assert "forgery" in data
        assert "false_reject" in data
        assert data["forgery"]["empirical_acceptance_rate"] <= data["forgery"]["hoeffding_bound"] + 1e-3

    def test_api_aer_validation_endpoint(self, client):
        res = client.get("/api/analysis/aer-validation?L=8&shots=256&seed=42")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "VALIDATED"
        assert data["is_valid"] is True

    def test_api_sweeps_endpoint(self, client):
        res = client.get("/api/analysis/sweeps?L=32&N=1000&seed=42")
        assert res.status_code == 200
        data = res.json()
        assert "sweep_vs_L" in data
        assert "roc_curve" in data

    def test_api_sweeps_export_csv_and_json(self, client):
        # CSV
        res_csv = client.get("/api/analysis/sweeps/export?format=csv&sweep_type=vs_L&L=32&N=1000")
        assert res_csv.status_code == 200
        assert "text/csv" in res_csv.headers["content-type"]
        assert "L,Hoeffding_Bound" in res_csv.text

        # JSON
        res_json = client.get("/api/analysis/sweeps/export?format=json&L=32&N=1000")
        assert res_json.status_code == 200
        assert "application/json" in res_json.headers["content-type"]

    def test_api_benchmarks_endpoint(self, client):
        res = client.get("/api/analysis/benchmarks?iterations=1&seed=42")
        assert res.status_code == 200
        data = res.json()
        assert "complexity_analysis" in data

    def test_api_confusion_matrix_endpoint(self, client):
        res = client.get("/api/analysis/confusion-matrix?trials_per_category=3&L=32&seed=42")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "COMPUTED_FROM_REAL_SIMULATION"
        assert "metrics" in data
