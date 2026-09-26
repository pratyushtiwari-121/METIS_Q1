export interface ComplexNumber {
  real: number;
  imag: number;
}

export interface StateVectorInfo {
  alpha: ComplexNumber;
  beta: ComplexNumber;
  theta_rad: number;
  theta_deg: number;
  phi_rad: number;
  phi_deg: number;
  prob_0: number;
  prob_1: number;
  state_str: string;
}

export interface SignatureGenerateRequest {
  message: string;
  hash_function?: string;
  encoding_scheme?: string;
  shots?: number;
}

export interface SignatureGenerateResponse {
  signature_id: string;
  message: string;
  message_hash: string;
  binary_hash: string;
  message_length: number;
  state_vector: StateVectorInfo;
  circuit_ascii: string;
  qiskit_code: string;
  measurement_counts: Record<string, number>;
  shots: number;
  fidelity: number;
  classical_bits: string;
  pauli_correction: string;
  timestamp: string;
  status: string;
}

export interface SignatureListItem {
  signature_id: string;
  message_snippet: string;
  hash: string;
  shots: number;
  fidelity: number;
  status: string;
  timestamp: string;
}

export interface BasisVerificationResult {
  basis: string;
  expected: number;
  observed: number;
  deviation: number;
  status: string;
}

export interface VerificationRequest {
  message: string;
  signature_id?: string;
  signature_hex?: string;
  attack_scenario?: string;
  tamper_state?: StateVectorInfo;
  shots?: number;
  threshold?: number;
}

export interface HoeffdingBasisResult {
  basis: string;
  expected_prob: number;
  observed_prob: number;
  shots: number;
  epsilon: number;
  hoeffding_bound: number;
  confidence_pct: number;
  is_anomaly: boolean;
  interpretation: string;
}

export interface ForgerySummary {
  any_anomaly: boolean;
  all_anomaly: boolean;
  summary: string;
  confidence_score: number;
  anomaly_bases: string[];
}

export interface VerificationResponse {
  signature_id: string;
  message: string;
  expected_state: StateVectorInfo;
  reconstructed_state: StateVectorInfo;
  circuit_ascii: string;
  qiskit_code: string;
  expected_distribution: Record<string, number>;
  observed_distribution: Record<string, number>;
  observed_counts: Record<string, number>;
  basis_wise_results: BasisVerificationResult[];
  fidelity: number;
  deviation: number;
  bit_error_rate: number;
  threat_score: number;
  threshold: number;
  decision: string;
  verification_time_ms: number;
  timestamp: string;
  details: string;
  hoeffding_z?: HoeffdingBasisResult;
  hoeffding_x?: HoeffdingBasisResult;
  hoeffding_y?: HoeffdingBasisResult;
  forgery_summary?: ForgerySummary;
  shots?: number;
  purity?: number;
  von_neumann_entropy?: number;
  trace_distance?: number;
  bloch_displacement?: number;
  security_evidence?: Record<string, any>;
}

export interface AttackSimulateRequest {
  attack_type: string;
  signature_id?: string;
  target?: string;
  modification_type?: string;
  attack_intensity?: number;
  noise_level?: number;
  bit_flip_prob?: number;
  depolarizing_noise?: number;
  shots?: number;
  introduce_phase_error?: boolean;
  random_state_replacement?: boolean;
  interception_resend?: boolean;
  attacker_name?: string;
}

export interface AttackSimulateResponse {
  attack_id: number;
  attack_type: string;
  target: string;
  signature_id?: string;
  attack_intensity?: number;
  modification_type?: string;
  original_state: StateVectorInfo;
  tampered_state: StateVectorInfo;
  expected_distribution: Record<string, number>;
  observed_distribution: Record<string, number>;
  observed_counts: Record<string, number>;
  fidelity: number;
  fidelity_change_percent: number;
  deviation: number;
  deviation_change_percent: number;
  threat_score: number;
  threshold: number;
  decision: string;
  alert_message: string;
  flow_steps: Array<{ name: string; status: string }>;
  simulation_logs: Array<{ time: string; event: string; details: string; status: string }>;
  timestamp: string;
  hoeffding_z?: HoeffdingBasisResult;
  hoeffding_x?: HoeffdingBasisResult;
  hoeffding_y?: HoeffdingBasisResult;
  forgery_summary?: ForgerySummary;
  purity?: number;
  von_neumann_entropy?: number;
  trace_distance?: number;
  bloch_displacement?: number;
  security_evidence?: Record<string, any>;
  detector_fired?: string;
  measured_mismatch_rate?: number;
  expected_mismatch?: number;
  empirical_mismatch?: number;
  literature_bound?: string;
}

