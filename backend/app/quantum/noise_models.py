"""
Qiskit Aer Noise Models and Quantum Channel Simulation for Attack Vectors.
"""
from qiskit_aer.noise import NoiseModel, depolarizing_error, pauli_error

def create_quantum_channel_noise_model(
    depolarizing_prob: float = 0.0,
    bit_flip_prob: float = 0.0,
    phase_flip_prob: float = 0.0
) -> NoiseModel:
    """
    Constructs a Qiskit Aer NoiseModel simulating physical quantum transmission impairments.
    """
    noise_model = NoiseModel()

    # 1. Depolarizing error (replaces state with maximally mixed state with probability p)
    if depolarizing_prob > 0.0:
        p_dep = min(0.75, max(0.001, depolarizing_prob))
        dep_err = depolarizing_error(p_dep, 1)
        noise_model.add_all_qubit_quantum_error(dep_err, ["ry", "rz", "h", "x", "z", "measure"])

    # 2. Bit flip / Phase flip Pauli errors
    if bit_flip_prob > 0.0 or phase_flip_prob > 0.0:
        px = min(0.5, max(0.0, bit_flip_prob))
        pz = min(0.5, max(0.0, phase_flip_prob))
        py = 0.0
        p_identity = max(0.0, 1.0 - (px + py + pz))
        
        # Guard against sum > 1
        total_p = px + pz + p_identity
        px /= total_p
        pz /= total_p
        p_identity /= total_p

        p_error = pauli_error([('X', px), ('Z', pz), ('I', p_identity)])
        noise_model.add_all_qubit_quantum_error(p_error, ["ry", "rz", "h", "x", "z", "measure"])

    return noise_model
