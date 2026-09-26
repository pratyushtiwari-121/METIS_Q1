"""
Universal Quantum Circuit builder and runner supporting predefined circuits and custom user drag/drop gate structures.
"""
import math
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from app.schemas.schemas import GateItem, CircuitRunResponse, StateVectorInfo
from app.quantum.state_encoding import state_info_from_angles

def run_predefined_circuit(circuit_name: str, shots: int = 1024, custom_angle: float | None = None) -> CircuitRunResponse:
    """
    Executes a standard predefined quantum circuit.
    """
    simulator = AerSimulator()

    if circuit_name == "bell_state":
        qc = QuantumCircuit(2, 2)
        qc.h(0)
        qc.cx(0, 1)
        qc.measure([0, 1], [0, 1])

        counts = simulator.run(transpile(qc, simulator), shots=shots).result().get_counts()
        probs = {k: round(v / shots, 4) for k, v in sorted(counts.items())}
        ascii_art = qc.draw(output="text").single_string()
        code = f'''from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

qc = QuantumCircuit(2, 2)
qc.h(0)
qc.cx(0, 1)
qc.measure([0, 1], [0, 1])

sim = AerSimulator()
counts = sim.run(transpile(qc, sim), shots={shots}).result().get_counts()
print(counts)
'''
        return CircuitRunResponse(
            name="Bell State (|Phi+>)",
            description="Creates a maximally entangled 2-qubit Bell state: (|00> + |11>) / sqrt(2)",
            qubits=2,
            depth=qc.depth(),
            gate_count=len(qc.data),
            circuit_type="Entanglement",
            circuit_ascii=ascii_art,
            qiskit_code=code,
            counts=counts,
            probabilities=probs,
            expected_formula="|Phi+> = (|00> + |11>) / sqrt(2)",
            analysis_note="Measurement results show near 50/50 correlation between |00> and |11>, with 0% probability for |01> and |10|."
        )

    elif circuit_name == "superposition":
        qc = QuantumCircuit(1, 1)
        qc.h(0)
        qc.measure(0, 0)

        counts = simulator.run(transpile(qc, simulator), shots=shots).result().get_counts()
        probs = {k: round(v / shots, 4) for k, v in sorted(counts.items())}
        ascii_art = qc.draw(output="text").single_string()
        code = f'''from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

qc = QuantumCircuit(1, 1)
qc.h(0)
qc.measure(0, 0)

sim = AerSimulator()
counts = sim.run(transpile(qc, sim), shots={shots}).result().get_counts()
print(counts)
'''
        return CircuitRunResponse(
            name="Single Qubit Superposition",
            description="Applies a Hadamard gate to place |0> into equal superposition: (|0> + |1>) / sqrt(2)",
            qubits=1,
            depth=qc.depth(),
            gate_count=len(qc.data),
            circuit_type="Superposition",
            circuit_ascii=ascii_art,
            qiskit_code=code,
            counts=counts,
            probabilities=probs,
            expected_formula="|+> = (|0> + |1>) / sqrt(2)",
            analysis_note="Equal 50% probability of collapsing to |0> or |1> upon measurement."
        )

    elif circuit_name == "bit_flip":
        qc = QuantumCircuit(1, 1)
        qc.x(0)
        qc.measure(0, 0)

        counts = simulator.run(transpile(qc, simulator), shots=shots).result().get_counts()
        probs = {k: round(v / shots, 4) for k, v in sorted(counts.items())}
        ascii_art = qc.draw(output="text").single_string()
        code = f'''from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

qc = QuantumCircuit(1, 1)
qc.x(0)
qc.measure(0, 0)

sim = AerSimulator()
counts = sim.run(transpile(qc, sim), shots={shots}).result().get_counts()
print(counts)
'''
        return CircuitRunResponse(
            name="Pauli-X (Bit Flip)",
            description="Flips the computational basis state |0> to |1> (quantum NOT gate)",
            qubits=1,
            depth=qc.depth(),
            gate_count=len(qc.data),
            circuit_type="Pauli Error",
            circuit_ascii=ascii_art,
            qiskit_code=code,
            counts=counts,
            probabilities=probs,
            expected_formula="X|0> = |1>",
            analysis_note="Deterministic 100% measurement outcome in state |1>."
        )

    elif circuit_name == "phase_flip":
        qc = QuantumCircuit(1, 1)
        qc.h(0)
        qc.z(0)
        qc.h(0)
        qc.measure(0, 0)

        counts = simulator.run(transpile(qc, simulator), shots=shots).result().get_counts()
        probs = {k: round(v / shots, 4) for k, v in sorted(counts.items())}
        ascii_art = qc.draw(output="text").single_string()
        code = f'''from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

qc = QuantumCircuit(1, 1)
qc.h(0)
qc.z(0)
qc.h(0)
qc.measure(0, 0)

sim = AerSimulator()
counts = sim.run(transpile(qc, sim), shots={shots}).result().get_counts()
print(counts)
'''
        return CircuitRunResponse(
            name="Pauli-Z (Phase Flip in X-basis)",
            description="Applies a relative phase shift of pi (Z gate) in the superposition basis, transforming |+> to |->",
            qubits=1,
            depth=qc.depth(),
            gate_count=len(qc.data),
            circuit_type="Pauli Error",
            circuit_ascii=ascii_art,
            qiskit_code=code,
            counts=counts,
            probabilities=probs,
            expected_formula="H Z H |0> = |1>",
            analysis_note="Interference converts the relative phase change into a bit flip measured as |1>."
        )

    elif circuit_name == "entanglement":  # GHZ 3-qubit state
        qc = QuantumCircuit(3, 3)
        qc.h(0)
        qc.cx(0, 1)
        qc.cx(1, 2)
        qc.measure([0, 1, 2], [0, 1, 2])

        counts = simulator.run(transpile(qc, simulator), shots=shots).result().get_counts()
        probs = {k: round(v / shots, 4) for k, v in sorted(counts.items())}
        ascii_art = qc.draw(output="text").single_string()
        code = f'''from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

qc = QuantumCircuit(3, 3)
qc.h(0)
qc.cx(0, 1)
qc.cx(1, 2)
qc.measure([0, 1, 2], [0, 1, 2])

sim = AerSimulator()
counts = sim.run(transpile(qc, sim), shots={shots}).result().get_counts()
print(counts)
'''
        return CircuitRunResponse(
            name="GHZ Tripartite Entanglement",
            description="Generates 3-qubit Greenberger-Horne-Zeilinger entangled state: (|000> + |111>) / sqrt(2)",
            qubits=3,
            depth=qc.depth(),
            gate_count=len(qc.data),
            circuit_type="Entanglement",
            circuit_ascii=ascii_art,
            qiskit_code=code,
            counts=counts,
            probabilities=probs,
            expected_formula="|GHZ> = (|000> + |111>) / sqrt(2)",
            analysis_note="All 3 qubits collapse strictly together to either all zeros (000) or all ones (111)."
        )

    else:
        # Default fallback to Bell State
        return run_predefined_circuit("bell_state", shots)