export interface GateItem {
  name: string;
  qubit: number;
  target_qubit?: number;
  control_qubit?: number;
  control_qubit2?: number;
  param?: number;
}

export interface CustomCircuitRequest {
  name?: string;
  description?: string;
  qubits: number;
  gates: GateItem[];
  shots?: number;
}

export interface PredefinedCircuitRunRequest {
  circuit_name: string;
  shots?: number;
  custom_state_angle?: number;
}

export interface CircuitRunResponse {
  name: string;
  description: string;
  qubits: number;
  depth: number;
  gate_count: number;
  circuit_type: string;
  circuit_ascii: string;
  qiskit_code: string;
  counts: Record<string, number>;
  probabilities: Record<string, number>;
  expected_formula?: string;
  analysis_note: string;
}

export interface SystemResourceMetrics {
  cpu_usage_percent: number;
  memory_usage_percent: number;
  simulation_load_percent: number;
  simulator_status: string;
}

export interface DashboardSummaryResponse {
  total_signatures: number;
  signatures_trend_pct: number;
  verified_count: number;
  verified_success_rate: number;
  detected_attacks: number;
  detection_rate_pct: number;
  system_status: string;
  latest_result?: {
    type: string;
    title: string;
    message_id: string;
    verification_fidelity: number;
    measurement_deviation: number;
    threat_score: string;
    final_decision: string;
    status: string;
    is_threat: boolean;
  };
  measurement_distribution: {
    p0_exp: number;
    p0_obs: number;
    p1_exp: number;
    p1_obs: number;
  };
  threat_trend: Array<{ time: string; legitimate: number; attacks: number }>;
  recent_logs: Array<{ id: number; time: string; event: string; details: string; status: string }>;
  system_resources: SystemResourceMetrics;
}

export interface AnalyticsSummaryResponse {
  total_simulations: number;
  total_signatures: number;
  total_verifications: number;
  total_attacks: number;
  verification_accuracy: number;
  attacks_detected: number;
  avg_verification_time_ms: number;
  detection_rate: number;
  false_positive_rate: number;
  false_negative_rate: number;
  precision: number;
  avg_fidelity: number;
}

export interface TrendPoint {
  time_label: string;
  legitimate_count: number;
  attack_count: number;
  avg_fidelity: number;
  avg_deviation: number;
}

export interface AnalyticsTrendsResponse {
  activity_trend: TrendPoint[];
  attack_type_distribution: Record<string, number>;
  fidelity_distribution: Array<{ range: string; count: number; color: string }>;
  system_load_history: Array<{ time: string; cpu: number; memory: number; simulation_load: number }>;
}

export interface LogItemResponse {
  id: number;
  timestamp: string;
  event_type: string;
  category: string;
  details: string;
  status: string;
  source: string;
  signature_id?: string;
}

export interface LogSummaryStats {
  total_logs: number;
  successful_events: number;
  detected_attacks: number;
  blocked_attempts: number;
  system_events: number;
  unauthorized_access: number;
  events_by_category: Record<string, number>;
}

export interface LogListResponse {
  logs: LogItemResponse[];
  summary: LogSummaryStats;
  page: number;
  page_size: number;
  total_count: number;
}

export interface SystemSettings {
  app_name: string;
  theme: string;
  language: string;
  timezone: string;
  default_shots: number;
  default_qubits: number;
  simulator_backend: string;
  measurement_basis: string;
  verification_threshold: number;
  fidelity_threshold: number;
  max_verification_attempts: number;
  replay_protection: boolean;
  attack_detection_sensitivity: string;
  enable_logging: boolean;
  log_retention_days: number;
  security_alerts: boolean;
  alert_on_attack: boolean;
  alert_on_verification_failure: boolean;
  noise_model_enabled: boolean;
  debug_mode: boolean;
  simulation_seed?: number;
}

