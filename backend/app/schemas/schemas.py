from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime

# --- Quantum State Schemas ---
class ComplexNumber(BaseModel):
    real: float
    imag: float

class StateVectorInfo(BaseModel):
    alpha: ComplexNumber
    beta: ComplexNumber
    theta_rad: float
    theta_deg: float
    phi_rad: float
    phi_deg: float
    prob_0: float
    prob_1: float
    state_str: str

# --- Signature Generation Schemas ---
class SignatureGenerateRequest(BaseModel):
    message: str = Field(..., max_length=500, description="Message string to sign")
    hash_function: str = Field(default="SHA-256")
    encoding_scheme: str = Field(default="Amplitude Encoding")
    shots: int = Field(default=1024, ge=100, le=8192)

class SignatureGenerateResponse(BaseModel):
    signature_id: str
    message: str
    message_hash: str
    binary_hash: str
    message_length: int
    state_vector: StateVectorInfo
    circuit_ascii: str
    qiskit_code: str
    measurement_counts: dict[str, int]
    shots: int
    fidelity: float
    classical_bits: str
    pauli_correction: str
    timestamp: str
    status: str

class SignatureListItem(BaseModel):
    signature_id: str
    message_snippet: str
    hash: str
    shots: int
    fidelity: float
    status: str
    timestamp: str

# --- Verification Schemas ---
class VerificationRequest(BaseModel):
    message: str
    signature_id: Optional[str] = None
    signature_hex: Optional[str] = None
    attack_scenario: Optional[str] = None  # None, "tampered_message", "bit_flip", "phase_flip", "random_state", "forgery"
    tamper_state: Optional[StateVectorInfo] = None
    shots: int = Field(default=1024, ge=100, le=8192)
    threshold: Optional[float] = Field(default=None)

class BasisVerificationResult(BaseModel):
    basis: str
    expected: float
    observed: float
    deviation: float
    status: str

class HoeffdingBasisResult(BaseModel):
    """Hoeffding inequality result for a single measurement basis."""
    basis: str
    expected_prob: float
    observed_prob: float
    shots: int
    epsilon: float
    hoeffding_bound: float
    confidence_pct: float
    is_anomaly: bool
    interpretation: str

class ForgerySummary(BaseModel):
    """Aggregate forgery/anomaly estimation across all three bases."""
    any_anomaly: bool
    all_anomaly: bool
    anomaly_bases: list[str]
    summary: str

class VerificationResponse(BaseModel):
    signature_id: str
    message: str
    expected_state: StateVectorInfo
    reconstructed_state: StateVectorInfo
    circuit_ascii: str
    qiskit_code: str
    expected_distribution: dict[str, float]
    observed_distribution: dict[str, float]
    observed_counts: dict[str, int]
    basis_wise_results: list[BasisVerificationResult]
    fidelity: float
    deviation: float
    bit_error_rate: float
    threat_score: float
    threshold: float
    decision: str  # "LEGITIMATE", "ATTACK DETECTED", "INVALID"
    verification_time_ms: float
    timestamp: str
    details: str
    # --- Statistical Analysis Fields (FIX 3, 4) ---
    hoeffding_z: Optional[HoeffdingBasisResult] = None
    hoeffding_x: Optional[HoeffdingBasisResult] = None
    hoeffding_y: Optional[HoeffdingBasisResult] = None
    forgery_summary: Optional[ForgerySummary] = None
    shots: int = 1024
    # --- Physical Quantum Metrics ---
    purity: Optional[float] = None
    von_neumann_entropy: Optional[float] = None
    trace_distance: Optional[float] = None
    bloch_displacement: Optional[float] = None
    security_evidence: Optional[dict[str, Any]] = None

# --- Attack Simulation Schemas ---
class AttackSimulateRequest(BaseModel):
    attack_type: str = Field(..., description="No Attack, Forgery Attack, Impersonation Attack, Replay Attack, Channel Manipulation, Unauthorized Verification")
    signature_id: Optional[str] = None
    key_id: Optional[str] = None
    target: str = Field(default="Signature", description="Signature, Message, Both")
    modification_type: str = Field(default="Alter Quantum State (Bit Flip)")
    attack_intensity: float = Field(default=0.5, ge=0.0, le=1.0)
    noise_level: float = Field(default=0.0, ge=0.0, le=1.0)
    bit_flip_prob: float = Field(default=0.3, ge=0.0, le=1.0)
    depolarizing_noise: float = Field(default=0.0, ge=0.0, le=1.0)
    shots: int = Field(default=1024, ge=100, le=8192)
    introduce_phase_error: bool = Field(default=False)
    random_state_replacement: bool = Field(default=False)
    interception_resend: bool = Field(default=False)
    attacker_name: Optional[str] = "Eve (Unauthorized Actor)"
    qds_strategy: Optional[str] = "multi_basis"
    nonce: Optional[str] = None
    verifier_id: Optional[str] = "Bob"
    auth_token: Optional[str] = None
    client_id: Optional[str] = "client_default"

