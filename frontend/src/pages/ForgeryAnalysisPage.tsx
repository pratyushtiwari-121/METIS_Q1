import React, { useState, useEffect, useCallback } from 'react';
import {
  TrendingDown,
  Sliders,
  Play,
  Download,
  Info,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  AreaChart,
  Area
} from 'recharts';
import { api } from '../services/api';
import type {
  HoeffdingBoundResponse,
  MonteCarloSimulationResponse,
  SweepsResponse
} from '../types';

export const ForgeryAnalysisPage: React.FC = () => {
  // Configurable Parameters (Sliders)
  const [L, setL] = useState<number>(64);
  const [sA, setSA] = useState<number>(0.10);
  const [sV, setSV] = useState<number>(0.25);
  const [channelNoise, setChannelNoise] = useState<number>(0.02);
  const [nTrials, setNTrials] = useState<number>(10000);
  const [adversaryStrategy, setAdversaryStrategy] = useState<number>(1.0 / 3.0); // 0.3333 default

  // Data states
  const [hoeffdingData, setHoeffdingData] = useState<HoeffdingBoundResponse | null>(null);
  const [mcData, setMcData] = useState<MonteCarloSimulationResponse | null>(null);
  const [sweepsData, setSweepsData] = useState<SweepsResponse | null>(null);

  // UI state
  const [activeTab, setActiveTab] = useState<'vs_L' | 'vs_threshold' | 'vs_strategy' | 'vs_noise' | 'roc'>('vs_L');
  const [showAssumptions, setShowAssumptions] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const loadAllAnalysisData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      // 1. Fetch analytical Hoeffding bounds & assumptions
      const hData = await api.getHoeffdingBounds({
        L,
        p_e: adversaryStrategy,
        p_h: channelNoise,
        s_a: sA
      });
      setHoeffdingData(hData);

      // 2. Run Monte Carlo simulation
      const mcRes = await api.runMonteCarlo({
        L,
        p_e: adversaryStrategy,
        p_h: channelNoise,
        s_a: sA,
        N_trials: nTrials,
        seed: 42
      });
      setMcData(mcRes);

      // 3. Fetch sweeps dataset
      const swRes = await api.getSweeps({
        L,
        s_a: sA,
        p_e: adversaryStrategy,
        p_h: channelNoise,
        N: Math.min(nTrials, 10000),
        seed: 42
      });
      setSweepsData(swRes);
    } catch (err: any) {
      setError(err.message || 'Failed to execute theoretical security sweeps');
    } finally {
      setIsLoading(false);
    }
  }, [L, sA, adversaryStrategy, channelNoise, nTrials]);

  // Load initial data
  useEffect(() => {
    // oxlint-disable-next-line react/set-state-in-effect
    loadAllAnalysisData();
  }, [loadAllAnalysisData]);

  const handleRunSimulation = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const mcRes = await api.runMonteCarlo({
        L,
        p_e: adversaryStrategy,
        p_h: channelNoise,
        s_a: sA,
        N_trials: nTrials,
        seed: 42
      });
      setMcData(mcRes);

      const hData = await api.getHoeffdingBounds({
        L,
        p_e: adversaryStrategy,
        p_h: channelNoise,
        s_a: sA
      });
      setHoeffdingData(hData);
    } catch (err: any) {
      setError(err.message || 'Simulation execution failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleExport = (format: 'csv' | 'json') => {
    const url = api.getSweepsExportUrl(format, activeTab, L, sA, adversaryStrategy, channelNoise, nTrials);
    window.open(url, '_blank');
  };

  return (
    <div className="space-y-6 pb-16">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <TrendingDown className="w-6 h-6 text-purple-400" />
            Theoretical Forgery Bounds &amp; Monte Carlo Verification
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Analytical Hoeffding concentration bounds validated against Born-rule Monte Carlo simulations across configurable parameter sweeps.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowAssumptions(!showAssumptions)}
            className="flex items-center gap-1.5 px-3 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold border border-slate-700 transition-colors cursor-pointer"
          >
            <Info className="w-4 h-4 text-cyan-400" />
            <span>Assumptions</span>
          </button>

          <button
            onClick={() => handleExport('csv')}
            className="flex items-center gap-1.5 px-3 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold border border-slate-700 transition-colors cursor-pointer"
          >
            <Download className="w-4 h-4 text-emerald-400" />
            <span>Export CSV</span>
          </button>

          <button
            onClick={() => handleExport('json')}
            className="flex items-center gap-1.5 px-3 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold border border-slate-700 transition-colors cursor-pointer"
          >
            <Download className="w-4 h-4 text-cyan-400" />
            <span>Export JSON</span>
          </button>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="p-4 rounded-xl bg-red-950/40 border border-red-500/40 text-red-300 text-xs flex items-center gap-3">
          <AlertCircle className="w-5 h-5 text-red-400 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Documented Mathematical Assumptions Panel */}
      {showAssumptions && hoeffdingData?.assumptions && (
        <div className="p-5 rounded-xl bg-[#0a1224] border border-cyan-500/30 space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-bold text-cyan-300 flex items-center gap-2">
              <Info className="w-4 h-4 text-cyan-400" />
              {hoeffdingData.assumptions.title}
            </h2>
            <span className="text-[10px] font-mono text-slate-400">Classical Concentration Inequalities</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-2">
            <div className="p-3 rounded-lg bg-[#070d1a] border border-blue-900/30 text-xs font-mono space-y-1">
              <span className="text-purple-300 font-bold block">Adversary Forgery Acceptance Bound:</span>
              <p className="text-slate-300 font-semibold">{hoeffdingData.assumptions.bounds?.forgery_acceptance}</p>
            </div>
            <div className="p-3 rounded-lg bg-[#070d1a] border border-blue-900/30 text-xs font-mono space-y-1">
              <span className="text-emerald-300 font-bold block">Honest False Rejection Bound:</span>
              <p className="text-slate-300 font-semibold">{hoeffdingData.assumptions.bounds?.false_rejection}</p>
            </div>
          </div>

          <div className="space-y-2 pt-2">
            {hoeffdingData.assumptions.assumptions?.map((asm) => (
              <div key={asm.id} className="text-xs space-y-0.5">
                <span className="font-bold text-slate-200">Assumption {asm.id} ({asm.name}):</span>
                <p className="text-slate-400 leading-relaxed text-[11px]">{asm.details}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Interactive Controls & Live Metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Parameter Sliders */}
        <div className="p-5 rounded-xl bg-[#090e1a]/90 border border-blue-900/30 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xs font-bold uppercase tracking-wider text-slate-300 font-mono flex items-center gap-2">
              <Sliders className="w-4 h-4 text-cyan-400" />
              Simulation Controls
            </h2>
            <button
              onClick={handleRunSimulation}
              disabled={isLoading}
              className="flex items-center gap-1.5 px-3 py-1 rounded-md bg-cyan-600 hover:bg-cyan-500 text-white text-[11px] font-bold shadow-sm shadow-cyan-500/20 cursor-pointer disabled:opacity-50"
            >
              <Play className="w-3 h-3" />
              <span>Simulate</span>
            </button>
          </div>

          {/* Slider: Key Length L */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs font-mono">
              <span className="text-slate-400">Key Length (L):</span>
              <span className="text-cyan-300 font-bold">{L} copies</span>
            </div>
            <input
              type="range"
              min="8"
              max="256"
              step="8"
              value={L}
              onChange={(e) => setL(parseInt(e.target.value))}
              className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-500"
            />
          </div>

          {/* Slider: Acceptance Threshold s_a */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs font-mono">
              <span className="text-slate-400">Acceptance Threshold (s_a):</span>
              <span className="text-emerald-400 font-bold">{sA.toFixed(2)}</span>
            </div>
            <input
              type="range"
              min="0.02"
              max="0.30"
              step="0.01"
              value={sA}
              onChange={(e) => setSA(parseFloat(e.target.value))}
              className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-emerald-500"
            />
          </div>

          {/* Slider: Rejection Threshold s_v */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs font-mono">
              <span className="text-slate-400">Rejection Threshold (s_v):</span>
              <span className="text-amber-400 font-bold">{sV.toFixed(2)}</span>
            </div>
            <input
              type="range"
              min="0.15"
              max="0.45"
              step="0.01"
              value={sV}
              onChange={(e) => setSV(parseFloat(e.target.value))}
              className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-amber-500"
            />
          </div>

          {/* Slider: Channel Noise p_h */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs font-mono">
              <span className="text-slate-400">Honest Channel Error (p_h):</span>
              <span className="text-blue-400 font-bold">{(channelNoise * 100).toFixed(1)}%</span>
            </div>
            <input
              type="range"
              min="0.0"
              max="0.10"
              step="0.005"
              value={channelNoise}
              onChange={(e) => setChannelNoise(parseFloat(e.target.value))}
              className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-blue-500"
            />
          </div>

          {/* Adversary Strategy Selection */}
          <div className="space-y-1.5 pt-2 border-t border-slate-800/80">
            <label className="text-xs text-slate-400 font-mono block">Adversary Per-Copy Strategy (p_e):</label>
            <select
              value={adversaryStrategy}
              onChange={(e) => setAdversaryStrategy(parseFloat(e.target.value))}
              className="w-full px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700 text-xs font-mono text-slate-200"
            >
              <option value={0.50}>Random Guess (p_e = 0.5000)</option>
              <option value={1.0 / 3.0}>Single-Basis Measure &amp; Guess (p_e = 0.3333)</option>
              <option value={0.5 * (1.0 - 1.0 / Math.sqrt(3))}>Optimal POVM on 3 MUBs (p_e = 0.2113)</option>
            </select>
          </div>

          {/* Slider: N Trials */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs font-mono">
              <span className="text-slate-400">Monte Carlo Iterations (N):</span>
              <span className="text-purple-300 font-bold">{nTrials.toLocaleString()}</span>
            </div>
            <input
              type="range"
              min="1000"
              max="25000"
              step="1000"
              value={nTrials}
              onChange={(e) => setNTrials(parseInt(e.target.value))}
              className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-purple-500"
            />
          </div>
        </div>

        {/* Right: Analytical vs Monte Carlo Verification Status Cards */}
        <div className="lg:col-span-2 grid grid-cols-1 sm:grid-cols-2 gap-4">
          {/* Card 1: Forgery Acceptance Rate */}
          <div className="p-5 rounded-xl bg-[#090e1a]/90 border border-blue-900/30 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between">
                <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-purple-950 border border-purple-500/30 text-purple-300">
                  Adversary Forgery
                </span>
                {mcData?.empirical_rate_le_bound ? (
                  <span className="flex items-center gap-1 text-[10px] font-mono text-emerald-400">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    Bound Holds
                  </span>
                ) : (
                  <span className="flex items-center gap-1 text-[10px] font-mono text-red-400">
                    <AlertCircle className="w-3.5 h-3.5" />
                    Exceeds
                  </span>
                )}
              </div>

              <h3 className="text-sm font-bold text-slate-200 mt-2">P(Forgery Accepted)</h3>
              <p className="text-[11px] text-slate-400 font-mono mt-0.5">
                Hoeffding Bound vs Empirical Born-Rule Sampling
              </p>
            </div>

            <div className="pt-4 border-t border-slate-800/80 space-y-2 text-xs font-mono">
              <div className="flex justify-between">
                <span className="text-slate-400">Analytical Bound:</span>
                <span className="text-purple-300 font-bold">
                  {hoeffdingData ? hoeffdingData.forgery_bound.toExponential(4) : '...'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Empirical Monte Carlo:</span>
                <span className="text-cyan-300 font-bold">
                  {mcData ? mcData.forgery.empirical_acceptance_rate?.toExponential(4) : '...'}
                </span>
              </div>
              <div className="flex justify-between text-[11px] text-slate-500">
                <span>95% Wilson Score CI:</span>
                <span>
                  [{mcData?.forgery.ci_95_lower?.toFixed(4)}, {mcData?.forgery.ci_95_upper?.toFixed(4)}]
                </span>
              </div>
            </div>
          </div>

          {/* Card 2: Honest False Rejection Rate */}
          <div className="p-5 rounded-xl bg-[#090e1a]/90 border border-blue-900/30 flex flex-col justify-between">
            <div>
              <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-emerald-950 border border-emerald-500/30 text-emerald-300">
                Honest Verification
              </span>
              <h3 className="text-sm font-bold text-slate-200 mt-2">P(False Rejection)</h3>
              <p className="text-[11px] text-slate-400 font-mono mt-0.5">
                Probability of legitimate signer being rejected due to noise
              </p>
            </div>

            <div className="pt-4 border-t border-slate-800/80 space-y-2 text-xs font-mono">
              <div className="flex justify-between">
                <span className="text-slate-400">Analytical Bound:</span>
                <span className="text-emerald-300 font-bold">
                  {hoeffdingData ? hoeffdingData.false_reject_bound.toExponential(4) : '...'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Empirical Rate:</span>
                <span className="text-cyan-300 font-bold">
                  {mcData ? mcData.false_reject.empirical_false_reject_rate?.toExponential(4) : '...'}
                </span>
              </div>
              <div className="flex justify-between text-[11px] text-slate-500">
                <span>95% Wilson Score CI:</span>
                <span>
                  [{mcData?.false_reject.ci_95_lower?.toFixed(4)}, {mcData?.false_reject.ci_95_upper?.toFixed(4)}]
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Parameter Sweeps Charts & Recharts Section */}
      <div className="p-5 rounded-xl bg-[#090e1a]/90 border border-blue-900/30 space-y-4">
        {/* Sweep Tabs Navigation */}
        <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-800 pb-3">
          <div className="flex flex-wrap items-center gap-1.5">
            <button
              onClick={() => setActiveTab('vs_L')}
              className={`px-3 py-1.5 rounded-lg text-xs font-mono transition-all cursor-pointer ${
                activeTab === 'vs_L'
                  ? 'bg-purple-600/30 text-purple-300 border border-purple-500/50 font-bold'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              1. Forgery vs Key Length (L)
            </button>
            <button
              onClick={() => setActiveTab('vs_threshold')}
              className={`px-3 py-1.5 rounded-lg text-xs font-mono transition-all cursor-pointer ${
                activeTab === 'vs_threshold'
                  ? 'bg-emerald-600/30 text-emerald-300 border border-emerald-500/50 font-bold'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              2. Forgery vs Threshold (s_a)
            </button>
            <button
              onClick={() => setActiveTab('vs_strategy')}
              className={`px-3 py-1.5 rounded-lg text-xs font-mono transition-all cursor-pointer ${
                activeTab === 'vs_strategy'
                  ? 'bg-cyan-600/30 text-cyan-300 border border-cyan-500/50 font-bold'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              3. Strategy Comparison
            </button>
            <button
              onClick={() => setActiveTab('vs_noise')}
              className={`px-3 py-1.5 rounded-lg text-xs font-mono transition-all cursor-pointer ${
                activeTab === 'vs_noise'
                  ? 'bg-amber-600/30 text-amber-300 border border-amber-500/50 font-bold'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              4. False Reject vs Noise
            </button>
            <button
              onClick={() => setActiveTab('roc')}
              className={`px-3 py-1.5 rounded-lg text-xs font-mono transition-all cursor-pointer ${
                activeTab === 'roc'
                  ? 'bg-blue-600/30 text-blue-300 border border-blue-500/50 font-bold'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              5. ROC Threshold Curve
            </button>
          </div>

          {activeTab === 'roc' && sweepsData?.roc_curve && (
            <span className="text-xs font-mono text-cyan-300 bg-cyan-950/60 px-2.5 py-1 rounded border border-cyan-500/40">
              AUC = {sweepsData.roc_curve.auc.toFixed(4)}
            </span>
          )}
        </div>

        {/* Chart Visualization Area */}
        <div className="h-80 w-full pt-2">
          {activeTab === 'vs_L' && sweepsData?.sweep_vs_L && (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={sweepsData.sweep_vs_L} margin={{ top: 10, right: 30, left: 10, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="L" stroke="#94a3b8" label={{ value: 'Signature Key Length L (qubit copies)', position: 'insideBottom', offset: -10, fill: '#64748b' }} />
                <YAxis stroke="#94a3b8" label={{ value: 'Probability', angle: -90, position: 'insideLeft', fill: '#64748b' }} />
                <Tooltip contentStyle={{ backgroundColor: '#090e1a', borderColor: '#334155' }} />
                <Legend verticalAlign="top" height={36} />
                <Line type="monotone" dataKey="hoeffding_bound" name="Analytical Hoeffding Bound" stroke="#c084fc" strokeWidth={2} dot={{ r: 4 }} />
                <Line type="monotone" dataKey="empirical_rate" name="Empirical Monte Carlo" stroke="#22d3ee" strokeWidth={2} dot={{ r: 4 }} />
              </LineChart>
            </ResponsiveContainer>
          )}

          {activeTab === 'vs_threshold' && sweepsData?.sweep_vs_threshold && (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={sweepsData.sweep_vs_threshold} margin={{ top: 10, right: 30, left: 10, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="s_a" stroke="#94a3b8" label={{ value: 'Acceptance Threshold s_a', position: 'insideBottom', offset: -10, fill: '#64748b' }} />
                <YAxis stroke="#94a3b8" label={{ value: 'Probability', angle: -90, position: 'insideLeft', fill: '#64748b' }} />
                <Tooltip contentStyle={{ backgroundColor: '#090e1a', borderColor: '#334155' }} />
                <Legend verticalAlign="top" height={36} />
                <Line type="monotone" dataKey="hoeffding_bound" name="Hoeffding Bound vs s_a" stroke="#10b981" strokeWidth={2} dot={{ r: 4 }} />
                <Line type="monotone" dataKey="empirical_rate" name="Empirical Rate" stroke="#06b6d4" strokeWidth={2} dot={{ r: 4 }} />
              </LineChart>
            </ResponsiveContainer>
          )}

          {activeTab === 'vs_strategy' && sweepsData?.sweep_vs_strategy && (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={sweepsData.sweep_vs_strategy} margin={{ top: 10, right: 30, left: 10, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="L" stroke="#94a3b8" label={{ value: 'Key Length L', position: 'insideBottom', offset: -10, fill: '#64748b' }} />
                <YAxis stroke="#94a3b8" label={{ value: 'Acceptance Probability Bound', angle: -90, position: 'insideLeft', fill: '#64748b' }} />
                <Tooltip contentStyle={{ backgroundColor: '#090e1a', borderColor: '#334155' }} />
                <Legend verticalAlign="top" height={36} />
                <Line type="monotone" dataKey="random_guess_bound" name="Random Guess (p_e=0.50)" stroke="#38bdf8" strokeWidth={2} />
                <Line type="monotone" dataKey="single_basis_bound" name="Single-Basis (p_e=0.33)" stroke="#a855f7" strokeWidth={2} />
                <Line type="monotone" dataKey="optimal_povm_bound" name="Optimal POVM (p_e=0.21)" stroke="#f43f5e" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          )}

          {activeTab === 'vs_noise' && sweepsData?.sweep_vs_noise && (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={sweepsData.sweep_vs_noise} margin={{ top: 10, right: 30, left: 10, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="p_h" stroke="#94a3b8" label={{ value: 'Channel Error Probability p_h', position: 'insideBottom', offset: -10, fill: '#64748b' }} />
                <YAxis stroke="#94a3b8" label={{ value: 'False Rejection Probability', angle: -90, position: 'insideLeft', fill: '#64748b' }} />
                <Tooltip contentStyle={{ backgroundColor: '#090e1a', borderColor: '#334155' }} />
                <Legend verticalAlign="top" height={36} />
                <Line type="monotone" dataKey="hoeffding_bound" name="False Reject Bound" stroke="#f59e0b" strokeWidth={2} dot={{ r: 4 }} />
                <Line type="monotone" dataKey="empirical_rate" name="Empirical False Rejections" stroke="#ef4444" strokeWidth={2} dot={{ r: 4 }} />
              </LineChart>
            </ResponsiveContainer>
          )}

          {activeTab === 'roc' && sweepsData?.roc_curve && (
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={sweepsData.roc_curve.curve_points} margin={{ top: 10, right: 30, left: 10, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="fpr" stroke="#94a3b8" label={{ value: 'False Positive Rate (P_forgery)', position: 'insideBottom', offset: -10, fill: '#64748b' }} />
                <YAxis stroke="#94a3b8" label={{ value: 'True Positive Rate (1 - P_false_reject)', angle: -90, position: 'insideLeft', fill: '#64748b' }} />
                <Tooltip contentStyle={{ backgroundColor: '#090e1a', borderColor: '#334155' }} />
                <Area type="monotone" dataKey="tpr" stroke="#3b82f6" fill="#1e3a8a" fillOpacity={0.4} name="ROC Curve (TPR vs FPR)" />
              </AreaChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>
    </div>
  );
};