// --- Quantum Physics Lab Interfaces ---
export interface TomographyResult {
  shots: number;
  measurements: {
    Z: { counts: Record<string, number>; p0: number; p1: number; observed_expectation: number; theoretical_expectation: number };
    X: { counts: Record<string, number>; p0: number; p1: number; observed_expectation: number; theoretical_expectation: number };
    Y: { counts: Record<string, number>; p0: number; p1: number; observed_expectation: number; theoretical_expectation: number };
  };
  reconstructed_bloch: { x: number; y: number; z: number; length: number };
  theoretical_bloch: { x: number; y: number; z: number; length: number };
  reconstructed_density_matrix: Array<Array<{ real: number; imag: number }>>;
  expected_density_matrix: Array<Array<{ real: number; imag: number }>>;
  fidelity: number;
  trace_distance: number;
  frobenius_residual: number;
  purity_expected: number;
  purity_reconstructed: number;
  entropy_expected: number;
  entropy_reconstructed: number;
  density_matrix_validation: {
    is_valid: boolean;
    is_hermitian: boolean;
    is_unit_trace: boolean;
    is_positive: boolean;
    trace: number;
    eigenvalues: number[];
  };
}

export interface DensityMatrixAnalysis {
  bloch: { x: number; y: number; z: number; length: number };
  density_matrix: Array<Array<{ real: number; imag: number }>>;
  validation: {
    is_valid: boolean;
    is_hermitian: boolean;
    is_unit_trace: boolean;
    is_positive: boolean;
    trace: number;
    eigenvalues: number[];
  };
  purity: number;
  von_neumann_entropy: number;
  pauli_expectations: { X: number; Y: number; Z: number };
  is_pure_state: boolean;
}

export interface ChannelSimulationResult {
  channel_name: string;
  parameter: number;
  initial_state: {
    bloch: { x: number; y: number; z: number; length: number };
    purity: number;
    entropy: number;
    density_matrix: Array<Array<{ real: number; imag: number }>>;
  };
  output_state: {
    bloch: { x: number; y: number; z: number; length: number };
    purity: number;
    entropy: number;
    density_matrix: Array<Array<{ real: number; imag: number }>>;
  };
  metrics: {
    fidelity: number;
    trace_distance: number;
    bloch_displacement: number;
    qber: number;
    purity_drop: number;
    entropy_increase: number;
  };
}

export interface DecoherenceSweepPoint {
  noise_parameter: number;
  fidelity: number;
  purity: number;
  entropy: number;
  trace_distance: number;
  bloch_length: number;
  qber: number;
}

export interface InterceptResendResult {
  eve_active: boolean;
  shots: number;
  expected_distribution: Record<string, number>;
  observed_distribution: Record<string, number>;
  counts: Record<string, number>;
  fidelity: number;
  trace_distance: number;
  tvd: number;
  qber: number;
  entropy_alice: number;
  entropy_bob: number;
  verdict: string;
  eve_stats: {
    bases_used: Record<string, number>;
    collapse_percentage: string;
  };
}

export interface NoCloningResult {
  theorem: string;
  theoretical_maximum_fidelity: number;
  achieved_clone_fidelity: number;
  trace_distance_to_original: number;
  fidelity_gap_due_to_physics: number;
  purity_original: number;
  purity_clone: number;
  entropy_original: number;
  entropy_clone: number;
  security_implication: string;
}

export interface BellStateAnalysis {
  bell_state: string;
  shots: number;
  counts: Record<string, number>;
  probabilities: Record<string, number>;
  correlation: number;
  tvd: number;
  circuit_ascii: string;
  entanglement_quality: string;
}

export interface ChshTestResult {
  shots_per_setting: number;
  total_shots: number;
  angles: { a: number; a_prime: number; b: number; b_prime: number };
  correlations: Record<string, number>;
  chsh_s_value: number;
  classical_bound: number;
  tsirelson_bound: number;
  violates_classical_bound: boolean;
  quantum_violation_margin: number;
  channel_verdict: string;
  disclaimer: string;
}

