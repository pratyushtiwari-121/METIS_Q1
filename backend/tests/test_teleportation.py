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
def test_teleportation_fidelity(theta, phi):
    result = compute_teleportation_fidelity(theta, phi, shots=1024)
    fidelity = result["fidelity"]
    assert pytest.approx(fidelity, rel=1e-3) == 1.0
