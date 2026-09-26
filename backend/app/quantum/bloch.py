"""
Bloch sphere coordinate calculations and vector projections.
"""
import math

def angles_to_bloch_coordinates(theta_rad: float, phi_rad: float) -> dict[str, float]:
    """
    Computes Cartesian coordinates (x, y, z) on the unit Bloch sphere.
    x = sin(theta) * cos(phi)
    y = sin(theta) * sin(phi)
    z = cos(theta)
    """
    x = math.sin(theta_rad) * math.cos(phi_rad)
    y = math.sin(theta_rad) * math.sin(phi_rad)
    z = math.cos(theta_rad)

    return {
        "x": round(float(x), 4),
        "y": round(float(y), 4),
        "z": round(float(z), 4),
        "length": round(float(math.sqrt(x * x + y * y + z * z)), 4)
    }


def compute_bloch_displacement(
    vec1: dict[str, float],
    vec2: dict[str, float]
) -> float:
    """
    Computes Euclidean distance between two Bloch vectors:
        D_Bloch = √((dx)² + (dy)² + (dz)²)
    Range: [0.0, 2.0]
      0.0 → identical states
      2.0 → antipodal (orthogonal) states on the Bloch sphere
    Used as a physical diagnostic indicator.
    """
    dx = vec1.get("x", 0.0) - vec2.get("x", 0.0)
    dy = vec1.get("y", 0.0) - vec2.get("y", 0.0)
    dz = vec1.get("z", 0.0) - vec2.get("z", 0.0)
    dist = math.sqrt(dx * dx + dy * dy + dz * dz)
    return round(float(min(2.0, max(0.0, dist))), 4)