// ===========================================================================
// QDS Protocol Types (Steps 2-3)
// ===========================================================================

export interface KeyElement {
  position: number;
  basis: 'Z' | 'X' | 'Y';
  bit: number;
  state_label: string;
}

export interface PauliEigenstate {
  position: number;
  basis: 'Z' | 'X' | 'Y';
  bit: number;
  label: string;
  theta: number;
  phi: number;
  bloch: [number, number, number];
  alpha: ComplexNumber;
  beta: ComplexNumber;
}

export interface QDSKeygenRequest {
  length?: number;
  seed?: number;
}

export interface QDSKeygenResponse {
  key_id: string;
  length: number;
  created_at: string;
  public_key_summary: {
    total_states_per_bit: number;
    bases_distribution: Record<string, number>;
  };
  sample_elements: KeyElement[];
}

export interface QDSDistributeRequest {
  key_id: string;
  verifiers?: string[];
  depolarizing_prob?: number;
  bit_flip_prob?: number;
  phase_flip_prob?: number;
  seed?: number;
}

export interface StoredStateSummary {
  position: number;
  bit_label: number;
  original_state_label: string;
  original_basis: string;
  original_bit: number;
  teleportation_outcome: string;
  pauli_correction: string;
  fidelity_with_original: number;
  noise_applied: boolean;
  noise_details: string;
}

export interface VerifierMemorySummary {
  verifier_id: string;
  key_id: string;
  total_states: number;
  avg_fidelity: number;
  states_0?: StoredStateSummary[];
  states_1?: StoredStateSummary[];
}

export interface QDSDistributeResponse {
  key_id: string;
  verifiers: string[];
  total_states_teleported: number;
  teleportation_method: string;
  noise_applied: boolean;
  verifiers_status: Record<string, VerifierMemorySummary>;
}

export interface QDSSignRequest {
  key_id: string;
  message: string;
  bit?: number;
}

export interface QDSSignResponse {
  signature_id: string;
  key_id: string;
  message: string;
  message_hash: string;
  bit: number;
  compact_string: string;
  binding_token: string;
  classical_signature: KeyElement[];
  created_at: string;
}

export interface QDSVerifyRequest {
  key_id: string;
  signature_id?: string;
  message: string;
  bit?: number;
  classical_signature?: KeyElement[];
  compact_string?: string;
  binding_token?: string;
  verifier_id?: string;
  s_a?: number;
  s_v?: number;
  seed?: number;
}

export interface QDSVerifyResponse {
  verifier_id: string;
  key_id: string;
  signature_id: string;
  message: string;
  bit: number;
  total_positions: number;
  mismatch_count: number;
  mismatch_rate: number;
  s_a: number;
  s_v: number;
  decision: string;
  decision_reason: string;
  binding_valid: boolean;
  timestamp: string;
  sample_positions: Array<{
    position: number;
    claimed_basis: string;
    claimed_bit: number;
    observed_bit: number;
    mismatch: boolean;
    prob_0: number;
    prob_1: number;
    original_state_label: string;
  }>;
}

// ===========================================================================
// Step 4: Theoretical Analysis, Sweeps & Performance Types
// ===========================================================================

export interface HoeffdingAssumptionItem {
  id: number;
  name: string;
  details: string;
}

export interface HoeffdingBoundResponse {
  L: number;
  p_e: number;
  p_h: number;
  s_a: number;
  forgery_bound: number;
  false_reject_bound: number;
  forgery_formula: string;
  false_reject_formula: string;
  assumptions: {
    title: string;
    bounds: Record<string, string>;
    assumptions: HoeffdingAssumptionItem[];
  };
}

export interface MonteCarloSimulationRequest {
  L?: number;
  p_e?: number;
  p_h?: number;
  s_a?: number;
  N_trials?: number;
  seed?: number;
}

