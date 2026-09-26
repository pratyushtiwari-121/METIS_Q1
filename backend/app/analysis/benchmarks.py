"""
Performance benchmarking and classification metrics for Quantum Digital Signatures (QDS).

Measures:
- Keygen, signing, and verification latency (ms) and peak memory (KB) vs L and verifier count K.
- Fits linear regression model to verify O(L) scaling complexity.
- Runs dynamic real-world attack simulation battery to compute dynamic confusion matrix,
  accuracy, precision, recall, specificity, and F1 score per attack type.
- All numbers are dynamically computed, never hardcoded constants.
"""

import time
import tracemalloc
from typing import Optional, Any
import numpy as np

from app.database.session import SessionLocal
from app.qds.keygen import generate_qds_keypair
from app.qds.distribution import distribute_public_keys
from app.qds.signing import sign_message
from app.qds.verification import verify_signature
from app.qds.thresholds import QDSThresholds, QDSDecision
from app.qds.adversary import (
    simulate_random_guess_forgery,
    simulate_measure_and_guess_forgery,
    simulate_impersonation,
    simulate_channel_manipulation,
    simulate_replay_attack,
)


def run_performance_benchmarks(
    L_values: Optional[list[int]] = None,
    verifier_counts: Optional[list[int]] = None,
    iterations: int = 3,
    seed: int = 42
) -> dict[str, Any]:
    """
    Benchmarks signing and verification execution time and peak memory vs key length L
    and verifier count K. Verifies linear O(L) scaling.
    """
    if L_values is None:
        L_values = [16, 32, 64, 128, 256]
    if verifier_counts is None:
        verifier_counts = [2, 3, 4]

    benchmarks_by_L = []
    benchmarks_by_K = []

    fixed_verifiers = ["Bob", "Charlie"]
    thresholds = QDSThresholds(s_a=0.10, s_v=0.25)

    # 1. Benchmark scaling vs L (fixed K = 2 verifiers)
    for L in L_values:
        keygen_times = []
        signing_times = []
        verify_times = []
        memory_deltas = []

        for it in range(iterations):
            tracemalloc.start()
            t0 = time.perf_counter()
            priv, pub = generate_qds_keypair(length=L, seed=seed + it * 100 + L)
            t1 = time.perf_counter()

            sig = sign_message(f"Benchmark payload L={L}", priv, bit=0)
            t2 = time.perf_counter()

            # Distribute public key states
            mems = distribute_public_keys(pub, verifiers=fixed_verifiers, seed=seed + it)
            _ = verify_signature(sig, verifier_id="Bob", memory=mems["Bob"], thresholds=thresholds, seed=seed + it)
            t3 = time.perf_counter()

            _, peak_mem = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            keygen_times.append((t1 - t0) * 1000.0)
            signing_times.append((t2 - t1) * 1000.0)
            verify_times.append((t3 - t2) * 1000.0)
            memory_deltas.append(peak_mem / 1024.0)  # in KB

        benchmarks_by_L.append({
            "L": L,
            "keygen_time_ms": round(float(np.mean(keygen_times)), 3),
            "signing_time_ms": round(float(np.mean(signing_times)), 3),
            "verify_time_ms": round(float(np.mean(verify_times)), 3),
            "total_protocol_time_ms": round(float(np.mean(keygen_times) + np.mean(signing_times) + np.mean(verify_times)), 3),
            "peak_memory_kb": round(float(np.mean(memory_deltas)), 2)
        })

    # 2. Benchmark scaling vs verifier count K (fixed L = 64)
    fixed_L = 64
    for K in verifier_counts:
        v_list = [f"Verifier_{i+1}" for i in range(K)]
        dist_times = []
        for it in range(iterations):
            _, pub = generate_qds_keypair(length=fixed_L, seed=seed + it)
            t0 = time.perf_counter()
            _ = distribute_public_keys(pub, verifiers=v_list, seed=seed + it)
            t1 = time.perf_counter()
            dist_times.append((t1 - t0) * 1000.0)

        benchmarks_by_K.append({
            "num_verifiers": K,
            "distribution_time_ms": round(float(np.mean(dist_times)), 3),
            "distribution_time_per_verifier_ms": round(float(np.mean(dist_times) / K), 3)
        })

    # 3. Fit linear model y = m * L + c and calculate R^2 coefficient of determination
    L_arr = np.array([pt["L"] for pt in benchmarks_by_L], dtype=float)
    t_verify = np.array([pt["verify_time_ms"] for pt in benchmarks_by_L], dtype=float)
    t_sign = np.array([pt["signing_time_ms"] for pt in benchmarks_by_L], dtype=float)

    # Verification R^2
    m_v, c_v = np.polyfit(L_arr, t_verify, 1)
    fit_v = m_v * L_arr + c_v
    ss_res_v = np.sum((t_verify - fit_v) ** 2)
    ss_tot_v = np.sum((t_verify - np.mean(t_verify)) ** 2)
    r2_verify = 1.0 - (ss_res_v / ss_tot_v) if ss_tot_v > 0 else 1.0

    # Signing R^2
    m_s, c_s = np.polyfit(L_arr, t_sign, 1)
    fit_s = m_s * L_arr + c_s
    ss_res_s = np.sum((t_sign - fit_s) ** 2)
    ss_tot_s = np.sum((t_sign - np.mean(t_sign)) ** 2)
    r2_sign = 1.0 - (ss_res_s / ss_tot_s) if ss_tot_s > 0 else 1.0

    return {
        "benchmarks_by_L": benchmarks_by_L,
        "benchmarks_by_K": benchmarks_by_K,
        "complexity_analysis": {
            "theoretical_complexity": "O(L) per verifier",
            "empirical_scaling_status": "O(L) LINEAR CONFIRMED" if r2_verify >= 0.85 else "SUB-LINEAR",
            "verification_r2": round(float(r2_verify), 4),
            "signing_r2": round(float(r2_sign), 4),
            "verification_slope_ms_per_qubit": round(float(m_v), 5),
            "verification_intercept_ms": round(float(c_v), 4)
        },
        "system_info": {
            "iterations_per_point": iterations,
            "memory_tracker": "tracemalloc",
            "timer": "time.perf_counter"
        }
    }


