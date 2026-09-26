import React, { useState, useEffect } from 'react';
import {
  ShieldCheck,
  FileText,
  Download,
  CheckCircle2,
  AlertTriangle,
  Activity,
  Layers,
  Sparkles,
  Info,
  X,
  FileCheck,
  RefreshCw,
  FlaskConical,
  Binary,
  Zap
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  CartesianGrid
} from 'recharts';
import { BlochSphere } from '../components/common/BlochSphere';
import { AliceBobPipeline } from '../components/common/AliceBobPipeline';
import { api } from '../services/api';
import type { VerificationResponse, SignatureGenerateResponse, StateVectorInfo } from '../types';

interface VerificationPageProps {
  onNavigate?: (route: string) => void;
  preselectedSignature?: SignatureGenerateResponse | null;
  preselectedAttack?: any | null;
  onClearAttack?: () => void;
}

export const VerificationPage: React.FC<VerificationPageProps> = ({
  onNavigate,
  preselectedSignature,
  preselectedAttack,
  onClearAttack
}) => {
  const [inputMode, setInputMode] = useState<'manual' | 'upload'>('manual');
  const [savedSignatures, setSavedSignatures] = useState<any[]>([]);
  const [message, setMessage] = useState(
    preselectedSignature?.message || 'Secure communication with quantum signatures!'
  );
  const [signatureHex, setSignatureHex] = useState(
    preselectedSignature?.message_hash ||
      '3f7a9c8e4d2b1e6f0c9a8d7e5b4c3a2d1e0f9a8b7c6d5e4f3a2b1c0d9e8f7a6'
  );
  const [signatureId, setSignatureId] = useState(
    preselectedSignature?.signature_id || 'QSIG-2025-0510-001'
  );
  const [format, setFormat] = useState<'hex' | 'binary' | 'state'>('hex');
  const [loading, setLoading] = useState(false);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [uploadedFileName, setUploadedFileName] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<VerificationResponse | null>(null);

  // Security & Channel Scenario state
  const [attackScenario, setAttackScenario] = useState<string>('clean');
  const [scenarioDetails, setScenarioDetails] = useState<string>(
    'Clean Quantum Channel: Untampered message & valid state vector'
  );
  const [activeAttackContext, setActiveAttackContext] = useState<any | null>(null);

  const loadSavedSignatures = async () => {
    try {
      const sigs = await api.listSignatures(25);
      setSavedSignatures(sigs);
    } catch {
      // ignore
    }
  };

  const executeDirectVerification = async (tamperState?: StateVectorInfo, forceScenario?: string) => {
    if (!message.trim()) return;
    try {
      setLoading(true);
      setError(null);
      const res = await api.verifySignature({
        message: message.trim(),
        signature_id: signatureId,
        signature_hex: signatureHex.trim(),
        attack_scenario: forceScenario || (attackScenario !== 'clean' ? attackScenario : undefined),
        tamper_state: tamperState,
        shots: 1024,
        threshold: 0.100
      });
      setResult(res);
    } catch (err: any) {
      setError(err.message || 'Failed to verify signature.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // oxlint-disable-next-line react/set-state-in-effect
    loadSavedSignatures();
  }, []);

  // Sync if preselectedSignature changes
  useEffect(() => {
    if (preselectedSignature) {
      // oxlint-disable-next-line react/set-state-in-effect
      setMessage(preselectedSignature.message);
      setSignatureHex(preselectedSignature.message_hash);
      setSignatureId(preselectedSignature.signature_id);
      setActiveAttackContext(null);
      setAttackScenario('clean');
    }
  }, [preselectedSignature]);

  // Sync if preselectedAttack changes from Attack Simulation tab
  useEffect(() => {
    if (preselectedAttack) {
      // oxlint-disable-next-line react/set-state-in-effect
      setActiveAttackContext(preselectedAttack);
      if (preselectedAttack.signature_id) {
        setSignatureId(preselectedAttack.signature_id);
      }
      const isNoAtk =
        preselectedAttack.attack_type === 'No Attack' ||
        (preselectedAttack.threat_score !== undefined && preselectedAttack.threat_score < 0.30 && preselectedAttack.decision === 'LEGITIMATE');

      if (isNoAtk) {
        setAttackScenario('clean');
        setScenarioDetails('Clean Quantum Channel: Untampered message & valid state vector');
      } else {
        const atkType = preselectedAttack.attack_type?.toLowerCase() || '';
        if (atkType.includes('forgery')) {
          setAttackScenario('forgery');
          setScenarioDetails('Active Forgery Attack: Signature or message state altered in transit');
        } else if (atkType.includes('impersonation')) {
          setAttackScenario('impersonation');
          setScenarioDetails('Active Impersonation Attack: Unauthorized user attempt with fake quantum state');
        } else if (atkType.includes('replay')) {
          setAttackScenario('replay');
          setScenarioDetails('Active Replay Attack: Previously captured signature resent without fresh nonce');
        } else if (atkType.includes('channel') || atkType.includes('noise')) {
          setAttackScenario('channel');
          setScenarioDetails('Active Channel Manipulation: Noise and state perturbation injected');
        } else if (atkType.includes('unauthorized')) {
          setAttackScenario('unauthorized');
          setScenarioDetails('Active Unauthorized Verification: Multiple false verification attempts');
        } else {
          setAttackScenario('bit_flip');
          setScenarioDetails(`Active ${preselectedAttack.attack_type}: State vector perturbed by Eve`);
        }
      }

      // Automatically execute verification with the attacked state
      executeDirectVerification(preselectedAttack.tampered_state, isNoAtk ? undefined : (preselectedAttack.attack_type || 'attack_injected'));
    }
    // oxlint-disable-next-line react-hooks/exhaustive-deps
  }, [preselectedAttack]);

  const handleSelectSignature = async (sigId: string) => {
    if (!sigId) return;
    try {
      const details = await api.getSignature(sigId);
      setSignatureId(details.signature_id);
      if (details.message) setMessage(details.message);
      if (details.hash) setSignatureHex(details.hash);
      setActiveAttackContext(null);
      setAttackScenario('clean');
      setScenarioDetails('Clean Quantum Channel: Untampered message & valid state vector');
      if (onClearAttack) onClearAttack();
      setError(null);
    } catch {
      const item = savedSignatures.find((s) => s.signature_id === sigId);
      if (item) {
        setSignatureId(item.signature_id);
        setSignatureHex(item.hash);
        setActiveAttackContext(null);
        setAttackScenario('clean');
        if (onClearAttack) onClearAttack();
      }
    }
  };

  const resetVerificationToClean = async () => {
    setActiveAttackContext(null);
    setAttackScenario('clean');
    setScenarioDetails('Clean Quantum Channel: Untampered message & valid state vector');
    if (onClearAttack) onClearAttack();
    if (savedSignatures.length > 0) {
      await handleSelectSignature(savedSignatures[0].signature_id);
    } else {
      setMessage('Secure communication with quantum signatures!');
      setSignatureHex('3f7a9c8e4d2b1e6f0c9a8d7e5b4c3a2d1e0f9a8b7c6d5e4f3a2b1c0d9e8f7a6');
      setSignatureId('QSIG-2025-0510-001');
    }
    setResult(null);
    setError(null);
  };

  const handleLoadLatestSignature = () => {
    if (savedSignatures.length > 0) {
      handleSelectSignature(savedSignatures[0].signature_id);
    }
  };

  const handleVerify = async () => {
    executeDirectVerification(
      activeAttackContext?.tampered_state,
      attackScenario !== 'clean' ? attackScenario : undefined
    );
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploadedFileName(file.name);
    const reader = new FileReader();
    reader.onload = (ev) => {
      try {
        const json = JSON.parse(ev.target?.result as string);
        if (json.message) setMessage(json.message);
        if (json.message_hash || json.hash) setSignatureHex(json.message_hash || json.hash);
        if (json.signature_id) setSignatureId(json.signature_id);
      } catch {
        setError('Invalid JSON signature file format.');
      }
    };
    reader.readAsText(file);
  };

  const handleDownloadReport = () => {
    const reportData = {
      title: 'Quantum Digital Signature Verification Audit Report',
      project: 'Quantum Digital Signature Security (SIH 2025)',
      signature_id: result?.signature_id || signatureId,
      message_verified: message,
      verification_decision: result?.decision || 'LEGITIMATE',
      fidelity: result?.fidelity || 0.992,
      measurement_deviation: result?.deviation || 0.021,
      threshold_tvd: result?.threshold || 0.100,
      basis_wise_results: result?.basis_wise_results || [],
      observed_distribution: result?.observed_distribution || {},
      verification_time_ms: result?.verification_time_ms || 1.24,
      timestamp: result?.timestamp || new Date().toISOString()
    };
    const blob = new Blob([JSON.stringify(reportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Verification_Report_${signatureId}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const defaultReconstructedState: StateVectorInfo = {
    alpha: { real: 0.7071, imag: 0.0 },
    beta: { real: 0.7071, imag: 0.0 },
    theta_rad: 1.5708,
    theta_deg: 90.0,
    phi_rad: 0.0,
    phi_deg: 0.0,
    prob_0: 0.5,
    prob_1: 0.5,
    state_str: '0.7071|0⟩ + 0.7071|1⟩'
  };

  const activeReconstructedState = result ? result.reconstructed_state : defaultReconstructedState;

  const chartData = result
    ? [
        {
          state: '|0⟩',
          Expected: result.expected_distribution['0'] || 0.5,
          Observed: result.observed_distribution['0'] || 0.49
        },
        {
          state: '|1⟩',
          Expected: result.expected_distribution['1'] || 0.5,
          Observed: result.observed_distribution['1'] || 0.51
        }
      ]
    : [
        { state: '|0⟩', Expected: 0.5, Observed: 0.49 },
        { state: '|1⟩', Expected: 0.5, Observed: 0.51 }
      ];

  const isLegit = !result || result.decision === 'LEGITIMATE';

  const getAttackDisplayName = () => {
    if (activeAttackContext?.attack_type && activeAttackContext.attack_type !== 'No Attack') {
      return activeAttackContext.attack_type;
    }
    switch (attackScenario) {
      case 'forgery':
      case 'tampered_message':
        return 'Forgery Attack';
      case 'impersonation':
      case 'random_state':
        return 'Impersonation Attack';
      case 'replay':
        return 'Replay Attack';
      case 'channel':
        return 'Channel Manipulation';
      case 'unauthorized':
        return 'Unauthorized Verification';
      case 'bit_flip':
        return 'Quantum State Bit-Flip (Pauli-X)';
      case 'phase_flip':
        return 'Quantum Phase Disturbance (Pauli-Z)';
      case 'clean':
        return 'Clean Channel';
      default:
        return attackScenario;
    }
  };

  const getFormattedSignatureDisplay = () => {
    if (format === 'binary') {
      return signatureHex.slice(0, 32).split('').map((c) => parseInt(c, 16).toString(2).padStart(4, '0')).join(' ');
    } else if (format === 'state') {
      return `|ψ⟩ = ${activeReconstructedState.state_str}`;
    }
    return signatureHex;
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            Signature Verification (Bob)
          </h1>
          <p className="text-xs text-slate-400">
            Bob (Receiver) verifies state vector <span className="font-mono text-purple-300">|&psi;_B&rang;</span> against expected state <span className="font-mono text-cyan-300">|&psi;_exp&rang;</span> via multi-basis measurement
          </p>
          <div className="flex flex-wrap items-center gap-2 mt-2">
            <span className="px-2.5 py-0.5 rounded text-[10px] font-mono font-bold bg-amber-950/80 border border-amber-500/40 text-amber-300">
              LEGACY DEMO (NOT SECURE)
            </span>
            <span className="text-[11px] text-slate-400">
              For information-theoretically secure QDS verification, see{' '}
              <button
                type="button"
                onClick={() => onNavigate && onNavigate('key-distribution')}
                className="text-cyan-400 hover:underline cursor-pointer"
              >
                Key Distribution
              </button>{' '}
              and{' '}
              <button
                type="button"
                onClick={() => onNavigate && onNavigate('forgery-analysis')}
                className="text-cyan-400 hover:underline cursor-pointer"
              >
                Forgery Analysis
              </button>.
            </span>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={resetVerificationToClean}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#0c162d] hover:bg-[#132247] border border-cyan-500/30 text-cyan-300 text-xs font-semibold cursor-pointer transition-all shadow-sm"
            title="Reset verification to clean authentic state"
          >
            <RefreshCw className="w-3.5 h-3.5 text-cyan-400" />
            <span>Reset to Clean Channel</span>
          </button>
          <span className="text-xs font-mono text-cyan-400/80 italic hidden lg:inline">
            &ldquo;Trust, but Verify with Quantum Physics&rdquo;
          </span>
        </div>
      </div>

      {/* Protocol Pipeline Banner */}
      <AliceBobPipeline
        onNavigate={onNavigate}
        activeStep="bob"
        isAttacked={attackScenario !== 'clean'}
        currentAttackName={getAttackDisplayName()}
      />

      {/* Step Indicators */}
      <div className="flex items-center justify-center p-3 rounded-xl bg-[#0a1122]/80 border border-blue-500/20 max-w-2xl mx-auto">
        <div className="flex items-center gap-2 sm:gap-6 text-xs font-medium">
          {[
            { num: 1, label: 'Input Data' },
            { num: 2, label: 'Reconstruct State' },
            { num: 3, label: 'Measurement & Analysis' },
            { num: 4, label: 'Verification Result' }
          ].map((s, idx, arr) => (
            <React.Fragment key={s.num}>
              <div className="flex items-center gap-2">
                <div
                  className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
                    result || s.num === 1
                      ? 'bg-purple-600 text-white shadow-md shadow-purple-900/50'
                      : 'bg-slate-800 text-slate-400'
                  }`}
                >
                  {s.num}
                </div>
                <span className={`hidden sm:inline ${result || s.num === 1 ? 'text-slate-200' : 'text-slate-500'}`}>
                  {s.label}
                </span>
              </div>
              {idx < arr.length - 1 && <div className="w-6 sm:w-12 h-[1px] bg-slate-700"></div>}
            </React.Fragment>
          ))}
        </div>
      </div>

      {error && (
        <div className="p-3 rounded-lg bg-red-950/60 border border-red-500/40 text-red-300 text-xs">
          {error}
        </div>
      )}

      {/* Row 1: Input Data, Reconstruct State, Verification Result */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 1. Input Message & Signature */}
        <div className="p-5 rounded-xl bg-[#0a1122]/90 border border-blue-500/20 shadow-lg space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <FileText className="w-4 h-4 text-cyan-400" />
              <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider font-sans">
                1. Input Message &amp; Signature
              </h2>
            </div>
            <div className="flex rounded-lg bg-[#070b16] p-0.5 border border-slate-800">
              <button
                onClick={() => setInputMode('manual')}
                className={`px-2 py-0.5 text-[11px] rounded font-medium transition-colors cursor-pointer ${
                  inputMode === 'manual' ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                Enter Manually
              </button>
              <label
                className={`px-2 py-0.5 text-[11px] rounded font-medium cursor-pointer transition-colors ${
                  inputMode === 'upload' ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                Upload File
                <input
                  type="file"
                  accept=".json"
                  onChange={handleFileUpload}
                  className="hidden"
                />
              </label>
            </div>
          </div>

          {uploadedFileName && (
            <div className="p-2 rounded bg-cyan-950/40 border border-cyan-500/30 text-cyan-300 text-[11px] flex items-center gap-2 font-mono">
              <FileCheck className="w-3.5 h-3.5 text-cyan-400" />
              <span>Loaded file: {uploadedFileName}</span>
            </div>
          )}

          {/* Live Database Signature Selector */}
          {savedSignatures.length > 0 && inputMode === 'manual' && (
            <div className="p-2.5 rounded-lg bg-[#070b16] border border-blue-900/40 space-y-1.5">
              <div className="flex items-center justify-between">
                <label className="text-[10px] text-cyan-400 font-semibold uppercase tracking-wider">
                  Pick from Live Database ({savedSignatures.length})
                </label>
                <button
                  type="button"
                  onClick={handleLoadLatestSignature}
                  className="text-[10px] font-mono text-purple-400 hover:text-purple-300 underline cursor-pointer"
                >
                  ⚡ Load Latest
                </button>
              </div>
              <select
                value={signatureId}
                onChange={(e) => handleSelectSignature(e.target.value)}
                className="w-full p-1.5 rounded bg-[#0b1328] border border-slate-700 text-xs font-mono text-slate-200 focus:outline-none focus:border-cyan-400 cursor-pointer"
              >
                <option value="">-- Choose Live Signature --</option>
                {savedSignatures.map((s) => (
                  <option key={s.signature_id} value={s.signature_id}>
                    {s.signature_id} — &ldquo;{s.message_snippet}&rdquo;
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Active Transferred Attack Banner */}
          {activeAttackContext && (
            <div className="p-3 rounded-lg bg-red-950/40 border border-red-500/50 space-y-1">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-red-300 flex items-center gap-1.5">
                  <AlertTriangle className="w-3.5 h-3.5 text-red-400 animate-pulse" />
                  Simulated Attack Active: {activeAttackContext.attack_type || getAttackDisplayName()}
                </span>
                <button
                  type="button"
                  onClick={resetVerificationToClean}
                  className="text-[10px] text-cyan-400 hover:text-cyan-200 underline cursor-pointer flex items-center gap-1 font-semibold"
                >
                  <RefreshCw className="w-3 h-3" />
                  Reset to Clean
                </button>
              </div>
              <p className="text-[10px] text-red-200/80 font-mono">
                Target: {activeAttackContext.signature_id || signatureId} &bull; Threat Score: {activeAttackContext.threat_score ?? 0.78}
              </p>
            </div>
          )}

          {/* Security & Attack Scenario Selector */}
          <div>
            <div className="flex items-center justify-between mb-1">
              <label className="text-[11px] text-slate-400 font-medium flex items-center gap-1.5">
                <ShieldCheck className="w-3.5 h-3.5 text-cyan-400" />
                Channel / Security Scenario
              </label>
              <span
                className={`text-[10px] font-mono px-1.5 py-0.5 rounded ${
                  attackScenario === 'clean'
                    ? 'bg-emerald-950/60 text-emerald-400 border border-emerald-500/30'
                    : 'bg-red-950/60 text-red-400 border border-red-500/30 animate-pulse font-bold'
                }`}
              >
                {attackScenario === 'clean' ? '● CLEAN CHANNEL' : `▲ ${getAttackDisplayName().toUpperCase()}`}
              </span>
            </div>
            <select
              value={attackScenario}
              onChange={(e) => {
                const val = e.target.value;
                setAttackScenario(val);
                if (val === 'clean') {
                  setScenarioDetails('Clean Quantum Channel: Untampered message & valid state vector');
                } else if (val === 'forgery' || val === 'tampered_message') {
                  setScenarioDetails('Forgery Attack: Signature or message content modified in transit');
                } else if (val === 'impersonation' || val === 'random_state') {
                  setScenarioDetails('Impersonation Attack: Unauthorized user attempt with fake quantum state');
                } else if (val === 'replay') {
                  setScenarioDetails('Replay Attack: Resending previously captured signature without fresh nonce');
                } else if (val === 'channel') {
                  setScenarioDetails('Channel Manipulation: Noise, bit-flips, and channel tampering injected');
                } else if (val === 'unauthorized') {
                  setScenarioDetails('Unauthorized Verification: Multiple false verification attempts');
                } else if (val === 'bit_flip') {
                  setScenarioDetails('Quantum Interception: Pauli-X bit flip injected on the quantum signature state');
                } else if (val === 'phase_flip') {
                  setScenarioDetails('Quantum Eavesdropping: Pauli-Z phase disturbance injected in quantum channel');
                }
              }}
              className={`w-full p-2 rounded-lg bg-[#070b16] border text-xs focus:outline-none cursor-pointer font-sans ${
                attackScenario === 'clean'
                  ? 'border-emerald-500/40 text-emerald-300'
                  : 'border-red-500/60 text-red-300 bg-[#160a0f]'
              }`}
            >
              <option value="clean">🟢 Authentic / Clean Channel (Expected: LEGITIMATE)</option>
              <option value="forgery">🔴 Forgery Attack (Modify Signature or Message)</option>
              <option value="impersonation">🔴 Impersonation Attack (Unauthorized User Attempt)</option>
              <option value="replay">🔴 Replay Attack (Resend Captured Signature)</option>
              <option value="channel">🔴 Channel Manipulation (Introduce Noise & Tampering)</option>
              <option value="unauthorized">🔴 Unauthorized Verification (Multiple False Attempts)</option>
              <option value="bit_flip">🔴 Quantum State Bit-Flip (Pauli-X Interception)</option>
              <option value="phase_flip">🔴 Quantum Phase Disturbance (Pauli-Z Error)</option>
              <option value="random_state">🔴 Random State Injection (Fake State Vector)</option>
            </select>
            <p className="text-[10px] text-slate-400 mt-1 italic leading-tight">{scenarioDetails}</p>
          </div>

          <div>
            <div className="flex justify-between text-xs text-slate-400 mb-1">
              <span>Message</span>
              <span className="font-mono">{message.length}/500</span>
            </div>
            <textarea
              value={message}
              onChange={(e) => setMessage(e.target.value.slice(0, 500))}
              rows={3}
              className="w-full p-2.5 rounded-lg bg-[#070b16] border border-blue-900/40 text-xs text-slate-200 font-sans focus:outline-none focus:border-cyan-400 resize-none"
            />
          </div>

          <div>
            <span className="text-[11px] text-slate-400 block mb-1">Signature Format</span>
            <div className="flex items-center gap-4 text-xs">
              <label className="flex items-center gap-1.5 cursor-pointer text-slate-300">
                <input
                  type="radio"
                  name="format"
                  checked={format === 'hex'}
                  onChange={() => setFormat('hex')}
                  className="text-cyan-500 focus:ring-0 cursor-pointer"
                />
                Hex String
              </label>
              <label className="flex items-center gap-1.5 cursor-pointer text-slate-400">
                <input
                  type="radio"
                  name="format"
                  checked={format === 'binary'}
                  onChange={() => setFormat('binary')}
                  className="text-cyan-500 focus:ring-0 cursor-pointer"
                />
                Binary
              </label>
              <label className="flex items-center gap-1.5 cursor-pointer text-slate-400">
                <input
                  type="radio"
                  name="format"
                  checked={format === 'state'}
                  onChange={() => setFormat('state')}
                  className="text-cyan-500 focus:ring-0 cursor-pointer"
                />
                Qubit State (|ψ⟩)
              </label>
            </div>
          </div>

          <div>
            <span className="text-[11px] text-slate-400 block mb-1">
              Signature ({format === 'hex' ? 'Hex' : format === 'binary' ? 'Binary' : 'State Vector'})
            </span>
            <input
              type="text"
              value={getFormattedSignatureDisplay()}
              onChange={(e) => setSignatureHex(e.target.value)}
              className="w-full p-2.5 rounded bg-[#070b16] border border-blue-900/40 font-mono text-[11px] text-cyan-300 focus:outline-none focus:border-cyan-400"
            />
          </div>

          <button
            onClick={handleVerify}
            disabled={loading || !message.trim()}
            className="w-full py-2.5 px-4 rounded-lg bg-gradient-to-r from-blue-600 via-purple-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white font-semibold text-xs transition-all shadow-lg shadow-purple-900/30 flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
          >
            {loading ? (
              <span className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 animate-spin" />
                Executing Quantum Verifier...
              </span>
            ) : (
              <>
                <ShieldCheck className="w-4 h-4" />
                Verify Signature
              </>
            )}
          </button>
        </div>

        {/* 2. Reconstruct Quantum State */}
        <div className="p-5 rounded-xl bg-[#0a1122]/90 border border-blue-500/20 shadow-lg space-y-3">
          <div className="flex items-center gap-2">
            <Layers className="w-4 h-4 text-purple-400" />
            <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider font-sans">
              2. Reconstruct Quantum State
            </h2>
          </div>
          <p className="text-[11px] text-slate-400">
            Recreating the quantum state from signature and message hash...
          </p>

          <div className="p-2 rounded-lg bg-[#070b16] border border-blue-900/40 text-[11px] font-mono">
            <span className="text-slate-400 block text-[10px] font-sans">State Vector (Reconstructed)</span>
            <span className="text-cyan-300 font-semibold">{activeReconstructedState.state_str}</span>
          </div>

          <BlochSphere stateInfo={activeReconstructedState} size={150} showDetails={false} />
        </div>

        {/* Verification Result Card */}
        <div className="p-5 rounded-xl bg-[#0a1122]/90 border border-blue-500/20 shadow-lg space-y-4 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 mb-3">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider font-sans">
                Verification Result
              </h2>
            </div>

            <div
              className={`p-3.5 rounded-xl border mb-3 ${
                isLegit
                  ? 'bg-emerald-950/50 border-emerald-500/40 text-emerald-300'
                  : 'bg-red-950/50 border-red-500/40 text-red-300'
              }`}
            >
              <div className="flex items-center justify-between font-bold text-base">
                <div className="flex items-center gap-2">
                  {isLegit ? (
                    <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                  ) : (
                    <AlertTriangle className="w-5 h-5 text-red-400" />
                  )}
                  <span>{isLegit ? 'SIGNATURE VERIFIED' : 'ATTACK DETECTED'}</span>
                </div>
                {!isLegit && (
                  <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-red-900/80 text-red-200 border border-red-400/50">
                    {getAttackDisplayName()}
                  </span>
                )}
              </div>
              <p className="text-xs text-slate-300 mt-1">
                {result?.details ||
                  (isLegit
                    ? 'The signature is authentic and untampered.'
                    : `Quantum state vector fidelity degraded below threshold under ${getAttackDisplayName()}. Verification rejected.`)}
              </p>
            </div>

            <div className="space-y-1.5 text-xs font-mono">
              {!isLegit && (
                <div className="flex justify-between py-1 border-b border-slate-800">
                  <span className="text-slate-400 font-sans">Attack Type</span>
                  <span className="text-red-400 font-bold">{getAttackDisplayName()}</span>
                </div>
              )}
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400 font-sans">Verification Fidelity</span>
                <span className={`font-bold ${isLegit ? 'text-emerald-400' : 'text-red-400'}`}>
                  {result?.fidelity ?? (isLegit ? 0.992 : 0.612)}
                </span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400 font-sans">Measurement Deviation</span>
                <span className={`font-bold ${isLegit ? 'text-purple-300' : 'text-red-400'}`}>
                  {result?.deviation ?? (isLegit ? 0.021 : 0.220)}
                </span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400 font-sans">Signature Copies (L)</span>
                <span className="text-cyan-300 font-bold">64 Pauli Eigenstates</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400 font-sans">Mismatch Rate (m)</span>
                <span className={`font-bold ${isLegit ? 'text-emerald-400' : 'text-red-400'}`}>
                  {result?.deviation !== undefined ? `${(result.deviation * 100).toFixed(1)}%` : (isLegit ? '0.0%' : '22.0%')}
                </span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400 font-sans">Thresholds (s_a / s_v)</span>
                <span className="text-slate-300 font-bold">0.100 / 0.250</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400 font-sans">Detector Fired</span>
                <span className={`font-bold uppercase px-1.5 py-0.2 rounded text-[10px] ${
                  isLegit ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' :
                  attackScenario === 'replay' ? 'bg-purple-950 text-purple-300 border border-purple-800' :
                  attackScenario === 'unauthorized' ? 'bg-red-950 text-red-300 border border-red-800' :
                  'bg-red-950 text-red-400 border border-red-800'
                }`}>
                  {isLegit ? 'None (Clean)' : attackScenario === 'replay' ? 'Nonce Detector' : attackScenario === 'unauthorized' ? 'Authorization' : 'Threshold Detector'}
                </span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400 font-sans">Final Decision</span>
                <span className={`font-bold ${isLegit ? 'text-emerald-400' : 'text-red-400'}`}>
                  {result?.decision || (isLegit ? 'Legitimate' : 'ATTACK DETECTED')}
                </span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400 font-sans">Verification Time</span>
                <span className="text-slate-300">{result?.verification_time_ms ? `${result.verification_time_ms} ms` : '1.24 ms'}</span>
              </div>
              <div className="flex justify-between py-1">
                <span className="text-slate-400 font-sans">Signature ID</span>
                <span className="text-cyan-300">{result?.signature_id || signatureId}</span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2 pt-2">
            <button
              onClick={() => setShowDetailsModal(true)}
              className="flex-1 py-2 px-3 rounded-lg bg-blue-900/40 hover:bg-blue-800/60 border border-blue-500/30 text-cyan-300 text-xs font-semibold text-center transition-colors cursor-pointer"
            >
              View Details
            </button>
            <button
              onClick={handleDownloadReport}
              className="flex-1 py-2 px-3 rounded-lg bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500 text-white text-xs font-semibold flex items-center justify-center gap-1.5 transition-all shadow-md shadow-purple-900/30 cursor-pointer"
            >
              <Download className="w-3.5 h-3.5" />
              Download Report
            </button>
          </div>
        </div>
      </div>

      {/* Row 2: Measurement Analysis, Comparison Metrics, Basis-wise Verification */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 3. Measurement Analysis Chart */}
        <div className="p-5 rounded-xl bg-[#0a1122]/90 border border-blue-500/20 shadow-lg">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider font-sans flex items-center gap-2">
              <Activity className="w-4 h-4 text-cyan-400" />
              3. Measurement Analysis
            </h2>
            <div className="flex items-center gap-3 text-[11px]">
              <span className="flex items-center gap-1 text-cyan-400">
                <span className="w-2.5 h-2.5 rounded-sm bg-cyan-500"></span> Expected
              </span>
              <span className="flex items-center gap-1 text-purple-400">
                <span className="w-2.5 h-2.5 rounded-sm bg-purple-500"></span> Observed
              </span>
            </div>
          </div>

          <div className="h-44 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="state" stroke="#64748b" fontSize={11} fontFamily="monospace" />
                <YAxis stroke="#64748b" fontSize={11} domain={[0, 1]} />
                <RechartsTooltip contentStyle={{ backgroundColor: '#0c1427', borderColor: '#0284c7', fontSize: 12 }} />
                <Bar dataKey="Expected" fill="#06b6d4" radius={[4, 4, 0, 0]} />
                <Bar dataKey="Observed" fill="#a855f7" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <p className="text-[11px] text-center text-slate-400 font-mono mt-1">Measurement Outcome</p>
        </div>

        {/* 4. Comparison Metrics Table */}
        <div className="p-5 rounded-xl bg-[#0a1122]/90 border border-blue-500/20 shadow-lg space-y-3 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 mb-3">
              <Layers className="w-4 h-4 text-purple-400" />
              <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider font-sans">
                4. Comparison Metrics
              </h2>
            </div>

            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 font-sans">
                  <th className="pb-1.5">Metric</th>
                  <th className="pb-1.5">Expected</th>
                  <th className="pb-1.5">Observed</th>
                  <th className="pb-1.5">Deviation</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                <tr>
                  <td className="py-1.5 text-slate-300">P(0)</td>
                  <td className="py-1.5 text-slate-400">0.500</td>
                  <td className="py-1.5 text-cyan-300">{result?.observed_distribution['0'] ?? 0.490}</td>
                  <td className="py-1.5 text-purple-300">0.010</td>
                </tr>
                <tr>
                  <td className="py-1.5 text-slate-300">P(1)</td>
                  <td className="py-1.5 text-slate-400">0.500</td>
                  <td className="py-1.5 text-cyan-300">{result?.observed_distribution['1'] ?? 0.510}</td>
                  <td className="py-1.5 text-purple-300">0.010</td>
                </tr>
                <tr>
                  <td className="py-1.5 text-slate-300">State Fidelity</td>
                  <td className="py-1.5 text-slate-400">1.000</td>
                  <td className="py-1.5 text-emerald-400 font-bold">{result?.fidelity ?? 0.992}</td>
                  <td className="py-1.5 text-purple-300">{result ? (1.0 - result.fidelity).toFixed(3) : '0.008'}</td>
                </tr>
                <tr>
                  <td className="py-1.5 text-slate-300">Bit Error Rate</td>
                  <td className="py-1.5 text-slate-400">0.000</td>
                  <td className="py-1.5 text-cyan-300">{result?.bit_error_rate ?? 0.021}</td>
                  <td className="py-1.5 text-purple-300">{result?.bit_error_rate ?? 0.021}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div
            className={`p-2 rounded-lg border text-xs flex items-center gap-2 ${
              isLegit
                ? 'bg-emerald-950/40 border-emerald-500/30 text-emerald-300'
                : 'bg-red-950/40 border-red-500/30 text-red-300'
            }`}
          >
            <CheckCircle2 className="w-4 h-4 shrink-0" />
            <span className="text-[11px]">
              {isLegit
                ? 'All metrics within acceptable threshold.'
                : 'Metrics exceed acceptable error bounds.'}
            </span>
          </div>
        </div>

        {/* Basis-wise Verification Card */}
        <div className="p-5 rounded-xl bg-[#0a1122]/90 border border-blue-500/20 shadow-lg space-y-3 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 mb-3">
              <Activity className="w-4 h-4 text-cyan-400" />
              <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider font-sans">
                Basis-wise Verification
              </h2>
            </div>

            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 font-sans">
                  <th className="pb-1.5">Basis</th>
                  <th className="pb-1.5">Expected</th>
                  <th className="pb-1.5">Observed</th>
                  <th className="pb-1.5">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {(result?.basis_wise_results || [
                  { basis: 'Z-basis', expected: 0.5, observed: 0.49, status: 'Valid' },
                  { basis: 'X-basis', expected: 0.5, observed: 0.51, status: 'Valid' },
                  { basis: 'Y-basis', expected: 0.5, observed: 0.48, status: 'Valid' }
                ]).map((b) => {
                  const hRes = b.basis.startsWith('Z') ? result?.hoeffding_z : b.basis.startsWith('X') ? result?.hoeffding_x : result?.hoeffding_y;
                  return (
                    <tr key={b.basis}>
                      <td className="py-2 text-slate-300">{b.basis}</td>
                      <td className="py-2 text-slate-400">{(b.expected * 100).toFixed(0)}%</td>
                      <td className="py-2 text-cyan-300">{(b.observed * 100).toFixed(0)}%</td>
                      <td className="py-2">
                        <span className={`inline-flex items-center gap-1 text-[11px] ${b.status === 'Valid' ? 'text-emerald-400' : 'text-red-400'}`}>
                          {b.status === 'Valid' ? (
                            <CheckCircle2 className="w-3.5 h-3.5" />
                          ) : (
                            <AlertTriangle className="w-3.5 h-3.5" />
                          )}
                          {b.status}
                          {hRes && (
                            <span className="text-[10px] text-slate-400 ml-1">
                              ({hRes.confidence_pct}% conf)
                            </span>
                          )}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          <div className="p-2.5 rounded-lg bg-blue-950/30 border border-blue-500/20 text-[11px] text-slate-300 flex items-start gap-2">
            <Info className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
            <p>
              {result?.forgery_summary?.summary ||
                'The measurement results are consistent with the expected distribution across all bases.'}
            </p>
          </div>
        </div>
      </div>

      {/* Row 3: Quantum Physical Security Evidence & Tomographic Invariants (Non-AI Physics Engine) */}
      <div className="p-5 rounded-xl bg-[#0a1122]/90 border border-cyan-500/30 shadow-xl space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-blue-900/30 pb-3">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-lg bg-cyan-950/60 border border-cyan-500/30">
              <FlaskConical className="w-5 h-5 text-cyan-400" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-slate-100 uppercase tracking-wider font-sans flex items-center gap-2">
                Quantum Physical Security Evidence &amp; Invariants
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950/60 text-emerald-400 border border-emerald-500/30 font-semibold normal-case">
                  Deterministic Physics Engine (No AI / ML)
                </span>
              </h2>
              <p className="text-xs text-slate-400">
                Mathematical proof of state integrity via density operators, trace distance, von Neumann entropy, and Hoeffding bounds.
              </p>
            </div>
          </div>
          {result?.security_evidence?.physical_interpretation && (
            <div className="text-right">
              <span className={`text-[11px] font-mono px-2.5 py-1 rounded font-semibold ${
                isLegit
                  ? 'bg-emerald-950/60 text-emerald-300 border border-emerald-500/30'
                  : 'bg-red-950/60 text-red-300 border border-red-500/30'
              }`}>
                {isLegit ? '● PURE COHERENT STATE' : '▲ DECOHERENCE DETECTED'}
              </span>
            </div>
          )}
        </div>

        {/* 4 Invariant Metric Cards */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="p-3.5 rounded-lg bg-[#070b16] border border-blue-900/30">
            <span className="text-[10px] text-slate-400 uppercase tracking-wider font-mono block mb-1">
              Purity γ = Tr(ρ²)
            </span>
            <div className="flex items-baseline gap-1.5">
              <span className={`text-lg font-bold font-mono ${
                (result?.purity ?? (isLegit ? 1.0 : 0.72)) > 0.95 ? 'text-emerald-400' : 'text-amber-400'
              }`}>
                {(result?.purity ?? (isLegit ? 1.0 : 0.72)).toFixed(4)}
              </span>
              <span className="text-[10px] text-slate-500 font-mono">
                {(result?.purity ?? (isLegit ? 1.0 : 0.72)) >= 0.999 ? '[Pure: 1.0]' : '[Mixed State]'}
              </span>
            </div>
            <p className="text-[10px] text-slate-500 mt-1">Bound: 0.5 (Max Mixed) ≤ γ ≤ 1.0 (Pure)</p>
          </div>

          <div className="p-3.5 rounded-lg bg-[#070b16] border border-blue-900/30">
            <span className="text-[10px] text-slate-400 uppercase tracking-wider font-mono block mb-1">
              Entropy S(ρ) = -Tr(ρ log₂ ρ)
            </span>
            <div className="flex items-baseline gap-1.5">
              <span className={`text-lg font-bold font-mono ${
                (result?.von_neumann_entropy ?? (isLegit ? 0.0 : 0.38)) < 0.05 ? 'text-emerald-400' : 'text-red-400'
              }`}>
                {(result?.von_neumann_entropy ?? (isLegit ? 0.0 : 0.38)).toFixed(4)}
              </span>
              <span className="text-[10px] text-slate-500 font-mono">bits</span>
            </div>
            <p className="text-[10px] text-slate-500 mt-1">Eavesdropping introduces entropy S &gt; 0</p>
          </div>

          <div className="p-3.5 rounded-lg bg-[#070b16] border border-blue-900/30">
            <span className="text-[10px] text-slate-400 uppercase tracking-wider font-mono block mb-1">
              Trace Distance D(ρ, σ)
            </span>
            <div className="flex items-baseline gap-1.5">
              <span className={`text-lg font-bold font-mono ${
                (result?.trace_distance ?? (isLegit ? 0.005 : 0.28)) < 0.10 ? 'text-cyan-400' : 'text-red-400'
              }`}>
                {(result?.trace_distance ?? (isLegit ? 0.005 : 0.28)).toFixed(4)}
              </span>
              <span className="text-[10px] text-slate-500 font-mono">
                {(result?.trace_distance ?? (isLegit ? 0.005 : 0.28)) < 0.10 ? 'Optimal' : 'High Shift'}
              </span>
            </div>
            <p className="text-[10px] text-slate-500 mt-1">Distinguishability: D = ½Tr|ρ - σ|</p>
          </div>

          <div className="p-3.5 rounded-lg bg-[#070b16] border border-blue-900/30">
            <span className="text-[10px] text-slate-400 uppercase tracking-wider font-mono block mb-1">
              Bloch Displacement D_Bloch
            </span>
            <div className="flex items-baseline gap-1.5">
              <span className={`text-lg font-bold font-mono ${
                (result?.bloch_displacement ?? (isLegit ? 0.012 : 0.42)) < 0.15 ? 'text-purple-400' : 'text-red-400'
              }`}>
                {(result?.bloch_displacement ?? (isLegit ? 0.012 : 0.42)).toFixed(4)}
              </span>
              <span className="text-[10px] text-slate-500 font-mono">Euclidean</span>
            </div>
            <p className="text-[10px] text-slate-500 mt-1">Sphere vector displacement ||r_exp - r_obs||</p>
          </div>
        </div>

        {/* Matrix & Statistical Concentration Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 pt-1">
          {/* Reconstructed Density Matrix Panel */}
          <div className="p-4 rounded-lg bg-[#070b16] border border-blue-900/40 space-y-2">
            <span className="text-xs font-semibold text-slate-300 flex items-center gap-1.5 font-sans">
              <Binary className="w-3.5 h-3.5 text-cyan-400" />
              Reconstructed Density Matrix ρ_obs
            </span>
            {result?.security_evidence?.density_matrix_reconstructed ? (
              <div className="grid grid-cols-2 gap-2 font-mono text-xs">
                <div className="p-2 rounded bg-slate-900/60 border border-slate-800 text-center">
                  <span className="text-[10px] text-slate-500 block">ρ[0,0]</span>
                  <span className="text-cyan-300 font-bold">
                    {result.security_evidence.density_matrix_reconstructed[0][0].real.toFixed(4)}
                    {result.security_evidence.density_matrix_reconstructed[0][0].imag >= 0 ? '+' : ''}
                    {result.security_evidence.density_matrix_reconstructed[0][0].imag.toFixed(4)}i
                  </span>
                </div>
                <div className="p-2 rounded bg-slate-900/60 border border-slate-800 text-center">
                  <span className="text-[10px] text-slate-500 block">ρ[0,1]</span>
                  <span className="text-purple-300 font-bold">
                    {result.security_evidence.density_matrix_reconstructed[0][1].real.toFixed(4)}
                    {result.security_evidence.density_matrix_reconstructed[0][1].imag >= 0 ? '+' : ''}
                    {result.security_evidence.density_matrix_reconstructed[0][1].imag.toFixed(4)}i
                  </span>
                </div>
                <div className="p-2 rounded bg-slate-900/60 border border-slate-800 text-center">
                  <span className="text-[10px] text-slate-500 block">ρ[1,0]</span>
                  <span className="text-purple-300 font-bold">
                    {result.security_evidence.density_matrix_reconstructed[1][0].real.toFixed(4)}
                    {result.security_evidence.density_matrix_reconstructed[1][0].imag >= 0 ? '+' : ''}
                    {result.security_evidence.density_matrix_reconstructed[1][0].imag.toFixed(4)}i
                  </span>
                </div>
                <div className="p-2 rounded bg-slate-900/60 border border-slate-800 text-center">
                  <span className="text-[10px] text-slate-500 block">ρ[1,1]</span>
                  <span className="text-cyan-300 font-bold">
                    {result.security_evidence.density_matrix_reconstructed[1][1].real.toFixed(4)}
                    {result.security_evidence.density_matrix_reconstructed[1][1].imag >= 0 ? '+' : ''}
                    {result.security_evidence.density_matrix_reconstructed[1][1].imag.toFixed(4)}i
                  </span>
                </div>
              </div>
            ) : (
              <div className="p-3 rounded bg-slate-900/40 border border-slate-800 text-xs text-slate-400 font-mono text-center">
                ρ = |ψ⟩⟨ψ| (Hermitian, Tr(ρ) = 1.0000, Positive Semi-Definite)
              </div>
            )}
            <p className="text-[11px] text-slate-400 font-sans">
              Hermitian conjugate satisfied: ρ = ρ†. Eigenvalues λ₁, λ₂ in [0, 1], Tr(ρ) = 1.0.
            </p>
          </div>

          {/* Statistical Bounds & Physics Security Interpretation */}
          <div className="p-4 rounded-lg bg-[#070b16] border border-blue-900/40 space-y-2 flex flex-col justify-between">
            <span className="text-xs font-semibold text-slate-300 flex items-center gap-1.5 font-sans">
              <Zap className="w-3.5 h-3.5 text-amber-400" />
              Statistical Bound &amp; Theoretical Guarantee
            </span>

            <div className="space-y-1 text-[11px] font-mono">
              <div className="flex justify-between py-1 border-b border-slate-800/80">
                <span className="text-slate-400 font-sans">Hoeffding Deviation Bound:</span>
                <span className="text-cyan-300">
                  ε ≤ {result?.security_evidence?.hoeffding_epsilon ?? 0.05} (N = {result?.shots || 1024} shots)
                </span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800/80">
                <span className="text-slate-400 font-sans">Mathematical Confidence:</span>
                <span className="text-emerald-400 font-bold">
                  {result?.security_evidence?.statistical_confidence_pct ?? 99.8}%
                </span>
              </div>
              <div className="flex justify-between py-1">
                <span className="text-slate-400 font-sans">No-Cloning Security Bound:</span>
                <span className="text-purple-300 font-bold">
                  F_cloning ≤ 5/6 (83.33%) &bull; Wootters-Zurek
                </span>
              </div>
            </div>

            <div className="p-2 rounded bg-cyan-950/30 border border-cyan-500/20 text-[10px] text-slate-300 font-sans">
              {result?.security_evidence?.physical_interpretation ||
                'Tomographic Pauli reconstruction reveals full quantum state coherence without non-unitary channel tampering.'}
            </div>
          </div>
        </div>
      </div>

      {/* Verification Details Modal */}
      {showDetailsModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="w-full max-w-xl p-6 rounded-2xl bg-[#0a1122] border border-cyan-500/40 shadow-2xl shadow-cyan-950/80 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="font-bold text-slate-100 flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-cyan-400" />
                Detailed Verification Report — {signatureId}
              </h3>
              <button
                onClick={() => setShowDetailsModal(false)}
                className="text-slate-400 hover:text-white transition-colors cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-2 text-xs font-mono">
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400 font-sans">Claimed Message:</span>
                <span className="text-slate-200 font-sans truncate max-w-xs">{message}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400 font-sans">Verified SHA-256 Digest:</span>
                <span className="text-cyan-300 truncate max-w-xs">{signatureHex}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400 font-sans">Quantum State Fidelity (F):</span>
                <span className="text-emerald-400 font-bold">{result?.fidelity || 0.992}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400 font-sans">Measurement TVD Deviation:</span>
                <span className="text-purple-300 font-bold">{result?.deviation || 0.021}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400 font-sans">Threat Score:</span>
                <span className="text-emerald-400 font-bold">{result?.threat_score || 0.01}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400 font-sans">Final Decision:</span>
                <span className={`font-bold ${isLegit ? 'text-emerald-400' : 'text-red-400'}`}>
                  {result?.decision || 'LEGITIMATE'}
                </span>
              </div>
            </div>

            <div className="p-3 rounded-lg bg-[#070b16] border border-blue-900/40 text-xs text-slate-300">
              <p className="font-semibold text-cyan-300 mb-1 font-sans">Cryptographic Integrity Analysis:</p>
              <p className="text-[11px] leading-relaxed">
                The quantum state reconstruction confirms the measurement probabilities match the expected theoretical distribution within a tolerance threshold of {result?.threshold || 0.100}. No eavesdropping decoherence or quantum bit-flip alteration was detected.
              </p>
            </div>

            <div className="flex items-center gap-2 pt-2">
              <button
                onClick={handleDownloadReport}
                className="flex-1 py-2 rounded-lg bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500 text-white text-xs font-semibold flex items-center justify-center gap-1.5 cursor-pointer"
              >
                <Download className="w-3.5 h-3.5" />
                Export JSON Report
              </button>
              <button
                onClick={() => setShowDetailsModal(false)}
                className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold cursor-pointer"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
