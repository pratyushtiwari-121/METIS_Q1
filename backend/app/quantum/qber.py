import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from typing import Dict, Any

# Helper to prepare eigenstates for each basis
def _prepare_basis_state(basis: str) -> QuantumCircuit:
    """Return a 1-qubit circuit that prepares the +1 eigenstate of the given basis.
    basis must be one of 'X', 'Y', 'Z'."""
    qc = QuantumCircuit(1)
    if basis == "X":
        # |+> = H|0>
        qc.h(0)
    elif basis == "Y":
        # |+i> = S† H |0>
        qc.h(0)
        qc.sdg(0)
    elif basis == "Z":
        # |0>
        pass  # already in |0>
    else:
        raise ValueError(f"Unsupported basis '{basis}'")
    return qc

def _measure_in_basis(qc: QuantumCircuit, basis: str) -> QuantumCircuit:
    """Add measurement in the specified basis to a 1‑qubit circuit.
    Returns the same circuit with a measurement on classical bit 0.
    """
    if basis == "X":
        qc.h(0)
    elif basis == "Y":
        qc.sdg(0)
        qc.h(0)
    # Z basis requires no pre‑rotation
    qc.measure(0, 0)
    return qc

def compute_qber(shots: int = 1024, noise_model: Any = None) -> Dict[str, Any]:
    """Compute QBER for X, Y, Z measurement bases.

    Returns a dict with per‑basis statistics and an overall summary.
    """
    simulator = AerSimulator(noise_model=noise_model)
    results: Dict[str, Any] = {}
    total_errors = 0
    total_counts = 0

    for basis in ["X", "Y", "Z"]:
        # Prepare the +1 eigenstate for the basis
        prep = _prepare_basis_state(basis)
        # Add measurement in the same basis
        meas = _measure_in_basis(prep, basis)
        # Ensure a classical register exists
        if not meas.cregs:
            meas.add_register(meas.cregs[0])
        # Run the circuit
        job = simulator.run(transpile(meas, simulator), shots=shots)
        counts = job.result().get_counts()
        # In ideal case, the correct outcome is '0'
        correct = counts.get("0", 0)
        total = sum(counts.values())
        errors = total - correct
        qber = errors / total if total > 0 else 0.0
        results[basis] = {
            "total": total,
            "correct": correct,
            "incorrect": errors,
            "errors": errors,
            "qber": round(qber, 6),
            "percentage": round(qber * 100, 4)
        }
        total_errors += errors
        total_counts += total

    overall_qber = total_errors / total_counts if total_counts > 0 else 0.0
    results["overall"] = {
        "total": total_counts,
        "errors": total_errors,
        "qber": round(overall_qber, 6),
        "percentage": round(overall_qber * 100, 4)
    }
    return results