class AttackSimulateResponse(BaseModel):
    attack_id: int
    attack_type: str
    target: str
    signature_id: Optional[str]
    original_state: StateVectorInfo
    tampered_state: StateVectorInfo
    expected_distribution: dict[str, float]
    observed_distribution: dict[str, float]
    observed_counts: dict[str, int]
    fidelity: float
    fidelity_change_percent: float
    deviation: float
    deviation_change_percent: float
    threat_score: float
    threshold: float
    decision: str
    alert_message: str
    flow_steps: list[dict[str, str]]
    simulation_logs: list[dict[str, str]]
    timestamp: str
    # --- Statistical Analysis Fields ---
    hoeffding_z: Optional[HoeffdingBasisResult] = None
    hoeffding_x: Optional[HoeffdingBasisResult] = None
    hoeffding_y: Optional[HoeffdingBasisResult] = None
    forgery_summary: Optional[ForgerySummary] = None
    # --- Physical Quantum Metrics ---
    purity: Optional[float] = None
    von_neumann_entropy: Optional[float] = None
    trace_distance: Optional[float] = None
    bloch_displacement: Optional[float] = None
    security_evidence: Optional[dict[str, Any]] = None
    # --- QDS Step 3 Adversary Fields ---
    detector_fired: Optional[str] = None  # "threshold", "nonce", "rate-limit", "authorization"
    measured_mismatch_rate: Optional[float] = None
    empirical_mismatch: Optional[float] = None
    expected_mismatch: Optional[float] = None
    literature_bound: Optional[str] = None
    qds_details: Optional[dict[str, Any]] = None

# --- Quantum Circuit Schemas ---
class GateItem(BaseModel):
    name: str  # "H", "X", "Y", "Z", "S", "T", "I", "CX", "CZ", "SWAP", "CCX", "M", "RESET"
    qubit: int
    target_qubit: Optional[int] = None
    control_qubit: Optional[int] = None
    control_qubit2: Optional[int] = None
    param: Optional[float] = None  # for rotation gates

class CustomCircuitRequest(BaseModel):
    name: str = "Custom Circuit"
    description: Optional[str] = "User created quantum circuit"
    qubits: int = Field(default=2, ge=1, le=5)
    gates: list[GateItem] = []
    shots: int = Field(default=1024, ge=100, le=8192)

class PredefinedCircuitRunRequest(BaseModel):
    circuit_name: str = Field(..., description="bell_state, superposition, teleportation, bit_flip, phase_flip, entanglement, signature_gen, signature_verify")
    shots: int = Field(default=1024, ge=100, le=8192)
    custom_state_angle: Optional[float] = None

class CircuitRunResponse(BaseModel):
    name: str
    description: str
    qubits: int
    depth: int
    gate_count: int
    circuit_type: str
    circuit_ascii: str
    qiskit_code: str
    counts: dict[str, int]
    probabilities: dict[str, float]
    state_vector: Optional[list[ComplexNumber]] = None
    qubit_bloch_vectors: Optional[list[StateVectorInfo]] = None
    expected_formula: Optional[str] = None
    analysis_note: str

# --- Analytics Schemas ---
class AnalyticsSummaryResponse(BaseModel):
    total_simulations: int
    total_signatures: int
    total_verifications: int
    total_attacks: int
    verification_accuracy: float
    attacks_detected: int
    avg_verification_time_ms: float
    detection_rate: float
    false_positive_rate: float
    false_negative_rate: float
    precision: float
    avg_fidelity: float

class TrendPoint(BaseModel):
    time_label: str
    legitimate_count: int
    attack_count: int
    avg_fidelity: float
    avg_deviation: float

class AnalyticsTrendsResponse(BaseModel):
    activity_trend: list[TrendPoint]
    attack_type_distribution: dict[str, int]
    fidelity_distribution: list[dict[str, Any]]
    system_load_history: list[dict[str, Any]]

# --- Dashboard Schemas ---
class SystemResourceMetrics(BaseModel):
    cpu_usage_percent: float
    memory_usage_percent: float
    simulation_load_percent: float
    simulator_status: str