def run_custom_circuit(
    qubits: int,
    gates: list[GateItem],
    shots: int = 1024,
    circuit_name: str = "Custom Circuit"
) -> CircuitRunResponse:
    """
    Constructs and executes a user-defined custom quantum circuit.
    """
    num_qubits = max(1, min(5, qubits))
    qc = QuantumCircuit(num_qubits, num_qubits)

    py_lines = [
        "from qiskit import QuantumCircuit, transpile",
        "from qiskit_aer import AerSimulator",
        "",
        f"qc = QuantumCircuit({num_qubits}, {num_qubits})"
    ]

    has_explicit_measure = False

    for g in gates:
        q = max(0, min(num_qubits - 1, g.qubit))
        name = g.name.upper()

        if name == "H":
            qc.h(q)
            py_lines.append(f"qc.h({q})")
        elif name == "X":
            qc.x(q)
            py_lines.append(f"qc.x({q})")
        elif name == "Y":
            qc.y(q)
            py_lines.append(f"qc.y({q})")
        elif name == "Z":
            qc.z(q)
            py_lines.append(f"qc.z({q})")
        elif name == "S":
            qc.s(q)
            py_lines.append(f"qc.s({q})")
        elif name == "T":
            qc.t(q)
            py_lines.append(f"qc.t({q})")
        elif name == "I":
            qc.id(q)
            py_lines.append(f"qc.id({q})")
        elif name in ("CX", "CNOT"):
            target = g.target_qubit if g.target_qubit is not None else (q + 1) % num_qubits
            qc.cx(q, target)
            py_lines.append(f"qc.cx({q}, {target})")
        elif name == "CZ":
            target = g.target_qubit if g.target_qubit is not None else (q + 1) % num_qubits
            qc.cz(q, target)
            py_lines.append(f"qc.cz({q}, {target})")
        elif name == "SWAP":
            target = g.target_qubit if g.target_qubit is not None else (q + 1) % num_qubits
            qc.swap(q, target)
            py_lines.append(f"qc.swap({q}, {target})")
        elif name in ("CCX", "TOFFOLI"):
            c1 = q
            c2 = g.control_qubit if g.control_qubit is not None else (q + 1) % num_qubits
            target = g.target_qubit if g.target_qubit is not None else (q + 2) % num_qubits
            qc.ccx(c1, c2, target)
            py_lines.append(f"qc.ccx({c1}, {c2}, {target})")
        elif name == "ROTATION" or name == "RY":
            theta_val = g.param if g.param is not None else math.pi / 4
            qc.ry(theta_val, q)
            py_lines.append(f"qc.ry({theta_val:.4f}, {q})")
        elif name == "RZ":
            phi_val = g.param if g.param is not None else math.pi / 4
            qc.rz(phi_val, q)
            py_lines.append(f"qc.rz({phi_val:.4f}, {q})")
        elif name in ("M", "MEASURE"):
            qc.measure(q, q)
            py_lines.append(f"qc.measure({q}, {q})")
            has_explicit_measure = True
        elif name == "RESET":
            qc.reset(q)
            py_lines.append(f"qc.reset({q})")

    # If user hasn't explicitly added measure gates, measure all qubits
    if not has_explicit_measure:
        qc.measure(range(num_qubits), range(num_qubits))
        py_lines.append(f"qc.measure(range({num_qubits}), range({num_qubits}))")

    py_lines.extend([
        "",
        "sim = AerSimulator()",
        f"counts = sim.run(transpile(qc, sim), shots={shots}).result().get_counts()",
        "print(counts)"
    ])

    simulator = AerSimulator()
    job = simulator.run(transpile(qc, simulator), shots=shots)
    counts = job.result().get_counts()
    probs = {k: round(v / shots, 4) for k, v in sorted(counts.items())}

    ascii_art = qc.draw(output="text").single_string()

    return CircuitRunResponse(
        name=circuit_name,
        description=f"Custom quantum circuit with {num_qubits} qubits and {len(gates)} gates.",
        qubits=num_qubits,
        depth=qc.depth(),
        gate_count=len(qc.data),
        circuit_type="Custom",
        circuit_ascii=ascii_art,
        qiskit_code="\n".join(py_lines),
        counts=counts,
        probabilities=probs,
        expected_formula=f"{num_qubits}-qubit state superposition",
        analysis_note=f"Executed {shots} shots on local Qiskit Aer simulator."
    )
