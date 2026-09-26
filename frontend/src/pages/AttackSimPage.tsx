import React, { useState, useEffect } from 'react';
import {
  ShieldAlert,
  ShieldCheck,
  UserX,
  RotateCcw,
  Radio,
  Lock,
  Play,
  AlertTriangle,
  Activity,
  Layers,
  Sparkles,
  Sliders,
  Settings2,
  FileText,
  CheckCircle2,
  Database,
  RefreshCw
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
import type { AttackSimulateResponse, StateVectorInfo, SignatureListItem } from '../types';

interface AttackSimPageProps {
  onNavigate?: (route: string) => void;
  onSelectAttackForVerify?: (attackResult: AttackSimulateResponse) => void;
  activeAttack?: AttackSimulateResponse | null;
  onUpdateAttack?: (attackResult: AttackSimulateResponse) => void;
}

export const AttackSimPage: React.FC<AttackSimPageProps> = ({
  onNavigate,
  onSelectAttackForVerify,
  activeAttack,
  onUpdateAttack
}) => {
  const [selectedAttack, setSelectedAttack] = useState<string>(
    activeAttack?.attack_type || 'No Attack'
  );
  const [intensity, setIntensity] = useState<number>(activeAttack?.attack_intensity ?? 0.0);
  const [modType, setModType] = useState<string>(activeAttack?.modification_type || 'None (Clean Channel)');
  const [target, setTarget] = useState<string>('Signature');
  const [noiseLevel, setNoiseLevel] = useState<number>(0.0);
  const [bitFlipProb, setBitFlipProb] = useState<number>(0.0);
  const [depolNoise, setDepolNoise] = useState<number>(0.0);
  const [shots, setShots] = useState<number>(1024);
  const [phaseError, setPhaseError] = useState<boolean>(false);
  const [randomState, setRandomState] = useState<boolean>(false);
  const [interceptResend, setInterceptResend] = useState<boolean>(false);
  const [activeBlochTab, setActiveBlochTab] = useState<'before' | 'after'>('after');

  // Live signatures state
  const [savedSignatures, setSavedSignatures] = useState<SignatureListItem[]>([]);
  const [selectedSigId, setSelectedSigId] = useState<string>(activeAttack?.signature_id || '');
  const [loadingSigs, setLoadingSigs] = useState<boolean>(false);

  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AttackSimulateResponse | null>(activeAttack || null);

  const attackCards = [
    {
      name: 'No Attack',
      desc: 'Clean channel (Attacker inactive)',
      icon: ShieldCheck,
      presetMod: 'None (Clean Channel)',
      presetIntensity: 0.0,
      presetNoise: 0.0,
      presetDepol: 0.0,
      presetBitFlip: 0.0,
      isPassive: true
    },
    {
      name: 'Forgery Attack',
      desc: 'Modify signature or message',
      icon: ShieldAlert,
      presetMod: 'Alter Quantum State (Bit Flip)',
      presetIntensity: 0.5,
      presetNoise: 0.0,
      presetDepol: 0.0,
      presetBitFlip: 0.3,
      isPassive: false
    },
    {
      name: 'Impersonation Attack',
      desc: 'Unauthorized user attempts',
      icon: UserX,
      presetMod: 'Alter Quantum State (Bit Flip)',
      presetIntensity: 0.7,
      presetNoise: 0.1,
      presetDepol: 0.0,
      presetBitFlip: 0.4,
      isPassive: false
    },
    {
      name: 'Replay Attack',
      desc: 'Resend previously captured signature',
      icon: RotateCcw,
      presetMod: 'Tamper Signature Hash',
      presetIntensity: 0.8,
      presetNoise: 0.0,
      presetDepol: 0.0,
      presetBitFlip: 0.0,
      isPassive: false
    },
    {
      name: 'Channel Manipulation',
      desc: 'Introduce noise or tampering',
      icon: Radio,
      presetMod: 'Alter Quantum State (Bit Flip)',
      presetIntensity: 0.6,
      presetNoise: 0.4,
      presetDepol: 0.35,
      presetBitFlip: 0.25,
      isPassive: false
    },
    {
      name: 'Unauthorized Verification',
      desc: 'Multiple false verification attempts',
      icon: Lock,
      presetMod: 'Tamper Signature Hash',
      presetIntensity: 0.5,
      presetNoise: 0.0,
      presetDepol: 0.0,
      presetBitFlip: 0.0,
      isPassive: false
    }
  ];

  const loadSavedSignatures = async () => {
    try {
      setLoadingSigs(true);
      const sigs = await api.listSignatures(25);
      setSavedSignatures(sigs);
      if (sigs.length > 0 && !selectedSigId) {
        setSelectedSigId(sigs[0].signature_id);
      }
    } catch (err) {
      console.error('Failed to load saved signatures for attack sim:', err);
    } finally {
      setLoadingSigs(false);
    }
  };

  const handleSelectAttackType = (card: typeof attackCards[0]) => {
    setSelectedAttack(card.name);
    setModType(card.presetMod);
    setIntensity(card.presetIntensity);
    setNoiseLevel(card.presetNoise);
    setDepolNoise(card.presetDepol);
    setBitFlipProb(card.presetBitFlip);
    executeSimulation(
      card.name,
      card.presetMod,
      card.presetIntensity,
      card.presetNoise,
      card.presetDepol,
      card.presetBitFlip
    );
  };

  const executeSimulation = async (
    atkName?: string,
    mod?: string,
    intens?: number,
    noise?: number,
    depol?: number,
    bitFlip?: number,
    sigId?: string
  ) => {
    try {
      setLoading(true);
      setError(null);
      const activeSigId = sigId !== undefined ? sigId : (selectedSigId || undefined);
      const res = await api.simulateAttack({
        attack_type: atkName || selectedAttack,
        signature_id: activeSigId,
        target: target,
        modification_type: mod || modType,
        attack_intensity: intens !== undefined ? intens : intensity,
        noise_level: noise !== undefined ? noise : noiseLevel,
        bit_flip_prob: bitFlip !== undefined ? bitFlip : bitFlipProb,
        depolarizing_noise: depol !== undefined ? depol : depolNoise,
        shots: shots,
        introduce_phase_error: phaseError,
        random_state_replacement: randomState,
        interception_resend: interceptResend,
        attacker_name: 'Eve (Unauthorized Actor)'
      });
      setResult(res);
      if (onUpdateAttack) {
        onUpdateAttack(res);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to simulate attack scenario.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // oxlint-disable-next-line react/set-state-in-effect, react-hooks/exhaustive-deps
    loadSavedSignatures();
    if (!activeAttack && !result) {
      executeSimulation();
    }
    // oxlint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const isNoAttack =
    selectedAttack === 'No Attack' ||
    (result?.threat_score !== undefined && result.threat_score < 0.30 && result.decision === 'LEGITIMATE');

  // Defaults for initial load
  const defaultOriginalState: StateVectorInfo = {
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

  const defaultTamperedState: StateVectorInfo = {
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

  const currentOriginalState = result ? result.original_state : defaultOriginalState;
  const currentTamperedState = result ? result.tampered_state : defaultTamperedState;

  const chartData = result
    ? [
        {
          state: '|0⟩',
          Expected: result.expected_distribution['0'] || 0.5,
          Observed: result.observed_distribution['0'] || 0.5
        },
        {
          state: '|1⟩',
          Expected: result.expected_distribution['1'] || 0.5,
          Observed: result.observed_distribution['1'] || 0.5
        }
      ]
    : [
        { state: '|0⟩', Expected: 0.5, Observed: 0.5 },
        { state: '|1⟩', Expected: 0.5, Observed: 0.5 }
      ];

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            Attack Simulation (Eve)
          </h1>
          <p className="text-xs text-slate-400">
            Eve (Attacker) attempts channel manipulation, eavesdropping, or state vector forgery between Alice &amp; Bob
          </p>
        </div>
        <span className="text-xs font-mono text-purple-400/80 italic hidden sm:inline">
          &ldquo;Understand the Threats to Build a Safer Tomorrow&rdquo;
        </span>
      </div>

      {/* Protocol Pipeline Banner */}
      <AliceBobPipeline
        onNavigate={onNavigate}
        activeStep="channel"
        isAttacked={selectedAttack !== 'No Attack'}
        currentAttackName={selectedAttack}
      />

      {/* Top Attack Type Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        {attackCards.map((atk) => {
          const Icon = atk.icon;
          const isSelected = selectedAttack === atk.name;
          const isPassiveCard = atk.isPassive;
          return (
            <button
              key={atk.name}
              onClick={() => handleSelectAttackType(atk)}
              className={`p-3.5 rounded-xl text-left border transition-all cursor-pointer ${
                isSelected
                  ? isPassiveCard
                    ? 'bg-[#092219]/90 border-emerald-500 shadow-lg shadow-emerald-950/50 ring-1 ring-emerald-500/40'
                    : 'bg-[#251016]/90 border-red-500 shadow-lg shadow-red-950/50 ring-1 ring-red-500/40'
                  : 'bg-[#0a1122]/80 border-blue-500/20 hover:border-blue-400/40'
              }`}
            >
              <div className="flex items-center gap-2 mb-1.5">
                <div
                  className={`p-1.5 rounded-lg ${
                    isSelected
                      ? isPassiveCard
                        ? 'bg-emerald-500/20 text-emerald-400'
                        : 'bg-red-500/20 text-red-400'
                      : isPassiveCard
                        ? 'bg-emerald-500/10 text-emerald-400/80'
                        : 'bg-blue-500/20 text-cyan-400'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                </div>
                <h3 className="text-xs font-bold text-slate-200">{atk.name}</h3>
              </div>
              <p className="text-[11px] text-slate-400 leading-tight">{atk.desc}</p>
            </button>
          );
        })}
      </div>

      {error && (
        <div className="p-3 rounded-lg bg-red-950/60 border border-red-500/40 text-red-300 text-xs">
          {error}
        </div>
      )}

      {/* Row 1: 1. Configure Attack, 2. Simulation Flow, 3. Attack Parameters */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 1. Configure Attack */}
        <div className="p-5 rounded-xl bg-[#0a1122]/90 border border-blue-500/20 shadow-lg space-y-4 flex flex-col justify-between">
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <Settings2 className="w-4 h-4 text-cyan-400" />
              <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider font-sans">
                1. Configure Scenario
              </h2>
            </div>

            <div>
              <label className="text-[11px] text-slate-400 block mb-1">Scenario / Attack Mode</label>
              <select
                value={selectedAttack}
                onChange={(e) => {
                  const card = attackCards.find((c) => c.name === e.target.value);
                  if (card) handleSelectAttackType(card);
                }}
                className="w-full p-2.5 rounded bg-[#070b16] border border-blue-900/40 text-xs text-slate-200 focus:outline-none focus:border-cyan-400 cursor-pointer"
              >
                {attackCards.map((a) => (
                  <option key={a.name} value={a.name}>
                    {a.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <div className="flex items-center justify-between mb-1">
                <label className="text-[11px] text-slate-400 flex items-center gap-1.5">
                  <Database className="w-3.5 h-3.5 text-cyan-400" />
                  Target Signature (Live DB)
                </label>
                <button
                  type="button"
                  onClick={loadSavedSignatures}
                  disabled={loadingSigs}
                  className="text-[10px] text-cyan-400 hover:text-cyan-300 flex items-center gap-1 cursor-pointer"
                  title="Refresh signatures from DB"
                >
                  <RefreshCw className={`w-3 h-3 ${loadingSigs ? 'animate-spin' : ''}`} />
                  Refresh
                </button>
              </div>
              <select
                value={selectedSigId}
                onChange={(e) => {
                  setSelectedSigId(e.target.value);
                  executeSimulation(undefined, undefined, undefined, undefined, undefined, undefined, e.target.value);
                }}
                className="w-full p-2 rounded bg-[#070b16] border border-blue-900/40 text-xs text-slate-200 font-mono focus:outline-none focus:border-cyan-400 cursor-pointer"
              >
                <option value="">-- Latest Live Signature in DB --</option>
                {savedSignatures.map((s) => (
                  <option key={s.signature_id} value={s.signature_id}>
                    {s.signature_id} • "{s.message_snippet.slice(0, 18)}..." (Fid: {(s.fidelity * 100).toFixed(1)}%)
                  </option>
                ))}
              </select>
              {selectedSigId && (
                <div className="mt-1 flex items-center gap-1.5 text-[10px] text-slate-400">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                  <span>Targeting: <span className="font-mono text-cyan-300">{selectedSigId}</span></span>
                </div>
              )}
            </div>

            <div>
              <div className="flex justify-between text-[11px] text-slate-400 mb-1">
                <span>Attack Intensity</span>
                <span className={`font-mono ${selectedAttack === 'No Attack' ? 'text-emerald-400' : 'text-cyan-300'}`}>
                  {Math.round(intensity * 100)}%
                </span>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={intensity}
                onChange={(e) => setIntensity(parseFloat(e.target.value))}
                className={`w-full cursor-pointer ${
                  selectedAttack === 'No Attack' ? 'accent-emerald-500' : 'accent-red-500'
                }`}
              />
            </div>

            <div>
              <label className="text-[11px] text-slate-400 block mb-1">Modification Type</label>
              <select
                value={modType}
                onChange={(e) => setModType(e.target.value)}
                className="w-full p-2.5 rounded bg-[#070b16] border border-blue-900/40 text-xs text-slate-200 focus:outline-none focus:border-cyan-400 cursor-pointer"
              >
                <option value="None (Clean Channel)">None (Clean Channel)</option>
                <option value="Alter Quantum State (Bit Flip)">Alter Quantum State (Bit Flip)</option>
                <option value="Phase Flip Error (Pauli-Z)">Phase Flip Error (Pauli-Z)</option>
                <option value="Random State Vector Injection">Random State Vector Injection</option>
                <option value="Tamper Signature Hash">Tamper Signature Hash</option>
              </select>
            </div>

            <div>
              <span className="text-[11px] text-slate-400 block mb-1">Target</span>
              <div className="flex items-center gap-4 text-xs">
                {['Signature', 'Message', 'Both'].map((t) => (
                  <label key={t} className="flex items-center gap-1.5 cursor-pointer text-slate-300">
                    <input
                      type="radio"
                      name="target"
                      checked={target === t}
                      onChange={() => setTarget(t)}
                      className={`${selectedAttack === 'No Attack' ? 'text-emerald-500' : 'text-red-500'} focus:ring-0 cursor-pointer`}
                    />
                    {t}
                  </label>
                ))}
              </div>
            </div>
          </div>

          <button
            onClick={() => executeSimulation()}
            disabled={loading}
            className={`w-full py-2.5 px-4 rounded-lg font-semibold text-xs transition-all shadow-lg flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50 text-white ${
              selectedAttack === 'No Attack'
                ? 'bg-gradient-to-r from-emerald-600 via-teal-600 to-cyan-600 hover:from-emerald-500 hover:to-cyan-500 shadow-emerald-950/60'
                : 'bg-gradient-to-r from-red-600 via-red-500 to-rose-600 hover:from-red-500 hover:to-rose-500 shadow-red-950/60'
            }`}
          >
            {loading ? (
              <span className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 animate-spin" />
                Simulating Quantum Scenario...
              </span>
            ) : selectedAttack === 'No Attack' ? (
              <>
                <ShieldCheck className="w-4 h-4" />
                Run Baseline (No Attack) Simulation
              </>
            ) : (
              <>
                <Play className="w-4 h-4 fill-current" />
                Run Attack Simulation
              </>
            )}
          </button>
        </div>

        {/* 2. Simulation Flow */}
        <div className="p-5 rounded-xl bg-[#0a1122]/90 border border-blue-500/20 shadow-lg space-y-4 flex flex-col justify-between">
          <div className="flex items-center gap-2">
            <Activity className="w-4 h-4 text-cyan-400" />
            <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider font-sans">
              2. Simulation Flow
            </h2>
          </div>

          {/* Flow Diagram */}
          <div className="p-4 rounded-xl bg-[#060b17] border border-blue-900/30 space-y-3">
            {/* Top Status Alert Flag */}
            {isNoAttack ? (
              <div className="p-2 rounded-md bg-emerald-950/80 border border-emerald-500/50 text-center text-xs font-bold text-emerald-300 flex items-center justify-center gap-1.5 shadow-md shadow-emerald-950/50">
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                <span>🛡️ NO ATTACK ACTIVE (CLEAN TRANSMISSION)</span>
              </div>
            ) : (
              <div className="p-2 rounded-md bg-red-950/80 border border-red-500/50 text-center text-xs font-bold text-red-300 flex items-center justify-center gap-1.5 shadow-md shadow-red-950/50">
                <AlertTriangle className="w-3.5 h-3.5 text-red-400" />
                <span>⚡ {selectedAttack.toUpperCase()} INJECTED</span>
              </div>
            )}

            <div className="grid grid-cols-4 gap-2 text-center text-[10px] font-mono">
              <div className="p-2 rounded bg-[#0d162a] border border-slate-800">
                <FileText className="w-4 h-4 text-cyan-400 mx-auto mb-1" />
                <span className="text-slate-300 block">Original Msg</span>
              </div>
              <div className="p-2 rounded bg-[#0d162a] border border-slate-800">
                <Layers className="w-4 h-4 text-purple-400 mx-auto mb-1" />
                <span className="text-slate-300 block">Signature</span>
              </div>
              <div className="p-2 rounded bg-[#0d162a] border border-slate-800">
                <Radio className="w-4 h-4 text-cyan-400 mx-auto mb-1" />
                <span className="text-slate-300 block">Transmission</span>
              </div>
              <div
                className={`p-2 rounded border ${
                  isNoAttack
                    ? 'bg-emerald-950/60 border-emerald-500/40 text-emerald-300'
                    : 'bg-red-950/60 border-red-500/40 text-red-300'
                }`}
              >
                {isNoAttack ? (
                  <ShieldCheck className="w-4 h-4 text-emerald-400 mx-auto mb-1" />
                ) : (
                  <AlertTriangle className="w-4 h-4 text-red-400 mx-auto mb-1" />
                )}
                <span className="font-bold block">{isNoAttack ? 'Legitimate' : 'Result'}</span>
              </div>
            </div>

            {/* Path Indicator */}
            <div
              className={`p-2 rounded border border-dashed text-center text-[10px] font-mono ${
                isNoAttack
                  ? 'border-emerald-500/40 bg-emerald-950/20 text-emerald-400'
                  : 'border-red-500/40 bg-red-950/20 text-red-400'
              }`}
            >
              {isNoAttack
                ? 'Pure Quantum State / Authentic Channel (No Tampering)'
                : 'Modified Signature / Tampered Quantum State Detected'}
            </div>
          </div>

          <p className="text-[11px] text-slate-400 text-center italic font-mono">
            {isNoAttack
              ? 'Passive channel monitoring: No eavesdropping or quantum state collapse detected.'
              : 'Eavesdropper injection degrades quantum fidelity & alters basis statistics.'}
          </p>
        </div>

        {/* 3. Attack Parameters */}
        <div className="p-5 rounded-xl bg-[#0a1122]/90 border border-blue-500/20 shadow-lg space-y-4">
          <div className="flex items-center gap-2">
            <Sliders className="w-4 h-4 text-cyan-400" />
            <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider font-sans">
              3. Channel & Noise Parameters
            </h2>
          </div>

          <div className="space-y-3 text-xs">
            <div>
              <div className="flex justify-between text-[11px] text-slate-400 mb-1">
                <span>Noise Level</span>
                <span className="font-mono text-cyan-300">{Math.round(noiseLevel * 100)}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={noiseLevel}
                onChange={(e) => setNoiseLevel(parseFloat(e.target.value))}
                className="w-full accent-cyan-500 cursor-pointer"
              />
            </div>

            <div>
              <div className="flex justify-between text-[11px] text-slate-400 mb-1">
                <span>Bit Flip Probability</span>
                <span className="font-mono text-cyan-300">{bitFlipProb.toFixed(2)}</span>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={bitFlipProb}
                onChange={(e) => setBitFlipProb(parseFloat(e.target.value))}
                className="w-full accent-cyan-500 cursor-pointer"
              />
            </div>

            <div>
              <div className="flex justify-between text-[11px] text-slate-400 mb-1">
                <span>Depolarizing Noise</span>
                <span className="font-mono text-cyan-300">{Math.round(depolNoise * 100)}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={depolNoise}
                onChange={(e) => setDepolNoise(parseFloat(e.target.value))}
                className="w-full accent-cyan-500 cursor-pointer"
              />
            </div>

            <div className="flex justify-between items-center pt-1 border-t border-slate-800">
              <span className="text-[11px] text-slate-400">Number of Shots</span>
              <select
                value={shots}
                onChange={(e) => setShots(parseInt(e.target.value))}
                className="p-1 rounded bg-[#070b16] border border-slate-800 text-xs text-slate-300"
              >
                <option value={512}>512</option>
                <option value={1024}>1024</option>
                <option value={2048}>2048</option>
              </select>
            </div>

            <div className="pt-2 border-t border-slate-800 space-y-1.5">
              <span className="text-[10px] text-slate-500 uppercase tracking-wider font-semibold block">
                Advanced Options
              </span>
              <label className="flex items-center gap-2 text-[11px] text-slate-300 cursor-pointer">
                <input
                  type="checkbox"
                  checked={phaseError}
                  onChange={(e) => setPhaseError(e.target.checked)}
                  className="rounded text-cyan-500 focus:ring-0 cursor-pointer"
                />
                Introduce phase error (Pauli-Z)
              </label>
              <label className="flex items-center gap-2 text-[11px] text-slate-300 cursor-pointer">
                <input
                  type="checkbox"
                  checked={randomState}
                  onChange={(e) => setRandomState(e.target.checked)}
                  className="rounded text-cyan-500 focus:ring-0 cursor-pointer"
                />
                Use random state replacement
              </label>
              <label className="flex items-center gap-2 text-[11px] text-slate-300 cursor-pointer">
                <input
                  type="checkbox"
                  checked={interceptResend}
                  onChange={(e) => setInterceptResend(e.target.checked)}
                  className="rounded text-cyan-500 focus:ring-0 cursor-pointer"
                />
                Apply interception-resend strategy
              </label>
            </div>
          </div>
        </div>
      </div>

      {/* Row 2: 4. Results Comparison, 5. Quantum State Viz, 6. Detection Analysis, 7. Simulation Logs */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 4. Results Comparison Chart */}
        <div className="p-5 rounded-xl bg-[#0a1122]/90 border border-blue-500/20 shadow-lg space-y-3 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-2">
              <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider font-sans flex items-center gap-2">
                <Activity className="w-4 h-4 text-cyan-400" />
                4. Results Comparison
              </h2>
              <div className="flex items-center gap-3 text-[11px]">
                <span className="flex items-center gap-1 text-cyan-400">
                  <span className="w-2.5 h-2.5 rounded-sm bg-cyan-500"></span> Expected
                </span>
                <span className={`flex items-center gap-1 ${isNoAttack ? 'text-emerald-400' : 'text-red-400'}`}>
                  <span className={`w-2.5 h-2.5 rounded-sm ${isNoAttack ? 'bg-emerald-500' : 'bg-red-500'}`}></span> Observed
                </span>
              </div>
            </div>

            <div className="h-44 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="state" stroke="#64748b" fontSize={11} fontFamily="monospace" />
                  <YAxis stroke="#64748b" fontSize={11} domain={[0, 1]} />
                  <RechartsTooltip
                    contentStyle={{
                      backgroundColor: '#0c1427',
                      borderColor: isNoAttack ? '#10b981' : '#ef4444',
                      fontSize: 12
                    }}
                  />
                  <Bar dataKey="Expected" fill="#06b6d4" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="Observed" fill={isNoAttack ? '#10b981' : '#ef4444'} radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <p className="text-[11px] text-center text-slate-400 font-mono mt-1">Measurement Outcome Distribution</p>
          </div>

          <div
            className={`p-2.5 rounded-lg border text-xs flex items-center gap-2 ${
              isNoAttack
                ? 'bg-emerald-950/40 border-emerald-500/30 text-emerald-300'
                : 'bg-red-950/40 border-red-500/30 text-red-300'
            }`}
          >
            {isNoAttack ? (
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
            ) : (
              <AlertTriangle className="w-4 h-4 text-red-400 shrink-0" />
            )}
            <span className="text-[11px]">
              {isNoAttack
                ? 'Expected and observed measurement distributions align with high quantum fidelity (>99%). Zero channel tampering detected.'
                : 'Significant deviation from expected distribution detected. The observed measurement results indicate an active security threat.'}
            </span>
          </div>
        </div>

        {/* 5. Quantum State Visualization (Bloch Sphere) */}
        <div className="p-5 rounded-xl bg-[#0a1122]/90 border border-blue-500/20 shadow-lg space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Layers className="w-4 h-4 text-purple-400" />
              <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider font-sans">
                5. Quantum State Visualization
              </h2>
            </div>
            <div className="flex rounded-lg bg-[#070b16] p-0.5 border border-slate-800">
              <button
                onClick={() => setActiveBlochTab('before')}
                className={`px-2 py-0.5 text-[11px] rounded font-medium transition-colors cursor-pointer ${
                  activeBlochTab === 'before' ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                Original State
              </button>
              <button
                onClick={() => setActiveBlochTab('after')}
                className={`px-2 py-0.5 text-[11px] rounded font-medium transition-colors cursor-pointer ${
                  activeBlochTab === 'after'
                    ? isNoAttack
                      ? 'bg-emerald-600 text-white'
                      : 'bg-red-600 text-white'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {isNoAttack ? 'Observed State' : 'After Attack'}
              </button>
            </div>
          </div>

          <BlochSphere
            stateInfo={currentOriginalState}
            tamperedState={activeBlochTab === 'after' ? currentTamperedState : null}
            size={160}
            showDetails={true}
          />
        </div>

        {/* 6. Detection Analysis & 7. Simulation Logs */}
        <div className="space-y-6">
          {/* 6. Detection Analysis */}
          <div className="p-5 rounded-xl bg-[#0a1122]/90 border border-blue-500/20 shadow-lg space-y-3">
            <div className="flex items-center gap-2">
              {isNoAttack ? (
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
              ) : (
                <ShieldAlert className="w-4 h-4 text-red-400" />
              )}
              <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider font-sans">
                6. Detection Analysis
              </h2>
            </div>

            <div className="space-y-1.5 text-xs font-mono">
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400 font-sans">Verification Fidelity</span>
                <span className={`font-bold flex items-center gap-1 ${isNoAttack ? 'text-emerald-400' : 'text-red-400'}`}>
                  {result?.fidelity ?? (isNoAttack ? 1.0 : 0.612)}
                  <span className={`text-[10px] ${isNoAttack ? 'text-emerald-400' : 'text-red-500'}`}>
                    {isNoAttack ? '✓ Intact' : `↓ ${result?.fidelity_change_percent || 38.8}%`}
                  </span>
                </span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400 font-sans">Measurement Deviation</span>
                <span className={`font-bold flex items-center gap-1 ${isNoAttack ? 'text-emerald-400' : 'text-red-400'}`}>
                  {result?.deviation ?? (isNoAttack ? 0.0 : 0.22)}
                  <span className={`text-[10px] ${isNoAttack ? 'text-emerald-400' : 'text-red-500'}`}>
                    {isNoAttack ? '0.0% error' : `↑ ${result?.deviation_change_percent || 220}%`}
                  </span>
                </span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400 font-sans">Threat Score</span>
                <span className={`font-bold ${isNoAttack ? 'text-emerald-400' : 'text-red-400'}`}>
                  {result?.threat_score ?? (isNoAttack ? '0.00 (LOW)' : 0.78)}
                </span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400 font-sans">Signature Copies (L)</span>
                <span className="text-cyan-300 font-bold">64 Pauli Eigenstates</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400 font-sans">Measured Mismatch Rate (m)</span>
                <span className={`font-bold ${isNoAttack ? 'text-emerald-400' : 'text-red-400'}`}>
                  {result?.measured_mismatch_rate !== undefined
                    ? `${(result.measured_mismatch_rate * 100).toFixed(1)}%`
                    : (isNoAttack ? '0.0%' : '38.8%')}
                </span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400 font-sans">Acceptance Threshold (s_a)</span>
                <span className="text-emerald-400 font-bold">0.100 (10.0%)</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400 font-sans">Detector Fired</span>
                <span className={`font-bold uppercase px-1.5 py-0.2 rounded text-[10px] ${
                  isNoAttack ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' :
                  result?.detector_fired === 'nonce' ? 'bg-purple-950 text-purple-300 border border-purple-800' :
                  result?.detector_fired === 'rate-limit' ? 'bg-amber-950 text-amber-300 border border-amber-800' :
                  result?.detector_fired === 'authorization' ? 'bg-red-950 text-red-300 border border-red-800' :
                  'bg-red-950 text-red-400 border border-red-800'
                }`}>
                  {result?.detector_fired || (isNoAttack ? 'None (Clean)' : 'Threshold')}
                </span>
              </div>
              <div className="flex justify-between py-1">
                <span className="text-slate-400 font-sans">Final Decision</span>
                <span className={`font-bold ${isNoAttack ? 'text-emerald-400' : 'text-red-400'}`}>
                  {result?.decision || (isNoAttack ? 'LEGITIMATE (PASSED)' : 'ATTACK DETECTED')}
                </span>
              </div>
            </div>

            {result?.forgery_summary && (
              <div className="p-2.5 rounded-lg bg-blue-950/40 border border-cyan-500/30 text-[11px] text-slate-300">
                <span className="font-semibold text-cyan-300 block mb-0.5">Statistical Analysis (Hoeffding Bound):</span>
                <p className="text-slate-300">{result.forgery_summary.summary}</p>
                {result.forgery_summary.confidence_score !== undefined && (
                  <span className="text-[10px] text-cyan-400 mt-1 block">
                    Statistical Confidence: {result.forgery_summary.confidence_score}%
                  </span>
                )}
              </div>
            )}

            <div
              className={`p-3 rounded-lg border text-xs flex items-start gap-2 ${
                isNoAttack
                  ? 'bg-emerald-950/60 border-emerald-500/40 text-emerald-300'
                  : 'bg-red-950/60 border-red-500/40 text-red-300'
              }`}
            >
              {isNoAttack ? (
                <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
              ) : (
                <AlertTriangle className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
              )}
              <p className="text-[11px] leading-tight">
                {result?.alert_message ||
                  (isNoAttack
                    ? 'No attack detected. The quantum digital signature passed all statistical verification checks.'
                    : 'Attack detected with high confidence. The signature fails verification under statistical analysis.')}
              </p>
            </div>

            {(onNavigate || onSelectAttackForVerify) && (
              <button
                onClick={() => {
                  if (result && onSelectAttackForVerify) {
                    onSelectAttackForVerify(result);
                  } else if (onNavigate) {
                    onNavigate('verification');
                  }
                }}
                className="w-full py-2.5 px-3 rounded-lg bg-gradient-to-r from-blue-600/40 via-cyan-600/40 to-blue-600/40 hover:from-blue-600/60 hover:to-cyan-600/60 border border-cyan-500/40 text-cyan-200 text-xs font-semibold flex items-center justify-center gap-2 cursor-pointer transition-all shadow-md"
              >
                <ShieldCheck className="w-4 h-4 text-cyan-400" />
                <span>⚡ Send &amp; Verify This {isNoAttack ? 'Clean Channel' : 'Attacked State'} in Verification Console &rarr;</span>
              </button>
            )}
          </div>

          {/* 7. Simulation Logs */}
          <div className="p-5 rounded-xl bg-[#0a1122]/90 border border-blue-500/20 shadow-lg space-y-3">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider font-sans flex items-center gap-2">
                <FileText className="w-4 h-4 text-cyan-400" />
                7. Simulation Logs
              </h2>
              <span className="text-[10px] font-mono text-slate-400">Live Trace</span>
            </div>

            <div className="space-y-1.5 text-xs font-mono max-h-36 overflow-y-auto">
              {(result?.simulation_logs || [
                { time: '14:31:02', event: 'Simulation Started', details: 'No Attack baseline (0%)', status: 'Success' },
                { time: '14:31:03', event: 'Channel Monitoring', details: 'Quantum state unperturbed', status: 'Success' },
                { time: '14:31:04', event: 'Measurement', details: '1024 shots completed', status: 'Success' },
                { time: '14:31:05', event: 'Verification', details: 'Fidelity = 1.000', status: 'Success' },
                { time: '14:31:05', event: 'Threat Detection', details: 'Score = 0.00 -> Legitimate', status: 'Legitimate' }
              ]).map((log, idx) => (
                <div key={idx} className="flex justify-between items-center py-1 border-b border-slate-800/40 text-[11px]">
                  <span className="text-slate-500">{log.time}</span>
                  <span className="text-slate-300 font-semibold">{log.event}</span>
                  <span className="text-cyan-300 font-sans text-[10px] truncate max-w-[110px]">{log.details}</span>
                  <span
                    className={`text-[10px] font-bold ${
                      log.status.includes('Attack') || log.status === 'Detected'
                        ? 'text-red-400'
                        : log.status === 'Warning'
                        ? 'text-amber-400'
                        : 'text-emerald-400'
                    }`}
                  >
                    {log.status}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

