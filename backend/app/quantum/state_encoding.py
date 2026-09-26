"""
Deterministic mapping from message SHA-256 hash to quantum state parameters.
"""
import hashlib
import cmath
import math
import numpy as np
from app.schemas.schemas import StateVectorInfo, ComplexNumber

def compute_sha256(message: str) -> tuple[str, str]:
    """
    Returns (hex_digest, binary_representation)
    """
    digest_bytes = hashlib.sha256(message.encode("utf-8")).digest()
    hex_digest = digest_bytes.hex()
    bin_digest = "".join(f"{b:08b}" for b in digest_bytes)
    return hex_digest, bin_digest

def hash_to_quantum_state(hex_hash: str) -> StateVectorInfo:
    """
    [LEGACY DEMO, NOT CRYPTOGRAPHICALLY SECURE]
    Replaced by Pauli-eigenstate QDS in backend/app/qds/.

    Deterministically transforms a 64-character (256-bit) SHA-256 hex string
    into valid normalized single-qubit quantum state parameters for educational demonstration.

    Mathematical mapping:
    - Bytes 0..3 (32 bits) -> integer u1 -> theta in [0.25, pi - 0.25] rad
      (bounded away from pure poles to demonstrate full superposition and Bloch sphere visualization)
    - Bytes 4..7 (32 bits) -> integer u2 -> phi in [0, 2*pi) rad
    - State: |psi> = cos(theta/2)|0> + e^(i*phi)*sin(theta/2)|1>
      where |alpha|^2 + |beta|^2 = 1.0
    """
    # Extract 32-bit integers from the hash
    chunk1 = int(hex_hash[0:8], 16)
    chunk2 = int(hex_hash[8:16], 16)
    max_32 = 0xFFFFFFFF

    # Map chunk1 to theta in [0.25, math.pi - 0.25]
    # This guarantees a non-trivial superposition showcasing quantum properties
    norm1 = chunk1 / max_32
    theta = 0.25 + norm1 * (math.pi - 0.50)
    
    # Map chunk2 to phi in [0, 2*pi)
    norm2 = chunk2 / max_32
    phi = norm2 * 2.0 * math.pi

    # Calculate amplitudes
    alpha_val = math.cos(theta / 2.0)
    # beta = exp(i * phi) * sin(theta / 2.0)
    sin_half = math.sin(theta / 2.0)
    beta_complex = sin_half * cmath.exp(1j * phi)

    alpha_real = float(alpha_val)
    alpha_imag = 0.0
    beta_real = float(beta_complex.real)
    beta_imag = float(beta_complex.imag)

    prob_0 = float(alpha_real**2 + alpha_imag**2)
    prob_1 = float(beta_real**2 + beta_imag**2)

    # Normalize if floating rounding causes slight drift
    total_p = prob_0 + prob_1
    prob_0 = round(prob_0 / total_p, 4)
    prob_1 = round(prob_1 / total_p, 4)

    theta_deg = round(math.degrees(theta), 2)
    phi_deg = round(math.degrees(phi), 2)

    # Human readable state string: e.g. "0.815|0> + (0.408 + 0.408i)|1>"
    if abs(beta_imag) < 1e-4:
        beta_str = f"{beta_real:+.4f}|1>"
    else:
        sign = "+" if beta_imag >= 0 else "-"
        beta_str = f"({beta_real:.4f} {sign} {abs(beta_imag):.4f}i)|1>"

    state_str = f"{alpha_real:.4f}|0> + {beta_str}"

    return StateVectorInfo(
        alpha=ComplexNumber(real=round(alpha_real, 4), imag=round(alpha_imag, 4)),
        beta=ComplexNumber(real=round(beta_real, 4), imag=round(beta_imag, 4)),
        theta_rad=round(theta, 4),
        theta_deg=theta_deg,
        phi_rad=round(phi, 4),
        phi_deg=phi_deg,
        prob_0=prob_0,
        prob_1=prob_1,
        state_str=state_str
    )

def state_info_from_angles(theta: float, phi: float) -> StateVectorInfo:
    """Reconstructs StateVectorInfo from theta and phi angles."""
    alpha_val = math.cos(theta / 2.0)
    sin_half = math.sin(theta / 2.0)
    beta_complex = sin_half * cmath.exp(1j * phi)

    alpha_real = float(alpha_val)
    alpha_imag = 0.0
    beta_real = float(beta_complex.real)
    beta_imag = float(beta_complex.imag)

    prob_0 = round(alpha_real**2, 4)
    prob_1 = round(beta_real**2 + beta_imag**2, 4)

    theta_deg = round(math.degrees(theta), 2)
    phi_deg = round(math.degrees(phi), 2)

    if abs(beta_imag) < 1e-4:
        beta_str = f"{beta_real:+.4f}|1>"
    else:
        sign = "+" if beta_imag >= 0 else "-"
        beta_str = f"({beta_real:.4f} {sign} {abs(beta_imag):.4f}i)|1>"

    state_str = f"{alpha_real:.4f}|0> + {beta_str}"

    return StateVectorInfo(
        alpha=ComplexNumber(real=round(alpha_real, 4), imag=round(alpha_imag, 4)),
        beta=ComplexNumber(real=round(beta_real, 4), imag=round(beta_imag, 4)),
        theta_rad=round(theta, 4),
        theta_deg=theta_deg,
        phi_rad=round(phi, 4),
        phi_deg=phi_deg,
        prob_0=prob_0,
        prob_1=prob_1,
        state_str=state_str
    )