export interface MonteCarloDetailResult {
  L: number;
  p_e?: number;
  p_h?: number;
  s_a: number;
  N_trials: number;
  seed: number;
  accepted_trials?: number;
  rejected_trials?: number;
  empirical_acceptance_rate?: number;
  empirical_false_reject_rate?: number;
  ci_95_lower: number;
  ci_95_upper: number;
  hoeffding_bound: number;
  bound_holds: boolean;
  empirical_le_bound: boolean;
  mean_sample_mismatch: number;
  std_sample_mismatch: number;
}

export interface MonteCarloSimulationResponse {
  forgery: MonteCarloDetailResult;
  false_reject: MonteCarloDetailResult;
  empirical_rate_le_bound: boolean;
  summary: string;
}

export interface AerValidationResponse {
  status: string;
  L: number;
  aer_honest_mismatch_rate: number;
  numpy_honest_mismatch_rate: number;
  aer_adversary_mismatch_rate: number;
  numpy_adversary_sample: number;
  total_variation_distance: number;
  shots: number;
  is_valid: boolean;
  note: string;
}

export interface SweepPointVsL {
  L: number;
  hoeffding_bound: number;
  empirical_rate: number;
  ci_95_lower: number;
  ci_95_upper: number;
  bound_holds: boolean;
}

export interface SweepPointVsThreshold {
  s_a: number;
  hoeffding_bound: number;
  empirical_rate: number;
  ci_95_lower: number;
  ci_95_upper: number;
  bound_holds: boolean;
}

export interface SweepPointVsStrategy {
  L: number;
  random_guess_bound: number;
  random_guess_empirical: number;
  single_basis_bound: number;
  single_basis_empirical: number;
  optimal_povm_bound: number;
  optimal_povm_empirical: number;
}

export interface SweepPointVsNoise {
  p_h: number;
  hoeffding_bound: number;
  empirical_rate: number;
  ci_95_lower: number;
  ci_95_upper: number;
  bound_holds: boolean;
}

export interface RocCurvePoint {
  s_a: number;
  fpr: number;
  tpr: number;
  forgery_bound: number;
  false_reject_bound: number;
}

export interface SweepsResponse {
  sweep_vs_L: SweepPointVsL[];
  sweep_vs_threshold: SweepPointVsThreshold[];
  sweep_vs_strategy: SweepPointVsStrategy[];
  sweep_vs_noise: SweepPointVsNoise[];
  roc_curve: {
    L: number;
    p_e: number;
    p_h: number;
    auc: number;
    curve_points: RocCurvePoint[];
  };
  assumptions: {
    title: string;
    bounds: Record<string, string>;
    assumptions: HoeffdingAssumptionItem[];
  };
}

export interface BenchmarkPointL {
  L: number;
  keygen_time_ms: number;
  signing_time_ms: number;
  verify_time_ms: number;
  total_protocol_time_ms: number;
  peak_memory_kb: number;
}

export interface BenchmarkPointK {
  num_verifiers: number;
  distribution_time_ms: number;
  distribution_time_per_verifier_ms: number;
}

export interface PerformanceBenchmarkResponse {
  benchmarks_by_L: BenchmarkPointL[];
  benchmarks_by_K: BenchmarkPointK[];
  complexity_analysis: {
    theoretical_complexity: string;
    empirical_scaling_status: string;
    verification_r2: number;
    signing_r2: number;
    verification_slope_ms_per_qubit: number;
    verification_intercept_ms: number;
  };
  system_info: {
    iterations_per_point: number;
    memory_tracker: string;
    timer: string;
  };
}

export interface AttackPerformanceDetail {
  true_positives: number;
  false_negatives: number;
  detection_recall: number;
  samples_tested: number;
}

export interface ConfusionMatrixResponse {
  status: string;
  sample_size: {
    honest_trials: number;
    attack_trials_total: number;
    total_runs: number;
  };
  confusion_matrix: {
    true_positives: number;
    false_positives: number;
    true_negatives: number;
    false_negatives: number;
  };
  metrics: {
    accuracy_percent: number;
    precision_percent: number;
    recall_percent: number;
    specificity_percent: number;
    f1_score: number;
  };
  per_attack_performance: Record<string, AttackPerformanceDetail>;
  mean_honest_mismatch: number;
  parameters: {
    L: number;
    s_a: number;
    s_v: number;
  };
}
