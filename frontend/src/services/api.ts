import type {
  DashboardSummaryResponse,
  SignatureGenerateRequest,
  SignatureGenerateResponse,
  SignatureListItem,
  VerificationRequest,
  VerificationResponse,
  AttackSimulateRequest,
  AttackSimulateResponse,
  PredefinedCircuitRunRequest,
  CustomCircuitRequest,
  CircuitRunResponse,
  AnalyticsSummaryResponse,
  AnalyticsTrendsResponse,
  LogListResponse,
  SystemSettings,
  TomographyResult,
  DensityMatrixAnalysis,
  ChannelSimulationResult,
  BellStateAnalysis,
  ChshTestResult,
  DecoherenceSweepPoint,
  InterceptResendResult,
  NoCloningResult,
  QDSKeygenRequest,
  QDSKeygenResponse,
  QDSDistributeRequest,
  QDSDistributeResponse,
  QDSSignRequest,
  QDSSignResponse,
  QDSVerifyRequest,
  QDSVerifyResponse,
  HoeffdingBoundResponse,
  MonteCarloSimulationRequest,
  MonteCarloSimulationResponse,
  AerValidationResponse,
  SweepsResponse,
  PerformanceBenchmarkResponse,
  ConfusionMatrixResponse
} from '../types';

/**
 * API base URL resolution:
 *  - Development: VITE_API_BASE_URL unset → '/api' → proxied by Vite to http://127.0.0.1:8000
 *  - Production (Vercel): set VITE_API_BASE_URL in Vercel project env vars to your
 *    backend URL, e.g. https://your-backend.onrender.com/api
 *    Without it the frontend shows an offline/simulator-mode banner.
 */
const API_BASE: string =
  (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(/\/$/, '') ?? '/api';

/** True when a backend URL was explicitly configured at build time. */
export const isBackendConfigured: boolean =
  typeof import.meta.env.VITE_API_BASE_URL === 'string' &&
  import.meta.env.VITE_API_BASE_URL.trim().length > 0;

/** Ping /api/health. Returns true if backend is reachable. */
export async function checkBackendHealth(): Promise<boolean> {
  try {
    const healthUrl = isBackendConfigured
      ? `${API_BASE}/health`
      : '/api/health';
    const res = await fetch(healthUrl, { method: 'GET' });
    return res.ok;
  } catch {
    return false;
  }
}

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers
      },
      ...options
    });
  } catch (networkErr: unknown) {
    // Network-level failure (backend unreachable)
    throw new Error(
      'Backend unreachable — the API server is not running or not yet deployed. ' +
      'The simulator is running in offline mode.'
    );
  }

  if (!res.ok) {
    let errorMsg = `HTTP ${res.status}: ${res.statusText}`;
    try {
      const errData = await res.json();
      if (errData.detail) errorMsg = errData.detail;
    } catch {
      // ignore JSON parse failures
    }
    throw new Error(errorMsg);
  }

  return res.json();
}