class DashboardSummaryResponse(BaseModel):
    total_signatures: int
    signatures_trend_pct: float
    verified_count: int
    verified_success_rate: float
    detected_attacks: int
    detection_rate_pct: float
    system_status: str
    latest_result: Optional[dict[str, Any]]
    measurement_distribution: dict[str, Any]
    threat_trend: list[dict[str, Any]]
    recent_logs: list[dict[str, Any]]
    system_resources: SystemResourceMetrics

# --- Logs Schemas ---
class LogItemResponse(BaseModel):
    id: int
    timestamp: str
    event_type: str
    category: str
    details: str
    status: str
    source: str
    signature_id: Optional[str]

class LogSummaryStats(BaseModel):
    total_logs: int
    successful_events: int
    detected_attacks: int
    blocked_attempts: int
    system_events: int
    unauthorized_access: int
    events_by_category: dict[str, int]

class LogListResponse(BaseModel):
    logs: list[LogItemResponse]
    summary: LogSummaryStats
    page: int
    page_size: int
    total_count: int

# --- Settings Schemas ---
class SystemSettings(BaseModel):
    app_name: str = "Quantum Digital Signature Security"
    theme: str = "dark-quantum"
    language: str = "en"
    timezone: str = "Asia/Kolkata"
    default_shots: int = 1024
    default_qubits: int = 2
    simulator_backend: str = "Qiskit Aer Simulator (Local)"
    measurement_basis: str = "Computational (Z-basis)"
    verification_threshold: float = 0.100
    fidelity_threshold: float = 0.850
    max_verification_attempts: int = 5
    replay_protection: bool = True
    attack_detection_sensitivity: str = "High"
    enable_logging: bool = True
    log_retention_days: int = 30
    security_alerts: bool = True
    alert_on_attack: bool = True
    alert_on_verification_failure: bool = True
    noise_model_enabled: bool = False
    debug_mode: bool = False
    simulation_seed: Optional[int] = 42

# --- Quantum Physics Lab Schemas ---
class TomographyRequest(BaseModel):
    theta: float = Field(default=1.2, description="State theta angle in radians")
    phi: float = Field(default=0.8, description="State phi angle in radians")
    shots: int = Field(default=1024, ge=100, le=8192)

class DensityMatrixAnalysisRequest(BaseModel):
    theta: float = Field(default=1.0)
    phi: float = Field(default=0.5)

class ChannelSimulationRequest(BaseModel):
    channel_name: str = Field(default="depolarizing", description="bit_flip, phase_flip, bit_phase_flip, depolarizing, amplitude_damping, phase_damping")
    theta: float = Field(default=1.0)
    phi: float = Field(default=0.5)
    parameter: float = Field(default=0.2, ge=0.0, le=1.0, description="Noise parameter p / gamma / lambda")

class DecoherenceSweepRequest(BaseModel):
    channel_name: str = Field(default="depolarizing")
    theta: float = Field(default=1.0)
    phi: float = Field(default=0.5)
    steps: int = Field(default=21, ge=5, le=51)

class InterceptResendRequest(BaseModel):
    theta: float = Field(default=1.2)
    phi: float = Field(default=0.8)
    shots: int = Field(default=1024, ge=100, le=8192)
    eve_active: bool = Field(default=True)

class NoCloningRequest(BaseModel):
    theta: float = Field(default=1.0)
    phi: float = Field(default=0.5)

class BellStateRequest(BaseModel):
    bell_type: str = Field(default="phi_plus", description="phi_plus, phi_minus, psi_plus, psi_minus")
    shots: int = Field(default=2048, ge=100, le=8192)

class ChshTestRequest(BaseModel):
    shots: int = Field(default=2048, ge=100, le=8192)
    noise_level: float = Field(default=0.0, ge=0.0, le=1.0)


# --- Quantum Digital Signature (QDS Step 2) Schemas ---
class QDSKeygenRequest(BaseModel):
    length: int = Field(default=32, ge=4, le=512, description="Length L of Pauli-eigenstate sequence per bit")
    seed: Optional[int] = Field(default=None, description="Optional seed for deterministic generation")

class QDSKeygenResponse(BaseModel):
    key_id: str
    length: int
    created_at: str
    public_key_summary: dict[str, Any]
    private_key_preview: list[dict[str, Any]]

class QDSDistributeRequest(BaseModel):
    key_id: str = Field(..., description="Key ID to distribute")
    verifiers: list[str] = Field(default=["Bob", "Charlie"], description="Verifiers receiving public key states")
    depolarizing_prob: float = Field(default=0.0, ge=0.0, le=1.0)
    bit_flip_prob: float = Field(default=0.0, ge=0.0, le=1.0)
    phase_flip_prob: float = Field(default=0.0, ge=0.0, le=1.0)
    seed: Optional[int] = None

