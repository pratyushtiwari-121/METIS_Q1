import React, { useState, useEffect } from 'react';
import {
  Atom,
  Activity,
  Play,
  ShieldAlert,
  CheckCircle2,
  AlertTriangle,
  Layers,
  Zap,
  LineChart as ChartIcon,
  Copy,
  Radio,
  Share2
} from 'lucide-react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  Legend
} from 'recharts';
import { api } from '../services/api';
import type {
  TomographyResult,
  ChannelSimulationResult,
  DecoherenceSweepPoint,
  InterceptResendResult,
  NoCloningResult,
  BellStateAnalysis,
  ChshTestResult,
  CircuitRunResponse
} from '../types';

type TabType =
  | 'teleportation'
  | 'bell'
  | 'chsh'
  | 'tomography'
  | 'channels'
  | 'decoherence'
  | 'intercept'
  | 'no_cloning';

export const PhysicsLabPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabType>('chsh');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // States for experiments
  const [theta, setTheta] = useState<number>(1.2);
  const [phi, setPhi] = useState<number>(0.8);
  const [shots, setShots] = useState<number>(2048);

  // Results
  const [teleportResult, setTeleportResult] = useState<CircuitRunResponse | null>(null);
  const [bellResult, setBellResult] = useState<BellStateAnalysis | null>(null);
  const [selectedBell, setSelectedBell] = useState<string>('phi_plus');
  const [chshResult, setChshResult] = useState<ChshTestResult | null>(null);
  const [chshNoise, setChshNoise] = useState<number>(0.0);
  const [tomoResult, setTomoResult] = useState<TomographyResult | null>(null);
  const [channelType, setChannelType] = useState<string>('depolarizing');
  const [channelParam, setChannelParam] = useState<number>(0.25);
  const [channelResult, setChannelResult] = useState<ChannelSimulationResult | null>(null);
  const [sweepPoints, setSweepPoints] = useState<DecoherenceSweepPoint[]>([]);
  const [eveActive, setEveActive] = useState<boolean>(true);
  const [interceptResult, setInterceptResult] = useState<InterceptResendResult | null>(null);
  const [noCloningResult, setNoCloningResult] = useState<NoCloningResult | null>(null);

  // --- Handlers ---
  const handleRunTeleportation = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.runPredefinedCircuit({
        circuit_name: 'teleportation',
        shots,
        custom_state_angle: theta
      });
      setTeleportResult(res);
    } catch (err: any) {
      setError(err.message || 'Teleportation protocol failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleRunBell = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.analyzeBellState({ bell_type: selectedBell, shots });
      setBellResult(res);
    } catch (err: any) {
      setError(err.message || 'Bell state analysis failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleRunChsh = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.runChshTest({ shots, noise_level: chshNoise });
      setChshResult(res);
    } catch (err: any) {
      setError(err.message || 'CHSH Bell test failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleRunTomography = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.runTomography({ theta, phi, shots });
      setTomoResult(res);
    } catch (err: any) {
      setError(err.message || 'Tomography failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleRunChannel = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.simulateChannel({
        channel_name: channelType,
        theta,
        phi,
        parameter: channelParam
      });
      setChannelResult(res);
    } catch (err: any) {
      setError(err.message || 'Channel simulation failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleRunSweep = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.getDecoherenceSweep({
        channel_name: channelType,
        theta,
        phi,
        steps: 21
      });
      setSweepPoints(res.sweep);
    } catch (err: any) {
      setError(err.message || 'Decoherence sweep failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleRunIntercept = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.runInterceptResend({ theta, phi, shots, eve_active: eveActive });
      setInterceptResult(res);
    } catch (err: any) {
      setError(err.message || 'Intercept-resend experiment failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleRunNoCloning = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.runNoCloning({ theta, phi });
      setNoCloningResult(res);
    } catch (err: any) {
      setError(err.message || 'No-cloning demonstration failed.');
    } finally {
      setLoading(false);
    }
  };

  // Initial load
  useEffect(() => {
    handleRunChsh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Switch tab & trigger default run
  const handleTabChange = (t: TabType) => {
    setActiveTab(t);
    setError(null);
    if (t === 'chsh' && !chshResult) handleRunChsh();
    else if (t === 'bell' && !bellResult) handleRunBell();
    else if (t === 'teleportation' && !teleportResult) handleRunTeleportation();
    else if (t === 'tomography' && !tomoResult) handleRunTomography();
    else if (t === 'channels' && !channelResult) handleRunChannel();
    else if (t === 'decoherence' && sweepPoints.length === 0) handleRunSweep();
    else if (t === 'intercept' && !interceptResult) handleRunIntercept();
    else if (t === 'no_cloning' && !noCloningResult) handleRunNoCloning();
  };

  return (
    <div className="space-y-6 pb-16">
      {/* Header */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <Atom className="w-6 h-6 text-cyan-400" />
            Quantum Physics Laboratory
          </h1>
          <p className="text-xs text-slate-400">
            Rigorous experimental verification of quantum information principles, linear algebra operators, and channel diagnostics (Strictly Zero AI/ML).
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="px-3 py-1 rounded-md bg-cyan-950/50 border border-cyan-500/30 text-cyan-300 text-xs font-mono">
            Qiskit Aer Simulator 2.x
          </span>
        </div>
      </div>

      {/* Tabs Navigation */}
      <div className="flex items-center gap-1.5 overflow-x-auto pb-2 border-b border-slate-800 text-xs">
        {[
          { id: 'chsh', label: 'CHSH Bell Inequality', icon: Zap },
          { id: 'bell', label: 'Bell States (EPR)', icon: Share2 },
          { id: 'teleportation', label: 'Quantum Teleportation', icon: Activity },
          { id: 'tomography', label: 'State Tomography', icon: Layers },
          { id: 'channels', label: 'Quantum Channels (6)', icon: Radio },
          { id: 'decoherence', label: 'Decoherence Curves', icon: ChartIcon },
          { id: 'intercept', label: 'Intercept-Resend (Eve)', icon: ShieldAlert },
          { id: 'no_cloning', label: 'No-Cloning Theorem', icon: Copy }
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => handleTabChange(tab.id as TabType)}
              className={`flex items-center gap-1.5 px-3 py-2 rounded-lg font-medium transition-all whitespace-nowrap cursor-pointer ${
                isActive
                  ? 'bg-blue-600/30 border border-cyan-500/50 text-cyan-300 shadow-md shadow-cyan-950/40'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/50 border border-transparent'
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {error && (
        <div className="p-3 rounded-lg bg-red-950/60 border border-red-500/40 text-red-300 text-xs flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* =======================================================================
          TAB 1: CHSH BELL INEQUALITY TEST
         ======================================================================= */}
      {activeTab === 'chsh' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Controls & Theoretical Panel */}
          <div className="p-5 rounded-xl bg-[#0a1122]/90 border border-blue-500/20 shadow-lg space-y-4">
            <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider font-sans flex items-center gap-2">
              <Zap className="w-4 h-4 text-cyan-400" />
              CHSH Experiment Parameters
            </h2>

            <div className="space-y-3 text-xs">
              <div>
                <div className="flex justify-between text-slate-400 mb-1">
                  <span>Measurement Shots per Setting</span>
                  <span className="font-mono text-cyan-300">{shots}</span>
                </div>
                <input
                  type="range"
                  min="512"
                  max="8192"
                  step="512"
                  value={shots}
                  onChange={(e) => setShots(Number(e.target.value))}
                  className="w-full accent-cyan-500 cursor-pointer"
                />
              </div>

              <div>
                <div className="flex justify-between text-slate-400 mb-1">
                  <span>Channel Depolarizing Noise</span>
                  <span className="font-mono text-cyan-300">{Math.round(chshNoise * 100)}%</span>
                </div>
                <input
                  type="range"
                  min="0.0"
                  max="0.8"
                  step="0.05"
                  value={chshNoise}
                  onChange={(e) => setChshNoise(Number(e.target.value))}
                  className="w-full accent-cyan-500 cursor-pointer"
                />
              </div>

              <button
                onClick={handleRunChsh}
                disabled={loading}
                className="w-full py-2.5 rounded-lg bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white font-semibold flex items-center justify-center gap-2 shadow-md cursor-pointer transition-all disabled:opacity-50"
              >
                <Play className="w-4 h-4" />
                <span>{loading ? 'Running Quantum Circuit...' : 'Execute CHSH Test'}</span>
              </button>
            </div>

            <div className="p-3 rounded-lg bg-[#070b16] border border-blue-900/30 text-[11px] text-slate-300 space-y-2">
              <span className="font-semibold text-cyan-300 block">Physical Foundation:</span>
              <p className="leading-relaxed">
                The Clauser-Horne-Shimony-Holt (CHSH) inequality tests non-local correlations on entangled Bell state <span className="font-mono text-purple-300">|Φ+⟩</span>:
              </p>
              <div className="p-2 rounded bg-slate-900 font-mono text-[10px] text-cyan-200">
                S = E(a, b) + E(a, b') + E(a', b) - E(a', b')
              </div>
              <ul className="list-disc list-inside space-y-0.5 text-[10px] text-slate-400">
                <li>Classical Local Realism: <span className="font-mono text-red-300">|S| ≤ 2.0</span></li>
                <li>Quantum Tsirelson Bound: <span className="font-mono text-emerald-300">|S| ≤ 2√2 ≈ 2.8284</span></li>
              </ul>
              <p className="text-[10px] text-slate-400 italic pt-1">
                Diagnostic: Quantum violation confirms clean entangled EPR distribution free from eavesdropper measurement collapse.
              </p>
            </div>
          </div>

          {/* Results Panel */}
          <div className="lg:col-span-2 space-y-6">
            {chshResult ? (
              <div className="p-5 rounded-xl bg-[#0a1122]/90 border border-blue-500/20 shadow-lg space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider font-sans">
                    CHSH Bell Parameter Result
                  </h3>
                  <span
                    className={`px-2.5 py-1 rounded-md text-xs font-bold border font-mono ${
                      chshResult.violates_classical_bound
                        ? 'bg-emerald-950/60 border-emerald-500/50 text-emerald-300'
                        : 'bg-red-950/60 border-red-500/50 text-red-300'
                    }`}
                  >
                    {chshResult.violates_classical_bound ? 'QUANTUM VIOLATION' : 'CLASSICAL BOUND (DEGRADED)'}
                  </span>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-center font-mono">
                  <div className="p-3 rounded-lg bg-[#070b16] border border-blue-900/40">
                    <span className="text-[10px] text-slate-400 block mb-1">Measured |S|</span>
                    <span
                      className={`text-xl font-bold ${
                        chshResult.violates_classical_bound ? 'text-emerald-400' : 'text-red-400'
                      }`}
                    >
                      {chshResult.chsh_s_value}
                    </span>
                  </div>
                  <div className="p-3 rounded-lg bg-[#070b16] border border-blue-900/40">
                    <span className="text-[10px] text-slate-400 block mb-1">Classical Limit</span>
                    <span className="text-xl font-bold text-slate-400">2.0000</span>
                  </div>
                  <div className="p-3 rounded-lg bg-[#070b16] border border-blue-900/40">
                    <span className="text-[10px] text-slate-400 block mb-1">Tsirelson Bound</span>
                    <span className="text-xl font-bold text-purple-300">2.8284</span>
                  </div>
                  <div className="p-3 rounded-lg bg-[#070b16] border border-blue-900/40">
                    <span className="text-[10px] text-slate-400 block mb-1">Violation Margin</span>
                    <span className="text-xl font-bold text-cyan-300">
                      +{chshResult.quantum_violation_margin}
                    </span>
                  </div>
                </div>

                {/* Sub-Correlations */}
                <div>
                  <h4 className="text-xs font-semibold text-slate-300 mb-2 font-sans">
                    Individual Setting Correlations E(θ_A, θ_B):
                  </h4>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs font-mono">
                    {Object.entries(chshResult.correlations).map(([key, val]) => (
                      <div key={key} className="p-2.5 rounded bg-slate-900/80 border border-slate-800 flex justify-between">
                        <span className="text-slate-400">{key}:</span>
                        <span className="text-cyan-300 font-bold">{val}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Verdict Card */}
                <div
                  className={`p-3.5 rounded-lg border text-xs flex items-start gap-2.5 ${
                    chshResult.violates_classical_bound
                      ? 'bg-emerald-950/40 border-emerald-500/30 text-emerald-200'
                      : 'bg-red-950/40 border-red-500/30 text-red-200'
                  }`}
                >
                  {chshResult.violates_classical_bound ? (
                    <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
                  ) : (
                    <AlertTriangle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
                  )}
                  <div>
                    <p className="font-semibold mb-0.5">{chshResult.channel_verdict}</p>
                    <p className="text-[11px] text-slate-400 italic">{chshResult.disclaimer}</p>
                  </div>
                </div>
              </div>
            ) : (
              <div className="p-12 rounded-xl bg-[#0a1122]/50 border border-slate-800 text-center text-slate-400 text-xs">
                Executing CHSH quantum circuit test...
              </div>
            )}
          </div>
        </div>
      )}

      {/* =======================================================================
          TAB 2: BELL STATES (EPR PAIR)
         ======================================================================= */}
      {activeTab === 'bell' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="p-5 rounded-xl bg-[#0a1122]/90 border border-blue-500/20 shadow-lg space-y-4">
            <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider font-sans flex items-center gap-2">
              <Share2 className="w-4 h-4 text-cyan-400" />
              Bell State Selection
            </h2>

            <div className="space-y-3 text-xs">
              <div>
                <label className="text-slate-400 block mb-1">State Type</label>
                <select
                  value={selectedBell}
                  onChange={(e) => setSelectedBell(e.target.value)}
                  className="w-full p-2 rounded-lg bg-[#070b16] border border-blue-900/40 text-slate-200 font-mono text-xs focus:outline-none"
                >
                  <option value="phi_plus">|Φ+⟩ = (|00⟩ + |11⟩) / √2</option>
                  <option value="phi_minus">|Φ-⟩ = (|00⟩ - |11⟩) / √2</option>
                  <option value="psi_plus">|Ψ+⟩ = (|01⟩ + |10⟩) / √2</option>
                  <option value="psi_minus">|Ψ-⟩ = (|01⟩ - |10⟩) / √2</option>
                </select>
              </div>

              <div>
                <label className="text-slate-400 block mb-1">Shots: {shots}</label>
                <input
                  type="range"
                  min="512"
                  max="4096"
                  step="512"
                  value={shots}
                  onChange={(e) => setShots(Number(e.target.value))}
                  className="w-full accent-cyan-500 cursor-pointer"
                />
              </div>

              <button
                onClick={handleRunBell}
                disabled={loading}
                className="w-full py-2.5 rounded-lg bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white font-semibold flex items-center justify-center gap-2 shadow-md cursor-pointer disabled:opacity-50"
              >
                <Play className="w-4 h-4" />
                <span>{loading ? 'Measuring...' : 'Analyze Entanglement'}</span>
              </button>
            </div>
          </div>

          <div className="lg:col-span-2 space-y-6">
            {bellResult && (
              <div className="p-5 rounded-xl bg-[#0a1122]/90 border border-blue-500/20 shadow-lg space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-bold text-slate-200 uppercase font-sans">
                    Bell State Measurement Statistics
                  </h3>
                  <span className="text-xs font-mono text-cyan-300">
                    Correlation E = {bellResult.correlation}
                  </span>
                </div>

                <div className="h-48 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={Object.entries(bellResult.probabilities).map(([state, prob]) => ({
                        state: `|${state}⟩`,
                        probability: prob
                      }))}
                    >
                      <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                      <XAxis dataKey="state" stroke="#64748b" fontSize={11} fontFamily="monospace" />
                      <YAxis stroke="#64748b" fontSize={11} domain={[0, 1]} />
                      <RechartsTooltip
                        contentStyle={{ backgroundColor: '#0c1427', borderColor: '#06b6d4', fontSize: 12 }}
                      />
                      <Bar dataKey="probability" fill="#06b6d4" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>

                <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 text-xs font-mono">
                  <span className="text-slate-400 block mb-1 font-sans">Generated Qiskit Circuit Diagram:</span>
                  <pre className="text-purple-300 overflow-x-auto text-[11px] leading-tight">
                    {bellResult.circuit_ascii}
                  </pre>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* =======================================================================
          TAB 3: QUANTUM TELEPORTATION PROTOCOL
         ======================================================================= */}
      {activeTab === 'teleportation' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="p-5 rounded-xl bg-[#0a1122]/90 border border-blue-500/20 shadow-lg space-y-4">
            <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider font-sans flex items-center gap-2">
              <Activity className="w-4 h-4 text-cyan-400" />
              Teleportation Input State
            </h2>

            <div className="space-y-3 text-xs">
              <div>
                <label className="text-slate-400 block mb-1">State θ (Polar Angle): {theta.toFixed(3)} rad</label>
                <input
                  type="range"
                  min="0.0"
                  max="3.14159"
                  step="0.05"
                  value={theta}
                  onChange={(e) => setTheta(Number(e.target.value))}
                  className="w-full accent-cyan-500 cursor-pointer"
                />
              </div>

              <button
                onClick={handleRunTeleportation}
                disabled={loading}
                className="w-full py-2.5 rounded-lg bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white font-semibold flex items-center justify-center gap-2 shadow-md cursor-pointer disabled:opacity-50"
              >
                <Play className="w-4 h-4" />
                <span>{loading ? 'Simulating...' : 'Run Teleportation'}</span>
              </button>
            </div>
          </div>

          <div className="lg:col-span-2 space-y-6">
            {teleportResult && (
              <div className="p-5 rounded-xl bg-[#0a1122]/90 border border-blue-500/20 shadow-lg space-y-4">
                <h3 className="text-sm font-bold text-slate-200 uppercase font-sans">
                  Teleportation Circuit with Classical Feed-Forward
                </h3>
                <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 text-xs font-mono">
                  <pre className="text-cyan-300 overflow-x-auto text-[11px] leading-tight">
                    {teleportResult.circuit_ascii}
                  </pre>
                </div>
                <div className="p-3 rounded-lg bg-blue-950/40 border border-blue-500/30 text-xs text-slate-300">
                  <pre className="font-sans whitespace-pre-wrap">{teleportResult.analysis_note}</pre>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* =======================================================================
          TAB 4: STATE TOMOGRAPHY
         ======================================================================= */}
      {activeTab === 'tomography' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="p-5 rounded-xl bg-[#0a1122]/90 border border-blue-500/20 shadow-lg space-y-4">
            <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider font-sans flex items-center gap-2">
              <Layers className="w-4 h-4 text-cyan-400" />
              State Tomography Setup
            </h2>

            <div className="space-y-3 text-xs">
              <div>
                <label className="text-slate-400 block mb-1">State θ: {theta.toFixed(3)} rad</label>
                <input
                  type="range"
                  min="0.0"
                  max="3.14159"
                  step="0.05"
                  value={theta}
                  onChange={(e) => setTheta(Number(e.target.value))}
                  className="w-full accent-cyan-500 cursor-pointer"
                />
              </div>

              <div>
                <label className="text-slate-400 block mb-1">State φ: {phi.toFixed(3)} rad</label>
                <input
                  type="range"
                  min="0.0"
                  max="6.28318"
                  step="0.05"
                  value={phi}
                  onChange={(e) => setPhi(Number(e.target.value))}
                  className="w-full accent-cyan-500 cursor-pointer"
                />
              </div>

              <div>
                <label className="text-slate-400 block mb-1">Shots: {shots}</label>
                <input
                  type="range"
                  min="512"
                  max="4096"
                  step="512"
                  value={shots}
                  onChange={(e) => setShots(Number(e.target.value))}
                  className="w-full accent-cyan-500 cursor-pointer"
                />
              </div>

              <button
                onClick={handleRunTomography}
                disabled={loading}
                className="w-full py-2.5 rounded-lg bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white font-semibold flex items-center justify-center gap-2 shadow-md cursor-pointer disabled:opacity-50"
              >
                <Play className="w-4 h-4" />
                <span>{loading ? 'Reconstructing...' : 'Run Pauli Tomography'}</span>
              </button>
            </div>
          </div>

          <div className="lg:col-span-2 space-y-6">
            {tomoResult && (
              <div className="p-5 rounded-xl bg-[#0a1122]/90 border border-blue-500/20 shadow-lg space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-bold text-slate-200 uppercase font-sans">
                    Tomography Reconstruction Results
                  </h3>
                  <span className="text-xs font-mono font-bold text-emerald-400">
                    Reconstruction Fidelity F = {tomoResult.fidelity}
                  </span>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 font-mono text-center text-xs">
                  <div className="p-2.5 rounded bg-[#070b16] border border-slate-800">
                    <span className="text-[10px] text-slate-400 block">Fidelity</span>
                    <span className="text-emerald-400 font-bold text-base">{tomoResult.fidelity}</span>
                  </div>
                  <div className="p-2.5 rounded bg-[#070b16] border border-slate-800">
                    <span className="text-[10px] text-slate-400 block">Trace Distance</span>
                    <span className="text-purple-300 font-bold text-base">{tomoResult.trace_distance}</span>
                  </div>
                  <div className="p-2.5 rounded bg-[#070b16] border border-slate-800">
                    <span className="text-[10px] text-slate-400 block">Purity</span>
                    <span className="text-cyan-300 font-bold text-base">{tomoResult.purity_reconstructed}</span>
                  </div>
                  <div className="p-2.5 rounded bg-[#070b16] border border-slate-800">
                    <span className="text-[10px] text-slate-400 block">Entropy S(ρ)</span>
                    <span className="text-slate-300 font-bold text-base">{tomoResult.entropy_reconstructed}</span>
                  </div>
                </div>

                {/* Pauli Expectations */}
                <div>
                  <h4 className="text-xs font-semibold text-slate-300 mb-2 font-sans">
                    Empirical vs Theoretical Pauli Expectations:
                  </h4>
                  <div className="grid grid-cols-3 gap-2 text-xs font-mono">
                    {['X', 'Y', 'Z'].map((basis) => {
                      const m = (tomoResult.measurements as any)[basis];
                      return (
                        <div key={basis} className="p-2 rounded bg-slate-900 border border-slate-800 space-y-1">
                          <span className="text-cyan-400 font-bold block">⟨{basis}⟩</span>
                          <div className="flex justify-between text-[11px]">
                            <span className="text-slate-400">Obs:</span>
                            <span className="text-slate-200">{m.observed_expectation}</span>
                          </div>
                          <div className="flex justify-between text-[11px]">
                            <span className="text-slate-400">Exp:</span>
                            <span className="text-slate-400">{m.theoretical_expectation}</span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* =======================================================================
          TAB 5: QUANTUM CHANNELS
         ======================================================================= */}
      {activeTab === 'channels' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="p-5 rounded-xl bg-[#0a1122]/90 border border-blue-500/20 shadow-lg space-y-4">
            <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider font-sans flex items-center gap-2">
              <Radio className="w-4 h-4 text-cyan-400" />
              Select Channel Model
            </h2>

            <div className="space-y-3 text-xs">
              <div>
                <label className="text-slate-400 block mb-1">Channel Type</label>
                <select
                  value={channelType}
                  onChange={(e) => setChannelType(e.target.value)}
                  className="w-full p-2 rounded-lg bg-[#070b16] border border-blue-900/40 text-slate-200 text-xs focus:outline-none"
                >
                  <option value="depolarizing">Depolarizing Channel (Isotropic Noise)</option>
                  <option value="bit_flip">Bit-Flip Channel (Pauli-X Error)</option>
                  <option value="phase_flip">Phase-Flip Channel (Pauli-Z Error)</option>
                  <option value="bit_phase_flip">Bit-Phase-Flip Channel (Pauli-Y Error)</option>
                  <option value="amplitude_damping">Amplitude Damping (T1 Energy Relaxation)</option>
                  <option value="phase_damping">Phase Damping (T2 Pure Dephasing)</option>
                </select>
              </div>

              <div>
                <div className="flex justify-between text-slate-400 mb-1">
                  <span>Channel Parameter: {channelParam.toFixed(2)}</span>
                </div>
                <input
                  type="range"
                  min="0.0"
                  max="1.0"
                  step="0.05"
                  value={channelParam}
                  onChange={(e) => setChannelParam(Number(e.target.value))}
                  className="w-full accent-cyan-500 cursor-pointer"
                />
              </div>

              <button
                onClick={handleRunChannel}
                disabled={loading}
                className="w-full py-2.5 rounded-lg bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white font-semibold flex items-center justify-center gap-2 shadow-md cursor-pointer disabled:opacity-50"
              >
                <Play className="w-4 h-4" />
                <span>{loading ? 'Simulating...' : 'Apply Channel'}</span>
              </button>
            </div>
          </div>

          <div className="lg:col-span-2 space-y-6">
            {channelResult && (
              <div className="p-5 rounded-xl bg-[#0a1122]/90 border border-blue-500/20 shadow-lg space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-bold text-slate-200 uppercase font-sans">
                    Channel Physical Impact Analysis
                  </h3>
                  <span className="text-xs font-mono text-cyan-300">
                    Fidelity F = {channelResult.metrics.fidelity}
                  </span>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 font-mono text-center text-xs">
                  <div className="p-2.5 rounded bg-[#070b16] border border-slate-800">
                    <span className="text-[10px] text-slate-400 block">State Fidelity</span>
                    <span className="text-emerald-400 font-bold text-base">{channelResult.metrics.fidelity}</span>
                  </div>
                  <div className="p-2.5 rounded bg-[#070b16] border border-slate-800">
                    <span className="text-[10px] text-slate-400 block">Trace Distance</span>
                    <span className="text-purple-300 font-bold text-base">{channelResult.metrics.trace_distance}</span>
                  </div>
                  <div className="p-2.5 rounded bg-[#070b16] border border-slate-800">
                    <span className="text-[10px] text-slate-400 block">Bloch Displacement</span>
                    <span className="text-cyan-300 font-bold text-base">{channelResult.metrics.bloch_displacement}</span>
                  </div>
                  <div className="p-2.5 rounded bg-[#070b16] border border-slate-800">
                    <span className="text-[10px] text-slate-400 block">Induced QBER</span>
                    <span className="text-red-400 font-bold text-base">{channelResult.metrics.qber}</span>
                  </div>
                </div>

                {/* State comparison */}
                <div className="grid grid-cols-2 gap-3 text-xs font-mono">
                  <div className="p-3 rounded bg-slate-900 border border-slate-800">
                    <span className="text-slate-400 block mb-1 font-sans">Input State:</span>
                    <p className="text-slate-200">Purity: {channelResult.initial_state.purity}</p>
                    <p className="text-slate-200">Entropy S: {channelResult.initial_state.entropy}</p>
                    <p className="text-cyan-300 text-[11px] mt-1">
                      Bloch: ({channelResult.initial_state.bloch.x}, {channelResult.initial_state.bloch.y}, {channelResult.initial_state.bloch.z})
                    </p>
                  </div>
                  <div className="p-3 rounded bg-slate-900 border border-slate-800">
                    <span className="text-slate-400 block mb-1 font-sans">Output State (Disturbed):</span>
                    <p className="text-purple-300">Purity: {channelResult.output_state.purity}</p>
                    <p className="text-purple-300">Entropy S: {channelResult.output_state.entropy}</p>
                    <p className="text-cyan-300 text-[11px] mt-1">
                      Bloch: ({channelResult.output_state.bloch.x}, {channelResult.output_state.bloch.y}, {channelResult.output_state.bloch.z})
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* =======================================================================
          TAB 6: DECOHERENCE SWEEP CURVES
         ======================================================================= */}
      {activeTab === 'decoherence' && (
        <div className="space-y-6">
          <div className="p-5 rounded-xl bg-[#0a1122]/90 border border-blue-500/20 shadow-lg space-y-4">
            <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
              <div>
                <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider font-sans flex items-center gap-2">
                  <ChartIcon className="w-4 h-4 text-cyan-400" />
                  Decoherence Parameter Sweeps (Live Physical Curves)
                </h2>
                <p className="text-xs text-slate-400">
                  Observe how Fidelity, Purity, Entropy, and Trace Distance degrade as channel noise increases.
                </p>
              </div>
              <div className="flex items-center gap-2">
                <select
                  value={channelType}
                  onChange={(e) => setChannelType(e.target.value)}
                  className="p-1.5 rounded-lg bg-[#070b16] border border-blue-900/40 text-slate-200 text-xs font-mono"
                >
                  <option value="depolarizing">Depolarizing</option>
                  <option value="bit_flip">Bit Flip</option>
                  <option value="phase_flip">Phase Flip</option>
                  <option value="amplitude_damping">Amplitude Damping</option>
                  <option value="phase_damping">Phase Damping</option>
                </select>
                <button
                  onClick={handleRunSweep}
                  disabled={loading}
                  className="px-3 py-1.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-semibold text-xs cursor-pointer"
                >
                  {loading ? 'Sweeping...' : 'Recompute Sweep'}
                </button>
              </div>
            </div>

            {sweepPoints.length > 0 && (
              <div className="h-72 w-full pt-2">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={sweepPoints} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                    <XAxis
                      dataKey="noise_parameter"
                      stroke="#64748b"
                      fontSize={11}
                      label={{ value: 'Noise Parameter (p)', position: 'insideBottomRight', offset: -5 }}
                    />
                    <YAxis stroke="#64748b" fontSize={11} domain={[0, 1]} />
                    <RechartsTooltip
                      contentStyle={{ backgroundColor: '#0c1427', borderColor: '#06b6d4', fontSize: 12 }}
                    />
                    <Legend wrapperStyle={{ fontSize: 11 }} />
                    <Line type="monotone" dataKey="fidelity" stroke="#10b981" name="Fidelity" strokeWidth={2} />
                    <Line type="monotone" dataKey="purity" stroke="#06b6d4" name="Purity" strokeWidth={2} />
                    <Line type="monotone" dataKey="entropy" stroke="#f59e0b" name="Entropy S(ρ)" strokeWidth={2} />
                    <Line type="monotone" dataKey="trace_distance" stroke="#ec4899" name="Trace Distance" strokeWidth={2} />
                    <Line type="monotone" dataKey="qber" stroke="#ef4444" name="QBER" strokeWidth={2} strokeDasharray="4 4" />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>
        </div>
      )}

      {/* =======================================================================
          TAB 7: INTERCEPT-RESEND EAVESDROPPING
         ======================================================================= */}
      {activeTab === 'intercept' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="p-5 rounded-xl bg-[#0a1122]/90 border border-blue-500/20 shadow-lg space-y-4">
            <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider font-sans flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 text-cyan-400" />
              Eavesdropping Configuration
            </h2>

            <div className="space-y-3 text-xs">
              <div className="flex items-center gap-2 p-2.5 rounded-lg bg-slate-900 border border-slate-800">
                <input
                  type="checkbox"
                  id="eveToggle"
                  checked={eveActive}
                  onChange={(e) => setEveActive(e.target.checked)}
                  className="rounded text-cyan-500 cursor-pointer"
                />
                <label htmlFor="eveToggle" className="cursor-pointer font-medium text-slate-200">
                  Activate Eve (Intercept-Resend in random basis)
                </label>
              </div>

              <div>
                <label className="text-slate-400 block mb-1">Shots: {shots}</label>
                <input
                  type="range"
                  min="512"
                  max="4096"
                  step="512"
                  value={shots}
                  onChange={(e) => setShots(Number(e.target.value))}
                  className="w-full accent-cyan-500 cursor-pointer"
                />
              </div>

              <button
                onClick={handleRunIntercept}
                disabled={loading}
                className="w-full py-2.5 rounded-lg bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white font-semibold flex items-center justify-center gap-2 shadow-md cursor-pointer disabled:opacity-50"
              >
                <Play className="w-4 h-4" />
                <span>{loading ? 'Measuring Disturbance...' : 'Execute Transmission'}</span>
              </button>
            </div>
          </div>

          <div className="lg:col-span-2 space-y-6">
            {interceptResult && (
              <div className="p-5 rounded-xl bg-[#0a1122]/90 border border-blue-500/20 shadow-lg space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-bold text-slate-200 uppercase font-sans">
                    Eavesdropping Disturbance Detection
                  </h3>
                  <span
                    className={`px-2.5 py-1 rounded-md text-xs font-bold border font-mono ${
                      interceptResult.eve_active
                        ? 'bg-red-950/60 border-red-500/50 text-red-300'
                        : 'bg-emerald-950/60 border-emerald-500/50 text-emerald-300'
                    }`}
                  >
                    {interceptResult.eve_active ? 'EVE DETECTED (COLLAPSED STATE)' : 'CLEAN CHANNEL'}
                  </span>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 font-mono text-center text-xs">
                  <div className="p-2.5 rounded bg-[#070b16] border border-slate-800">
                    <span className="text-[10px] text-slate-400 block">Induced QBER</span>
                    <span className={`text-base font-bold ${interceptResult.eve_active ? 'text-red-400' : 'text-emerald-400'}`}>
                      {(interceptResult.qber * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="p-2.5 rounded bg-[#070b16] border border-slate-800">
                    <span className="text-[10px] text-slate-400 block">State Fidelity</span>
                    <span className={`text-base font-bold ${interceptResult.eve_active ? 'text-red-400' : 'text-emerald-400'}`}>
                      {interceptResult.fidelity}
                    </span>
                  </div>
                  <div className="p-2.5 rounded bg-[#070b16] border border-slate-800">
                    <span className="text-[10px] text-slate-400 block">TVD Deviation</span>
                    <span className="text-purple-300 font-bold text-base">{interceptResult.tvd}</span>
                  </div>
                  <div className="p-2.5 rounded bg-[#070b16] border border-slate-800">
                    <span className="text-[10px] text-slate-400 block">Bob Entropy S</span>
                    <span className="text-amber-400 font-bold text-base">{interceptResult.entropy_bob}</span>
                  </div>
                </div>

                <div
                  className={`p-3 rounded-lg border text-xs flex items-start gap-2.5 ${
                    interceptResult.eve_active
                      ? 'bg-red-950/40 border-red-500/30 text-red-200'
                      : 'bg-emerald-950/40 border-emerald-500/30 text-emerald-200'
                  }`}
                >
                  {interceptResult.eve_active ? (
                    <AlertTriangle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
                  ) : (
                    <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
                  )}
                  <p>{interceptResult.verdict}</p>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* =======================================================================
          TAB 8: NO-CLONING THEOREM DEMONSTRATION
         ======================================================================= */}
      {activeTab === 'no_cloning' && (
        <div className="space-y-6">
          <div className="p-5 rounded-xl bg-[#0a1122]/90 border border-blue-500/20 shadow-lg space-y-4">
            <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider font-sans flex items-center gap-2">
              <Copy className="w-4 h-4 text-cyan-400" />
              Wootters-Zurek Quantum No-Cloning Demonstration (1982)
            </h2>

            {noCloningResult && (
              <div className="space-y-4">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 font-mono text-center text-xs">
                  <div className="p-3 rounded-lg bg-[#070b16] border border-slate-800">
                    <span className="text-[10px] text-slate-400 block mb-1">Theoretical Limit (UQCM)</span>
                    <span className="text-lg font-bold text-cyan-300">5/6 ≈ 0.8333</span>
                  </div>
                  <div className="p-3 rounded-lg bg-[#070b16] border border-slate-800">
                    <span className="text-[10px] text-slate-400 block mb-1">Achieved Clone Fidelity</span>
                    <span className="text-lg font-bold text-purple-300">{noCloningResult.achieved_clone_fidelity}</span>
                  </div>
                  <div className="p-3 rounded-lg bg-[#070b16] border border-slate-800">
                    <span className="text-[10px] text-slate-400 block mb-1">Fidelity Gap (Error)</span>
                    <span className="text-lg font-bold text-red-400">
                      {noCloningResult.fidelity_gap_due_to_physics}
                    </span>
                  </div>
                  <div className="p-3 rounded-lg bg-[#070b16] border border-slate-800">
                    <span className="text-[10px] text-slate-400 block mb-1">Clone Entropy</span>
                    <span className="text-lg font-bold text-amber-300">{noCloningResult.entropy_clone}</span>
                  </div>
                </div>

                <div className="p-4 rounded-xl bg-blue-950/30 border border-blue-500/20 text-xs text-slate-300 leading-relaxed space-y-2">
                  <span className="font-semibold text-cyan-300 block font-sans">
                    Cybersecurity Relevance to Quantum Digital Signatures (QDS):
                  </span>
                  <p>{noCloningResult.security_implication}</p>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
