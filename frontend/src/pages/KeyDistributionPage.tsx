import React, { useState, useEffect, useCallback } from 'react';
import {
  Share2,
  Atom,
  RefreshCw,
  Cpu,
  Layers,
  Database,
  Radio,
  Sliders,
  AlertCircle
} from 'lucide-react';
import { api } from '../services/api';
import type { QDSDistributeResponse, QDSKeygenResponse } from '../types';

export const KeyDistributionPage: React.FC = () => {
  // State configuration
  const [length, setLength] = useState<number>(32);
  const [depolarizingNoise, setDepolarizingNoise] = useState<number>(0.0);
  const [bitFlipNoise, setBitFlipNoise] = useState<number>(0.0);
  const [phaseFlipNoise, setPhaseFlipNoise] = useState<number>(0.0);
  const [verifiers] = useState<string[]>(['Bob', 'Charlie']);
  const [selectedVerifier, setSelectedVerifier] = useState<string>('Bob');
  const [selectedBit, setSelectedBit] = useState<number>(0);

  // Async states
  const [keypair, setKeypair] = useState<QDSKeygenResponse | null>(null);
  const [distResult, setDistResult] = useState<QDSDistributeResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleGenerateAndDistribute = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      // 1. Generate QDS keypair
      const keyData = await api.qdsKeygen({ length, seed: 42 });
      setKeypair(keyData);

      // 2. Distribute via teleportation
      const distData = await api.qdsDistribute({
        key_id: keyData.key_id,
        verifiers,
        depolarizing_prob: depolarizingNoise,
        bit_flip_prob: bitFlipNoise,
        phase_flip_prob: phaseFlipNoise,
        seed: 42
      });
      setDistResult(distData);
    } catch (err: any) {
      setError(err.message || 'Failed to execute quantum key distribution');
    } finally {
      setIsLoading(false);
    }
  }, [length, verifiers, depolarizingNoise, bitFlipNoise, phaseFlipNoise]);

  // Initialize keypair on mount
  useEffect(() => {
    // oxlint-disable-next-line react/set-state-in-effect
    handleGenerateAndDistribute();
  }, [handleGenerateAndDistribute]);

  const currentVerifierMemory = distResult?.verifiers_status[selectedVerifier];
  const displayedStates = selectedBit === 0
    ? currentVerifierMemory?.states_0
    : currentVerifierMemory?.states_1;

  return (
    <div className="space-y-6 pb-16">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <Share2 className="w-6 h-6 text-cyan-400" />
            Quantum Public Key Distribution (QPKD)
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Simulated Bell pair entanglement, quantum teleportation, and feed-forward Pauli corrections for verifier memory storage.
          </p>
        </div>

        <button
          onClick={handleGenerateAndDistribute}
          disabled={isLoading}
          className="flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white text-xs font-semibold shadow-md shadow-cyan-500/20 disabled:opacity-50 transition-all cursor-pointer"
        >
          <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          <span>{isLoading ? 'Teleporting States...' : 'Run Distribution'}</span>
        </button>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="p-4 rounded-xl bg-red-950/40 border border-red-500/40 text-red-300 text-xs flex items-center gap-3">
          <AlertCircle className="w-5 h-5 text-red-400 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Step-by-Step Protocol Pipeline Visual */}
      <div className="p-5 rounded-xl bg-[#090e1a]/90 border border-blue-900/30 space-y-4">
        <h2 className="text-xs font-bold uppercase tracking-wider text-cyan-400 font-mono flex items-center gap-2">
          <Radio className="w-4 h-4 text-cyan-400" />
          Teleportation Protocol Pipeline (Alice &rarr; Verifiers)
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-3 relative">
          {/* Step 1 */}
          <div className="p-4 rounded-lg bg-[#0d1628]/80 border border-blue-500/20 space-y-2 relative">
            <div className="flex items-center justify-between">
              <span className="w-6 h-6 rounded-full bg-blue-600/30 text-cyan-300 font-mono text-xs flex items-center justify-center font-bold">1</span>
              <Atom className="w-4 h-4 text-blue-400" />
            </div>
            <h3 className="text-xs font-bold text-slate-200">EPR Bell Pair Generation</h3>
            <p className="text-[11px] text-slate-400 leading-relaxed font-mono">
              |&Phi;+&rang; = 1/&radic;2 (|00&rang; + |11&rang;) shared between Alice and each Verifier.
            </p>
          </div>

          {/* Step 2 */}
          <div className="p-4 rounded-lg bg-[#0d1628]/80 border border-cyan-500/20 space-y-2 relative">
            <div className="flex items-center justify-between">
              <span className="w-6 h-6 rounded-full bg-cyan-600/30 text-cyan-300 font-mono text-xs flex items-center justify-center font-bold">2</span>
              <Layers className="w-4 h-4 text-cyan-400" />
            </div>
            <h3 className="text-xs font-bold text-slate-200">Bell State Measurement (BSM)</h3>
            <p className="text-[11px] text-slate-400 leading-relaxed font-mono">
              Alice projects (|&psi;&rang;, Bell_Alice), producing 2 classical bits (c1, c0).
            </p>
          </div>

          {/* Step 3 */}
          <div className="p-4 rounded-lg bg-[#0d1628]/80 border border-purple-500/20 space-y-2 relative">
            <div className="flex items-center justify-between">
              <span className="w-6 h-6 rounded-full bg-purple-600/30 text-purple-300 font-mono text-xs flex items-center justify-center font-bold">3</span>
              <Cpu className="w-4 h-4 text-purple-400" />
            </div>
            <h3 className="text-xs font-bold text-slate-200">Pauli Feed-Forward Correction</h3>
            <p className="text-[11px] text-slate-400 leading-relaxed font-mono">
              Verifier applies X^c1 &middot; Z^c0 to reconstruct authentic eigenstate |&psi;&rang;.
            </p>
          </div>

          {/* Step 4 */}
          <div className="p-4 rounded-lg bg-[#0d1628]/80 border border-emerald-500/20 space-y-2 relative">
            <div className="flex items-center justify-between">
              <span className="w-6 h-6 rounded-full bg-emerald-600/30 text-emerald-300 font-mono text-xs flex items-center justify-center font-bold">4</span>
              <Database className="w-4 h-4 text-emerald-400" />
            </div>
            <h3 className="text-xs font-bold text-slate-200">Quantum Memory Storage</h3>
            <p className="text-[11px] text-slate-400 leading-relaxed font-mono">
              Reconstructed state placed in Verifier Memory ready for projective test.
            </p>
          </div>
        </div>
      </div>

      {/* Control Panel & Parameters */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Configuration Controls */}
        <div className="p-5 rounded-xl bg-[#090e1a]/90 border border-blue-900/30 space-y-4">
          <h2 className="text-xs font-bold uppercase tracking-wider text-slate-300 font-mono flex items-center gap-2">
            <Sliders className="w-4 h-4 text-cyan-400" />
            Distribution Parameters
          </h2>

          {/* Key Length Slider */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs font-mono">
              <span className="text-slate-400">Signature Length (L):</span>
              <span className="text-cyan-300 font-bold">{length} qubits / bit</span>
            </div>
            <input
              type="range"
              min="8"
              max="128"
              step="8"
              value={length}
              onChange={(e) => setLength(parseInt(e.target.value))}
              className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-500"
            />
            <div className="flex justify-between text-[10px] text-slate-600 font-mono">
              <span>8</span>
              <span>32</span>
              <span>64</span>
              <span>128</span>
            </div>
          </div>

          {/* Depolarizing Noise Slider */}
          <div className="space-y-1.5 pt-2 border-t border-slate-800/80">
            <div className="flex justify-between text-xs font-mono">
              <span className="text-slate-400">Depolarizing Channel Noise:</span>
              <span className="text-amber-400 font-bold">{(depolarizingNoise * 100).toFixed(1)}%</span>
            </div>
            <input
              type="range"
              min="0.0"
              max="0.25"
              step="0.01"
              value={depolarizingNoise}
              onChange={(e) => setDepolarizingNoise(parseFloat(e.target.value))}
              className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-amber-500"
            />
          </div>

          {/* Bit-Flip Noise Slider */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs font-mono">
              <span className="text-slate-400">Pauli Bit-Flip Noise (X):</span>
              <span className="text-amber-400 font-bold">{(bitFlipNoise * 100).toFixed(1)}%</span>
            </div>
            <input
              type="range"
              min="0.0"
              max="0.20"
              step="0.01"
              value={bitFlipNoise}
              onChange={(e) => setBitFlipNoise(parseFloat(e.target.value))}
              className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-amber-500"
            />
          </div>

          {/* Phase-Flip Noise Slider */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs font-mono">
              <span className="text-slate-400">Pauli Phase-Flip Noise (Z):</span>
              <span className="text-amber-400 font-bold">{(phaseFlipNoise * 100).toFixed(1)}%</span>
            </div>
            <input
              type="range"
              min="0.0"
              max="0.20"
              step="0.01"
              value={phaseFlipNoise}
              onChange={(e) => setPhaseFlipNoise(parseFloat(e.target.value))}
              className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-amber-500"
            />
          </div>
        </div>

        {/* Right: Live Telemetry Cards */}
        <div className="lg:col-span-2 grid grid-cols-1 sm:grid-cols-2 gap-4">
          {/* Teleportation Status Card */}
          <div className="p-5 rounded-xl bg-[#090e1a]/90 border border-blue-900/30 flex flex-col justify-between">
            <div>
              <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-cyan-950 border border-cyan-500/30 text-cyan-300">
                Live Distribution
              </span>
              <h3 className="text-sm font-bold text-slate-200 mt-2">Teleportation Method</h3>
              <p className="text-xs text-slate-400 font-mono mt-1">
                {distResult?.teleportation_method || 'EPR Bell Pairs + Feed-Forward Pauli Correction'}
              </p>
            </div>
            <div className="pt-4 border-t border-slate-800/80 space-y-1 text-xs font-mono">
              <div className="flex justify-between text-slate-400">
                <span>Active Key ID:</span>
                <span className="text-slate-200 font-semibold">{keypair?.key_id || 'Generating...'}</span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>Total Teleported:</span>
                <span className="text-cyan-300 font-bold">{distResult?.total_states_teleported ?? 0} states</span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>Channel Noise:</span>
                <span className={distResult?.noise_applied ? 'text-amber-400' : 'text-emerald-400'}>
                  {distResult?.noise_applied ? 'Noise Injected' : 'Noiseless (Ideal)'}
                </span>
              </div>
            </div>
          </div>

          {/* Verifier Memory Fidelity Card */}
          <div className="p-5 rounded-xl bg-[#090e1a]/90 border border-blue-900/30 flex flex-col justify-between">
            <div>
              <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-emerald-950 border border-emerald-500/30 text-emerald-300">
                Quantum Memory Fidelity
              </span>
              <h3 className="text-sm font-bold text-slate-200 mt-2">Verifier Channel Health</h3>
              <p className="text-xs text-slate-400 font-mono mt-1">
                Computed live across stored qubit positions:
              </p>
            </div>
            <div className="pt-4 border-t border-slate-800/80 space-y-2 text-xs font-mono">
              {verifiers.map((v) => {
                const mem = distResult?.verifiers_status[v];
                const fid = mem?.avg_fidelity ?? 1.0;
                return (
                  <div key={v} className="flex items-center justify-between">
                    <span className="text-slate-300 font-semibold">{v}:</span>
                    <div className="flex items-center gap-2">
                      <div className="w-24 bg-slate-800 h-2 rounded-full overflow-hidden">
                        <div
                          className={`h-full ${fid >= 0.95 ? 'bg-emerald-400' : fid >= 0.85 ? 'bg-amber-400' : 'bg-red-400'}`}
                          style={{ width: `${Math.min(100, Math.max(0, fid * 100))}%` }}
                        />
                      </div>
                      <span className="text-cyan-300 font-bold">{(fid * 100).toFixed(1)}%</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>

      {/* Quantum Memory State Inspector */}
      <div className="p-5 rounded-xl bg-[#090e1a]/90 border border-blue-900/30 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h2 className="text-sm font-bold text-slate-100 flex items-center gap-2">
              <Database className="w-4 h-4 text-cyan-400" />
              Verifier Quantum Memory State Inspector
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Inspecting stored quantum eigenstates, BSM teleportation outcomes, and Pauli corrections.
            </p>
          </div>

          {/* Verifier Selector & Bit Selector */}
          <div className="flex items-center gap-2">
            <div className="flex bg-slate-800/80 p-0.5 rounded-lg border border-slate-700/60 text-xs font-mono">
              {verifiers.map((v) => (
                <button
                  key={v}
                  onClick={() => setSelectedVerifier(v)}
                  className={`px-3 py-1 rounded-md transition-all cursor-pointer ${
                    selectedVerifier === v
                      ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 font-bold'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  {v}
                </button>
              ))}
            </div>

            <div className="flex bg-slate-800/80 p-0.5 rounded-lg border border-slate-700/60 text-xs font-mono">
              <button
                onClick={() => setSelectedBit(0)}
                className={`px-3 py-1 rounded-md transition-all cursor-pointer ${
                  selectedBit === 0
                    ? 'bg-purple-500/20 text-purple-300 border border-purple-500/40 font-bold'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                Bit b = 0
              </button>
              <button
                onClick={() => setSelectedBit(1)}
                className={`px-3 py-1 rounded-md transition-all cursor-pointer ${
                  selectedBit === 1
                    ? 'bg-purple-500/20 text-purple-300 border border-purple-500/40 font-bold'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                Bit b = 1
              </button>
            </div>
          </div>
        </div>

        {/* States Table */}
        <div className="overflow-x-auto border border-slate-800/80 rounded-lg">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-[#0c1424] text-slate-400 border-b border-slate-800/80">
              <tr>
                <th className="p-3">Pos</th>
                <th className="p-3">True State</th>
                <th className="p-3">Basis</th>
                <th className="p-3">Teleport Outcome</th>
                <th className="p-3">Pauli Correction</th>
                <th className="p-3">Fidelity</th>
                <th className="p-3">Noise Detail</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50">
              {displayedStates && displayedStates.length > 0 ? (
                displayedStates.slice(0, 16).map((st) => (
                  <tr key={st.position} className="hover:bg-slate-800/30 transition-colors">
                    <td className="p-3 text-slate-500">#{st.position}</td>
                    <td className="p-3 font-bold text-cyan-300">{st.original_state_label}</td>
                    <td className="p-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        st.original_basis === 'Z' ? 'bg-blue-950 text-blue-300 border border-blue-800/40' :
                        st.original_basis === 'X' ? 'bg-purple-950 text-purple-300 border border-purple-800/40' :
                        'bg-amber-950 text-amber-300 border border-amber-800/40'
                      }`}>
                        {st.original_basis}-Basis
                      </span>
                    </td>
                    <td className="p-3 text-slate-300">
                      <span className="font-bold text-purple-400">{st.teleportation_outcome}</span>
                    </td>
                    <td className="p-3 text-slate-300">{st.pauli_correction}</td>
                    <td className="p-3 font-bold text-emerald-400">
                      {(st.fidelity_with_original * 100).toFixed(1)}%
                    </td>
                    <td className="p-3 text-slate-400 text-[11px]">{st.noise_details}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={7} className="p-6 text-center text-slate-500">
                    No states stored. Click &quot;Run Distribution&quot; above to teleport public key copies.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
