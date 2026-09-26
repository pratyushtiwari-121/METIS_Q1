import pytest
from app.quantum.teleportation import compute_teleportation_fidelity

@pytest.mark.parametrize(
    "theta,phi",
    [
        (0.0, 0.0),               # |0>
        (3.1415926535, 0.0),      # |1>
        (1.5707963268, 0.0),      # |+>
        (1.5707963268, 3.1415926535),  # |->
        (0.927295218, 0.7853981634),   # random Bloch state
    ]
)
def test_corrected_fidelity_approx_one(theta, phi):
    result = compute_teleportation_fidelity(theta, phi, shots=1024, apply_correction=True)
    fidelity = result["fidelity"]
    assert pytest.approx(fidelity, rel=1e-2) == 1.0

def test_uncorrected_fidelity_lower_than_corrected():
    theta, phi = 0.927295218, 0.7853981634
    corrected = compute_teleportation_fidelity(theta, phi, shots=2048, apply_correction=True)["fidelity"]
    uncorrected = compute_teleportation_fidelity(theta, phi, shots=2048, apply_correction=False)["fidelity"]
    assert uncorrected < corrected

def test_noisy_fidelity_lower_than_corrected():
    from app.quantum.noise_models import create_quantum_channel_noise_model
    theta, phi = 0.927295218, 0.7853981634
    noise = create_quantum_channel_noise_model(depolarizing_prob=0.02)
    corrected = compute_teleportation_fidelity(theta, phi, shots=2048, apply_correction=True)["fidelity"]
    noisy = compute_teleportation_fidelity(theta, phi, shots=2048, apply_correction=True, noise_model=noise)["fidelity"]
    assert noisy < corrected
