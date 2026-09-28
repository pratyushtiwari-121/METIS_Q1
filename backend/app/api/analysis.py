"""
API Router for QDS Theoretical Bounds, Monte Carlo Sweeps & Performance Benchmarks.
Mounted under /api/analysis/*.
"""

from typing import Optional
from fastapi import APIRouter, Query, Response
from fastapi.responses import JSONResponse

from app.schemas.schemas import (
    HoeffdingBoundResponse,
    MonteCarloSimulationRequest,
    MonteCarloSimulationResponse,
    AerValidationResponse,
    SweepsResponse,
    PerformanceBenchmarkResponse,
    ConfusionMatrixResponse,
)
from app.analysis.forgery import (
    hoeffding_forgery_bound,
    hoeffding_false_reject_bound,
    monte_carlo_forgery_simulation,
    monte_carlo_false_reject_simulation,
    validate_born_rule_against_aer,
    export_sweeps_to_dict,
    export_sweeps_to_csv,
    HOEFFDING_ASSUMPTIONS,
)
from app.analysis.benchmarks import (
    run_performance_benchmarks,
    run_real_simulation_confusion_matrix,
)

router = APIRouter(prefix="/analysis", tags=["QDS Security Analysis"])


@router.get("/hoeffding", response_model=HoeffdingBoundResponse)
def get_hoeffding_bounds(
    L: int = Query(default=64, ge=1, le=4096, description="Key length / qubit copies"),
    p_e: float = Query(default=0.3333, ge=0.0, le=1.0, description="Adversary per-copy mismatch rate"),
    p_h: float = Query(default=0.02, ge=0.0, le=1.0, description="Honest channel error rate"),
    s_a: float = Query(default=0.10, ge=0.0, lt=0.5, description="Acceptance threshold")
):
    """
    Computes analytical Hoeffding concentration bounds and returns mathematical assumptions.
    - P(forgery accepted) <= exp(-2 * L * (p_e - s_a)^2)
    - P(false reject)     <= exp(-2 * L * (s_a - p_h)^2)
    """
    forgery_bound = hoeffding_forgery_bound(L=L, p_e=p_e, s_a=s_a)
    false_reject_bound = hoeffding_false_reject_bound(L=L, p_h=p_h, s_a=s_a)

    return HoeffdingBoundResponse(
        L=L,
        p_e=round(p_e, 4),
        p_h=round(p_h, 4),
        s_a=round(s_a, 4),
        forgery_bound=round(forgery_bound, 8),
        false_reject_bound=round(false_reject_bound, 8),
        forgery_formula="P(forgery accepted) <= exp(-2 * L * (p_e - s_a)^2)",
        false_reject_formula="P(false reject) <= exp(-2 * L * (s_a - p_h)^2)",
        assumptions=HOEFFDING_ASSUMPTIONS
    )


@router.post("/monte-carlo", response_model=MonteCarloSimulationResponse)
def run_monte_carlo(req: MonteCarloSimulationRequest):
    """
    Runs vectorized NumPy Born-rule Monte Carlo simulation with Wilson confidence intervals.
    Validates that empirical acceptance rate does not exceed the Hoeffding bound.
    """
    res_forgery = monte_carlo_forgery_simulation(
        L=req.L,
        p_e=req.p_e,
        s_a=req.s_a,
        N=req.N_trials,
        seed=req.seed
    )
    res_false_reject = monte_carlo_false_reject_simulation(
        L=req.L,
        p_h=req.p_h,
        s_a=req.s_a,
        N=req.N_trials,
        seed=req.seed
    )

    empirical_le_bound = bool(res_forgery["bound_holds"])
    summary = (
        f"Simulated {req.N_trials:,} trials (L={req.L}, s_a={req.s_a:.2f}). "
        f"Forgery acceptance empirical rate: {res_forgery['empirical_acceptance_rate']:.6f} "
        f"(95% CI [{res_forgery['ci_95_lower']:.6f}, {res_forgery['ci_95_upper']:.6f}]), "
        f"Hoeffding bound: {res_forgery['hoeffding_bound']:.6f}. "
        f"Bound holds: {empirical_le_bound}."
    )

    return MonteCarloSimulationResponse(
        forgery=res_forgery,
        false_reject=res_false_reject,
        empirical_rate_le_bound=empirical_le_bound,
        summary=summary
    )