export const api = {
  // Dashboard
  getDashboardSummary: () => fetchJson<DashboardSummaryResponse>(`${API_BASE}/dashboard/summary`),

  // Signatures
  generateSignature: (data: SignatureGenerateRequest) =>
    fetchJson<SignatureGenerateResponse>(`${API_BASE}/signatures/generate`, {
      method: 'POST',
      body: JSON.stringify(data)
    }),
  listSignatures: (limit?: number) =>
    fetchJson<SignatureListItem[]>(`${API_BASE}/signatures${limit ? `?limit=${limit}` : ''}`),
  getSignature: (id: string) => fetchJson<any>(`${API_BASE}/signatures/${id}`),

  // Verification
  verifySignature: (data: VerificationRequest) =>
    fetchJson<VerificationResponse>(`${API_BASE}/verification/verify`, {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  // Attacks
  simulateAttack: (data: AttackSimulateRequest) =>
    fetchJson<AttackSimulateResponse>(`${API_BASE}/attacks/simulate`, {
      method: 'POST',
      body: JSON.stringify(data)
    }),
  listAttacks: () => fetchJson<any[]>(`${API_BASE}/attacks`),

  // Quantum Circuits
  runPredefinedCircuit: (data: PredefinedCircuitRunRequest) =>
    fetchJson<CircuitRunResponse>(`${API_BASE}/quantum/circuit/predefined`, {
      method: 'POST',
      body: JSON.stringify(data)
    }),
  runCustomCircuit: (data: CustomCircuitRequest) =>
    fetchJson<CircuitRunResponse>(`${API_BASE}/quantum/circuit/run`, {
      method: 'POST',
      body: JSON.stringify(data)
    }),
  listSavedCircuits: () => fetchJson<any[]>(`${API_BASE}/quantum/circuits`),

  // Analytics
  getAnalyticsSummary: () => fetchJson<AnalyticsSummaryResponse>(`${API_BASE}/analytics/summary`),
  getAnalyticsTrends: () => fetchJson<AnalyticsTrendsResponse>(`${API_BASE}/analytics/trends`),

  // Logs
  getLogs: (params?: { category?: string; status?: string; search?: string; page?: number; pageSize?: number }) => {
    const query = new URLSearchParams();
    if (params?.category) query.set('category', params.category);
    if (params?.status) query.set('status', params.status);
    if (params?.search) query.set('search', params.search);
    if (params?.page) query.set('page', params.page.toString());
    if (params?.pageSize) query.set('page_size', params.pageSize.toString());
    return fetchJson<LogListResponse>(`${API_BASE}/logs?${query.toString()}`);
  },
  getExportLogsUrl: () => `${API_BASE}/logs/export`,

  // Settings
  getSettings: () => fetchJson<SystemSettings>(`${API_BASE}/settings`),
  updateSettings: (data: SystemSettings) =>
    fetchJson<SystemSettings>(`${API_BASE}/settings`, {
      method: 'PUT',
      body: JSON.stringify(data)
    }),
  resetSettings: () =>
    fetchJson<SystemSettings>(`${API_BASE}/settings/reset`, {
      method: 'POST'
    }),

  // Physics Lab
  runTomography: (data: { theta: number; phi: number; shots?: number }) =>
    fetchJson<TomographyResult>(`${API_BASE}/physics-lab/tomography`, {
      method: 'POST',
      body: JSON.stringify(data)
    }),
  getDensityMatrix: (data: { theta: number; phi: number }) =>
    fetchJson<DensityMatrixAnalysis>(`${API_BASE}/physics-lab/density-matrix`, {
      method: 'POST',
      body: JSON.stringify(data)
    }),
  simulateChannel: (data: { channel_name: string; theta: number; phi: number; parameter: number }) =>
    fetchJson<ChannelSimulationResult>(`${API_BASE}/physics-lab/channel-simulation`, {
      method: 'POST',
      body: JSON.stringify(data)
    }),
  getDecoherenceSweep: (data: { channel_name: string; theta?: number; phi?: number; steps?: number }) =>
    fetchJson<{ channel_name: string; sweep: DecoherenceSweepPoint[] }>(`${API_BASE}/physics-lab/decoherence-sweep`, {
      method: 'POST',
      body: JSON.stringify(data)
    }),
  runInterceptResend: (data: { theta?: number; phi?: number; shots?: number; eve_active: boolean }) =>
    fetchJson<InterceptResendResult>(`${API_BASE}/physics-lab/intercept-resend`, {
      method: 'POST',
      body: JSON.stringify(data)
    }),
  runNoCloning: (data: { theta?: number; phi?: number }) =>
    fetchJson<NoCloningResult>(`${API_BASE}/physics-lab/no-cloning`, {
      method: 'POST',
      body: JSON.stringify(data)
    }),
  analyzeBellState: (data: { bell_type: string; shots?: number }) =>
    fetchJson<BellStateAnalysis>(`${API_BASE}/physics-lab/bell-states`, {
      method: 'POST',
      body: JSON.stringify(data)
    }),
  runChshTest: (data: { shots?: number; noise_level?: number }) =>
    fetchJson<ChshTestResult>(`${API_BASE}/physics-lab/chsh-test`, {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  // QDS Protocol Endpoints (Steps 2-3)
  qdsKeygen: (data?: QDSKeygenRequest) =>
    fetchJson<QDSKeygenResponse>(`${API_BASE}/qds/keygen`, {
      method: 'POST',
      body: JSON.stringify(data || {})
    }),
  qdsDistribute: (data: QDSDistributeRequest) =>
    fetchJson<QDSDistributeResponse>(`${API_BASE}/qds/distribute`, {
      method: 'POST',
      body: JSON.stringify(data)
    }),
  qdsSign: (data: QDSSignRequest) =>
    fetchJson<QDSSignResponse>(`${API_BASE}/qds/sign`, {
      method: 'POST',
      body: JSON.stringify(data)
    }),
  qdsVerify: (data: QDSVerifyRequest) =>
    fetchJson<QDSVerifyResponse>(`${API_BASE}/qds/verify`, {
      method: 'POST',
      body: JSON.stringify(data)
    }),
  getQdsMemory: (keyId: string, verifierId: string) =>
    fetchJson<any>(`${API_BASE}/qds/memory/${keyId}/${verifierId}`),

  // Analysis & Sweeps Endpoints (Step 4)
  getHoeffdingBounds: (params?: { L?: number; p_e?: number; p_h?: number; s_a?: number }) => {
    const q = new URLSearchParams();
    if (params?.L !== undefined) q.set('L', params.L.toString());
    if (params?.p_e !== undefined) q.set('p_e', params.p_e.toString());
    if (params?.p_h !== undefined) q.set('p_h', params.p_h.toString());
    if (params?.s_a !== undefined) q.set('s_a', params.s_a.toString());
    return fetchJson<HoeffdingBoundResponse>(`${API_BASE}/analysis/hoeffding?${q.toString()}`);
  },
  runMonteCarlo: (data: MonteCarloSimulationRequest) =>
    fetchJson<MonteCarloSimulationResponse>(`${API_BASE}/analysis/monte-carlo`, {
      method: 'POST',
      body: JSON.stringify(data)
    }),
  getAerValidation: (params?: { L?: number; shots?: number; seed?: number }) => {
    const q = new URLSearchParams();
    if (params?.L !== undefined) q.set('L', params.L.toString());
    if (params?.shots !== undefined) q.set('shots', params.shots.toString());
    if (params?.seed !== undefined) q.set('seed', params.seed.toString());
    return fetchJson<AerValidationResponse>(`${API_BASE}/analysis/aer-validation?${q.toString()}`);
  },
  getSweeps: (params?: { L?: number; s_a?: number; p_e?: number; p_h?: number; N?: number; seed?: number }) => {
    const q = new URLSearchParams();
    if (params?.L !== undefined) q.set('L', params.L.toString());
    if (params?.s_a !== undefined) q.set('s_a', params.s_a.toString());
    if (params?.p_e !== undefined) q.set('p_e', params.p_e.toString());
    if (params?.p_h !== undefined) q.set('p_h', params.p_h.toString());
    if (params?.N !== undefined) q.set('N', params.N.toString());
    if (params?.seed !== undefined) q.set('seed', params.seed.toString());
    return fetchJson<SweepsResponse>(`${API_BASE}/analysis/sweeps?${q.toString()}`);
  },
  getSweepsExportUrl: (format: string, sweepType: string, L?: number, s_a?: number, p_e?: number, p_h?: number, N?: number) => {
    const q = new URLSearchParams({ format, sweep_type: sweepType });
    if (L !== undefined) q.set('L', L.toString());
    if (s_a !== undefined) q.set('s_a', s_a.toString());
    if (p_e !== undefined) q.set('p_e', p_e.toString());
    if (p_h !== undefined) q.set('p_h', p_h.toString());
    if (N !== undefined) q.set('N', N.toString());
    return `${API_BASE}/analysis/sweeps/export?${q.toString()}`;
  },
  getPerformanceBenchmarks: (iterations?: number, seed?: number) => {
    const q = new URLSearchParams();
    if (iterations !== undefined) q.set('iterations', iterations.toString());
    if (seed !== undefined) q.set('seed', seed.toString());
    return fetchJson<PerformanceBenchmarkResponse>(`${API_BASE}/analysis/benchmarks?${q.toString()}`);
  },
  getConfusionMatrix: (params?: { trials_per_category?: number; L?: number; s_a?: number; s_v?: number; seed?: number }) => {
    const q = new URLSearchParams();
    if (params?.trials_per_category !== undefined) q.set('trials_per_category', params.trials_per_category.toString());
    if (params?.L !== undefined) q.set('L', params.L.toString());
    if (params?.s_a !== undefined) q.set('s_a', params.s_a.toString());
    if (params?.s_v !== undefined) q.set('s_v', params.s_v.toString());
    if (params?.seed !== undefined) q.set('seed', params.seed.toString());
    return fetchJson<ConfusionMatrixResponse>(`${API_BASE}/analysis/confusion-matrix?${q.toString()}`);
  }
};