class QDSDistributeResponse(BaseModel):
    key_id: str
    verifiers: list[str]
    total_states_teleported: int
    teleportation_method: str = "EPR Bell Pairs + Feed-Forward Pauli Correction"
    noise_applied: bool
    verifiers_status: dict[str, Any]

class QDSSignRequest(BaseModel):
    key_id: str = Field(..., description="Key ID used for signing")
    message: str = Field(..., description="Plaintext message payload")
    bit: int = Field(default=0, ge=0, le=1, description="Message bit being signed (0 or 1)")

class QDSSignResponse(BaseModel):
    signature_id: str
    key_id: str
    message: str
    message_hash: str
    bit: int
    compact_string: str
    binding_token: str
    classical_signature: list[dict[str, Any]]
    created_at: str

class QDSVerifyRequest(BaseModel):
    key_id: str = Field(..., description="Key ID used for verification")
    signature_id: Optional[str] = Field(default=None, description="Signature ID if saved, or pass explicit payload")
    message: str = Field(..., description="Plaintext message payload to verify")
    bit: int = Field(default=0, ge=0, le=1, description="Message bit being verified")
    classical_signature: Optional[list[dict[str, Any]]] = None
    compact_string: Optional[str] = None
    binding_token: Optional[str] = None
    verifier_id: str = Field(default="Bob", description="Verifier identifier (e.g. 'Bob' or 'Charlie')")
    s_a: Optional[float] = Field(default=0.10, ge=0.0, lt=0.5, description="Acceptance threshold (default 0.10)")
    s_v: Optional[float] = Field(default=0.25, gt=0.0, lt=0.5, description="Rejection threshold (default 0.25)")
    seed: Optional[int] = None

class QDSVerifyResponse(BaseModel):
    verifier_id: str
    key_id: str
    signature_id: str
    message: str
    bit: int
    total_positions: int
    mismatch_count: int
    mismatch_rate: float
    s_a: float
    s_v: float
    decision: str
    decision_reason: str
    binding_valid: bool
    timestamp: str
    sample_positions: list[dict[str, Any]]


# ===========================================================================
# Step 4: Theoretical Analysis, Monte Carlo & Performance Schemas
# ===========================================================================

class HoeffdingBoundResponse(BaseModel):
    L: int
    p_e: float
    p_h: float
    s_a: float
    forgery_bound: float
    false_reject_bound: float
    forgery_formula: str
    false_reject_formula: str
    assumptions: dict[str, Any]

class MonteCarloSimulationRequest(BaseModel):
    L: int = Field(default=64, ge=1, le=4096, description="Key length / qubit copies")
    p_e: float = Field(default=0.3333, ge=0.0, le=1.0, description="Adversary per-copy mismatch rate")
    p_h: float = Field(default=0.02, ge=0.0, le=1.0, description="Honest channel error rate")
    s_a: float = Field(default=0.10, ge=0.0, lt=0.5, description="Acceptance threshold")
    N_trials: int = Field(default=10000, ge=100, le=100000, description="Number of Monte Carlo iterations")
    seed: Optional[int] = Field(default=42, description="RNG seed for reproducibility")

class MonteCarloSimulationResponse(BaseModel):
    forgery: dict[str, Any]
    false_reject: dict[str, Any]
    empirical_rate_le_bound: bool
    summary: str

class AerValidationResponse(BaseModel):
    status: str
    L: int
    aer_honest_mismatch_rate: float
    numpy_honest_mismatch_rate: float
    aer_adversary_mismatch_rate: float
    numpy_adversary_sample: float
    total_variation_distance: float
    shots: int
    is_valid: bool
    note: str

class SweepsResponse(BaseModel):
    sweep_vs_L: list[dict[str, Any]]
    sweep_vs_threshold: list[dict[str, Any]]
    sweep_vs_strategy: list[dict[str, Any]]
    sweep_vs_noise: list[dict[str, Any]]
    roc_curve: dict[str, Any]
    assumptions: dict[str, Any]

class PerformanceBenchmarkResponse(BaseModel):
    benchmarks_by_L: list[dict[str, Any]]
    benchmarks_by_K: list[dict[str, Any]]
    complexity_analysis: dict[str, Any]
    system_info: dict[str, Any]

class ConfusionMatrixResponse(BaseModel):
    status: str
    sample_size: dict[str, Any]
    confusion_matrix: dict[str, Any]
    metrics: dict[str, Any]
    per_attack_performance: dict[str, Any]
    mean_honest_mismatch: float
    parameters: dict[str, Any]



