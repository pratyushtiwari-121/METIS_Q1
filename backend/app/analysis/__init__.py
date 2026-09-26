"""
Analysis module for Quantum Digital Signatures (QDS).
Provides analytical Hoeffding bounds, Monte Carlo simulations, parameter sweeps,
performance benchmarking (O(L) complexity), and classification metrics.
"""

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
    export_sweeps_to_dict,
    export_sweeps_to_csv,
    HOEFFDING_ASSUMPTIONS,
)
from app.analysis.benchmarks import (
    run_performance_benchmarks,
    run_real_simulation_confusion_matrix,
)

__all__ = [
    "hoeffding_forgery_bound",
    "hoeffding_false_reject_bound",
    "wilson_score_interval",
    "monte_carlo_forgery_simulation",
    "monte_carlo_false_reject_simulation",
    "validate_born_rule_against_aer",
    "sweep_forgery_vs_L",
    "sweep_forgery_vs_threshold",
    "sweep_forgery_vs_strategy",
    "sweep_false_reject_vs_noise",
    "sweep_roc_curve",
    "export_sweeps_to_dict",
    "export_sweeps_to_csv",
    "HOEFFDING_ASSUMPTIONS",
    "run_performance_benchmarks",
    "run_real_simulation_confusion_matrix",
]