@router.get("/aer-validation", response_model=AerValidationResponse)
def validate_aer_born_rule(
    L: int = Query(default=8, ge=4, le=16, description="Qubit count for Aer circuit"),
    shots: int = Query(default=1024, ge=100, le=4096),
    seed: int = Query(default=42)
):
    """
    Cross-validates NumPy Born-rule sampling against full Qiskit Aer circuit simulation.
    """
    val = validate_born_rule_against_aer(L=L, shots=shots, seed=seed)
    return AerValidationResponse(**val)


@router.get("/sweeps", response_model=SweepsResponse)
def get_sweeps(
    L: int = Query(default=64, ge=8, le=512),
    s_a: float = Query(default=0.10, ge=0.01, lt=0.5),
    p_e: float = Query(default=0.3333, ge=0.05, le=0.50),
    p_h: float = Query(default=0.02, ge=0.0, le=0.20),
    N: int = Query(default=10000, ge=1000, le=50000),
    seed: int = Query(default=42)
):
    """
    Returns multi-parameter sweeps (vs L, vs s_a, vs strategy, false-reject vs noise, and ROC curve).
    """
    data = export_sweeps_to_dict(L=L, s_a=s_a, p_e=p_e, p_h=p_h, N=N, seed=seed)
    return SweepsResponse(**data)


@router.get("/sweeps/export")
def export_sweeps(
    format: str = Query(default="json", pattern="^(json|csv)$"),
    sweep_type: str = Query(default="vs_L", pattern="^(vs_L|vs_threshold|vs_strategy|vs_noise|roc)$"),
    L: int = Query(default=64, ge=8, le=512),
    s_a: float = Query(default=0.10, ge=0.01, lt=0.5),
    p_e: float = Query(default=0.3333, ge=0.05, le=0.50),
    p_h: float = Query(default=0.02, ge=0.0, le=0.20),
    N: int = Query(default=10000, ge=1000, le=50000),
    seed: int = Query(default=42)
):
    """
    Exports sweep data in JSON or CSV format for external analysis.
    """
    if format == "csv":
        csv_content = export_sweeps_to_csv(
            sweep_type=sweep_type,
            L=L,
            s_a=s_a,
            p_e=p_e,
            p_h=p_h,
            N=N,
            seed=seed
        )
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=qds_sweep_{sweep_type}.csv"}
        )
    else:
        dict_data = export_sweeps_to_dict(L=L, s_a=s_a, p_e=p_e, p_h=p_h, N=N, seed=seed)
        return JSONResponse(content=dict_data)


@router.get("/benchmarks", response_model=PerformanceBenchmarkResponse)
def get_benchmarks(
    iterations: int = Query(default=2, ge=1, le=5),
    seed: int = Query(default=42)
):
    """
    Runs performance latency and memory benchmarks vs L and K, verifying O(L) scaling.
    """
    res = run_performance_benchmarks(iterations=iterations, seed=seed)
    return PerformanceBenchmarkResponse(**res)


@router.get("/confusion-matrix", response_model=ConfusionMatrixResponse)
def get_confusion_matrix(
    trials_per_category: int = Query(default=20, ge=1, le=100),
    L: int = Query(default=64, ge=8, le=256),
    s_a: float = Query(default=0.10, ge=0.01, lt=0.5),
    s_v: float = Query(default=0.25, gt=0.01, lt=0.5),
    seed: int = Query(default=42)
):
    """
    Runs real simulation battery across attack types and computes dynamic confusion matrix,
    accuracy, precision, recall, specificity, and F1 score. All numbers are dynamically computed.
    """
    res = run_real_simulation_confusion_matrix(
        trials_per_category=trials_per_category,
        L=L,
        s_a=s_a,
        s_v=s_v,
        seed=seed
    )
    return ConfusionMatrixResponse(**res)