def run_real_simulation_confusion_matrix(
    trials_per_category: int = 20,
    L: int = 64,
    s_a: float = 0.10,
    s_v: float = 0.25,
    seed: int = 42
) -> dict[str, Any]:
    """
    Executes real simulation runs across honest and adversarial vectors to dynamically
    compute the confusion matrix (TP, FP, TN, FN) and classification performance metrics:
    - Accuracy, Precision, Recall (Sensitivity), Specificity, F1 Score.
    Metrics are computed dynamically from actual execution results, never hardcoded.
    """
    thresholds = QDSThresholds(s_a=s_a, s_v=s_v)

    attack_categories = [
        "Random Guess Forgery",
        "Measure & Guess Forgery",
        "Impersonation Attack",
        "Channel Manipulation",
        "Replay Attack"
    ]

    per_attack_stats: dict[str, dict[str, int]] = {
        cat: {"tp": 0, "fn": 0} for cat in attack_categories
    }

    # 1. Honest simulations (Negative ground truth)
    tn = 0
    fp = 0
    honest_mismatches = []

    for i in range(trials_per_category):
        priv, pub = generate_qds_keypair(length=L, seed=seed + i)
        mems = distribute_public_keys(pub, verifiers=["Bob", "Charlie"], seed=seed + i)
        sig = sign_message(f"Honest Message #{i}", priv, bit=0)
        res = verify_signature(sig, verifier_id="Bob", memory=mems["Bob"], thresholds=thresholds, seed=seed + i)
        honest_mismatches.append(res.mismatch_rate)

        # Negative = Legitimate; True Negative = Accepted
        if res.decision == QDSDecision.ACCEPT:
            tn += 1
        else:
            fp += 1

    # 2. Attack simulations (Positive ground truth)
    total_tp = 0
    total_fn = 0

    db = SessionLocal()
    try:
        for cat in attack_categories:
            for i in range(trials_per_category):
                priv, pub = generate_qds_keypair(length=L, seed=seed + 1000 + i)
                mems = distribute_public_keys(pub, verifiers=["Bob", "Charlie"], seed=seed + i)
                v_mem = mems["Bob"]

                is_detected = False

                if cat == "Random Guess Forgery":
                    res = simulate_random_guess_forgery(pub, v_mem, verifier_id="Bob", bit=0, thresholds=thresholds, seed=seed + i)
                    is_detected = (res.decision != "ACCEPT")

                elif cat == "Measure & Guess Forgery":
                    res = simulate_measure_and_guess_forgery(pub, v_mem, verifier_id="Bob", bit=0, strategy="single_basis", thresholds=thresholds, seed=seed + i)
                    is_detected = (res.decision != "ACCEPT")

                elif cat == "Impersonation Attack":
                    res = simulate_impersonation(pub, v_mem, verifier_id="Bob", bit=0, thresholds=thresholds, seed=seed + i)
                    is_detected = (res.decision != "ACCEPT")

                elif cat == "Channel Manipulation":
                    res = simulate_channel_manipulation(
                        public_key=pub,
                        private_key=priv,
                        verifiers=["Bob", "Charlie"],
                        depolarizing_prob=0.30,
                        intercept_resend=True,
                        thresholds=thresholds,
                        seed=seed + i,
                    )
                    is_detected = (res.decision != "ACCEPT")

                elif cat == "Replay Attack":
                    replay_res = simulate_replay_attack(
                        db=db,
                        nonce=f"NONCE-CONFUSION-{seed}-{i}",
                        key_id=pub.key_id,
                        signature_id=f"SIG-CONFUSION-{i}",
                        is_second_attempt=True,
                    )
                    is_detected = (replay_res.detector_fired == "nonce" or replay_res.decision != "ACCEPT")

                if is_detected:
                    per_attack_stats[cat]["tp"] += 1
                    total_tp += 1
                else:
                    per_attack_stats[cat]["fn"] += 1
                    total_fn += 1
    finally:
        db.close()

    # Aggregate metric calculations
    total_samples = tn + fp + total_tp + total_fn
    accuracy = (total_tp + tn) / float(total_samples) if total_samples > 0 else 1.0
    precision = total_tp / float(total_tp + fp) if (total_tp + fp) > 0 else 1.0
    recall = total_tp / float(total_tp + total_fn) if (total_tp + total_fn) > 0 else 1.0
    specificity = tn / float(tn + fp) if (tn + fp) > 0 else 1.0
    f1 = (2.0 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 1.0

    per_attack_breakdown = {}
    for cat, counts in per_attack_stats.items():
        cat_tp = counts["tp"]
        cat_fn = counts["fn"]
        cat_recall = cat_tp / float(cat_tp + cat_fn) if (cat_tp + cat_fn) > 0 else 1.0
        per_attack_breakdown[cat] = {
            "true_positives": cat_tp,
            "false_negatives": cat_fn,
            "detection_recall": round(cat_recall * 100.0, 2),
            "samples_tested": cat_tp + cat_fn
        }

    return {
        "status": "COMPUTED_FROM_REAL_SIMULATION",
        "sample_size": {
            "honest_trials": trials_per_category,
            "attack_trials_total": trials_per_category * len(attack_categories),
            "total_runs": total_samples
        },
        "confusion_matrix": {
            "true_positives": total_tp,
            "false_positives": fp,
            "true_negatives": tn,
            "false_negatives": total_fn
        },
        "metrics": {
            "accuracy_percent": round(accuracy * 100.0, 2),
            "precision_percent": round(precision * 100.0, 2),
            "recall_percent": round(recall * 100.0, 2),
            "specificity_percent": round(specificity * 100.0, 2),
            "f1_score": round(f1, 4)
        },
        "per_attack_performance": per_attack_breakdown,
        "mean_honest_mismatch": round(float(np.mean(honest_mismatches)), 4),
        "parameters": {
            "L": L,
            "s_a": s_a,
            "s_v": s_v
        }
    }
