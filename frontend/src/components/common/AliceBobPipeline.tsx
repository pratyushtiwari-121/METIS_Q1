import React from 'react';
import {
  User,
  ShieldCheck,
  ShieldAlert,
  Radio,
  ArrowRight,
  KeyRound,
  FileText,
  Activity,
  CheckCircle2,
  Lock,
  Zap,
  Cpu
} from 'lucide-react';

interface AliceBobPipelineProps {
  onNavigate?: (route: string) => void;
  activeStep?: 'alice' | 'channel' | 'bob';
  currentAttackName?: string;
  isAttacked?: boolean;
}

export const AliceBobPipeline: React.FC<AliceBobPipelineProps> = ({
  onNavigate,
  activeStep,
  currentAttackName = 'None (Clean Channel)',
  isAttacked = false
}) => {
  return (
    <div className="p-5 rounded-2xl bg-gradient-to-b from-[#0a1122]/95 via-[#080d1a]/95 to-[#050811]/95 border border-cyan-500/30 shadow-2xl space-y-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 border-b border-blue-900/40 pb-3">
        <div>
          <h2 className="text-base font-bold text-slate-100 flex items-center gap-2 font-sans tracking-wide">
            <Zap className="w-4 h-4 text-cyan-400 fill-cyan-400/20" />
            Alice &amp; Bob Quantum Digital Signature Protocol Pipeline
          </h2>
          <p className="text-xs text-slate-400">
            End-to-End Quantum Cryptographic Transmission &amp; Verification Flow
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span
            className={`text-[10px] font-mono font-bold px-2.5 py-1 rounded-full flex items-center gap-1.5 border ${
              isAttacked
                ? 'bg-red-950/80 text-red-300 border-red-500/50 animate-pulse'
                : 'bg-emerald-950/80 text-emerald-300 border-emerald-500/50'
            }`}
          >
            <span
              className={`w-2 h-2 rounded-full ${
                isAttacked ? 'bg-red-400 animate-ping' : 'bg-emerald-400 animate-pulse'
              }`}
            ></span>
            {isAttacked ? `⚡ ATTACK ACTIVE: ${currentAttackName}` : '🛡️ CLEAN QUANTUM CHANNEL'}
          </span>
        </div>
      </div>

      {/* Main 3-Stage Pipeline */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 relative">
        {/* STAGE 1: ALICE (SENDER / SIGNER) */}
        <div
          onClick={() => onNavigate && onNavigate('signature-generation')}
          className={`p-4 rounded-xl border transition-all cursor-pointer relative overflow-hidden group ${
            activeStep === 'alice'
              ? 'bg-[#091a33]/90 border-cyan-400 ring-1 ring-cyan-400/50 shadow-lg shadow-cyan-950/50'
              : 'bg-[#070e1c]/80 border-blue-900/40 hover:border-cyan-500/50 hover:bg-[#091428]'
          }`}
        >
          {/* Top Label */}
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <div className="p-2 rounded-lg bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
                <User className="w-5 h-5 text-cyan-400" />
              </div>
              <div>
                <h3 className="text-xs font-extrabold text-cyan-300 uppercase tracking-wider font-sans">
                  ALICE (SENDER)
                </h3>
                <span className="text-[10px] text-slate-400 font-mono">Quantum Signer</span>
              </div>
            </div>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800">
              Stage 1
            </span>
          </div>

          <p className="text-[11px] text-slate-300 mb-3 leading-relaxed">
            Alice hashes plaintext message <span className="font-mono text-cyan-300">M</span> via <span className="text-cyan-400 font-mono">SHA-256</span> and encodes angles (&theta;, &phi;) into quantum state vector <span className="font-mono text-purple-300">|&psi;_A&rang;</span>.
          </p>

          <div className="space-y-1.5 text-[10px] font-mono bg-[#040812] p-2.5 rounded-lg border border-blue-950 text-slate-300">
            <div className="flex justify-between items-center">
              <span className="text-slate-400 flex items-center gap-1">
                <FileText className="w-3 h-3 text-cyan-400" /> Message Hash:
              </span>
              <span className="text-cyan-300">SHA-256 Digest</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-400 flex items-center gap-1">
                <KeyRound className="w-3 h-3 text-purple-400" /> Qubit State:
              </span>
              <span className="text-purple-300">|&psi;_A&rang; = &alpha;|0&rang; + &beta;|1&rang;</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-400 flex items-center gap-1">
                <Cpu className="w-3 h-3 text-emerald-400" /> Entanglement:
              </span>
              <span className="text-emerald-300 font-bold">Bell Pair |&Phi;&plus;&rang;</span>
            </div>
          </div>

          {onNavigate && (
            <div className="mt-3 text-right">
              <span className="text-[10px] text-cyan-400 group-hover:text-cyan-200 font-semibold flex items-center justify-end gap-1">
                Generate Signature &rarr;
              </span>
            </div>
          )}
        </div>

        {/* STAGE 2: QUANTUM CHANNEL & EVE (INTERCEPTOR / NOISE) */}
        <div
          onClick={() => onNavigate && onNavigate('attack-simulation')}
          className={`p-4 rounded-xl border transition-all cursor-pointer relative overflow-hidden group ${
            activeStep === 'channel' || isAttacked
              ? 'bg-[#220d14]/90 border-red-500 ring-1 ring-red-500/50 shadow-lg shadow-red-950/50'
              : 'bg-[#070e1c]/80 border-blue-900/40 hover:border-purple-500/50 hover:bg-[#110c1f]'
          }`}
        >
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <div
                className={`p-2 rounded-lg ${
                  isAttacked
                    ? 'bg-red-500/20 text-red-300 border border-red-500/40'
                    : 'bg-purple-500/20 text-purple-300 border border-purple-500/30'
                }`}
              >
                <Radio className={`w-5 h-5 ${isAttacked ? 'text-red-400 animate-pulse' : 'text-purple-400'}`} />
              </div>
              <div>
                <h3
                  className={`text-xs font-extrabold uppercase tracking-wider font-sans ${
                    isAttacked ? 'text-red-300' : 'text-purple-300'
                  }`}
                >
                  QUANTUM CHANNEL (EVE)
                </h3>
                <span className="text-[10px] text-slate-400 font-mono">
                  {isAttacked ? 'Active Interception' : 'Transmission Link'}
                </span>
              </div>
            </div>
            <span
              className={`text-[10px] font-mono px-2 py-0.5 rounded border ${
                isAttacked
                  ? 'bg-red-950 text-red-300 border-red-800 font-bold'
                  : 'bg-purple-950 text-purple-300 border-purple-800'
              }`}
            >
              Stage 2
            </span>
          </div>

          <p className="text-[11px] text-slate-300 mb-3 leading-relaxed">
            Quantum state <span className="font-mono text-purple-300">|&psi;_A&rang;</span> transmits through fiber/air. Eve can attempt eavesdropping, bit-flips (Pauli-X), or state injection.
          </p>

          <div className="space-y-1.5 text-[10px] font-mono bg-[#040812] p-2.5 rounded-lg border border-blue-950 text-slate-300">
            <div className="flex justify-between items-center">
              <span className="text-slate-400 flex items-center gap-1">
                <Activity className="w-3 h-3 text-purple-400" /> Channel Status:
              </span>
              <span className={isAttacked ? 'text-red-400 font-bold' : 'text-emerald-400'}>
                {isAttacked ? 'TAMPERED / NOISY' : 'UNPERTURBED'}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-400 flex items-center gap-1">
                <ShieldAlert className="w-3.5 h-3.5 text-red-400" /> Eve Activity:
              </span>
              <span className={isAttacked ? 'text-red-300 font-bold' : 'text-slate-400'}>
                {isAttacked ? currentAttackName : 'Inactive (Clean)'}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-400 flex items-center gap-1">
                <Lock className="w-3 h-3 text-cyan-400" /> No-Cloning Theorem:
              </span>
              <span className="text-cyan-300">ENFORCED (Eve leaves trace)</span>
            </div>
          </div>

          {onNavigate && (
            <div className="mt-3 text-right">
              <span className="text-[10px] text-purple-400 group-hover:text-purple-200 font-semibold flex items-center justify-end gap-1">
                Simulate Eve Attack &rarr;
              </span>
            </div>
          )}
        </div>

        {/* STAGE 3: BOB (RECEIVER / VERIFIER) */}
        <div
          onClick={() => onNavigate && onNavigate('verification')}
          className={`p-4 rounded-xl border transition-all cursor-pointer relative overflow-hidden group ${
            activeStep === 'bob'
              ? 'bg-[#081e14]/90 border-emerald-400 ring-1 ring-emerald-400/50 shadow-lg shadow-emerald-950/50'
              : 'bg-[#070e1c]/80 border-blue-900/40 hover:border-emerald-500/50 hover:bg-[#071714]'
          }`}
        >
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <div className="p-2 rounded-lg bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                <ShieldCheck className="w-5 h-5 text-emerald-400" />
              </div>
              <div>
                <h3 className="text-xs font-extrabold text-emerald-300 uppercase tracking-wider font-sans">
                  BOB (VERIFIER)
                </h3>
                <span className="text-[10px] text-slate-400 font-mono">Quantum Receiver</span>
              </div>
            </div>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800">
              Stage 3
            </span>
          </div>

          <p className="text-[11px] text-slate-300 mb-3 leading-relaxed">
            Bob receives state <span className="font-mono text-purple-300">|&psi;_B&rang;</span>, reconstructs expected state <span className="font-mono text-cyan-300">|&psi;_exp&rang;</span>, performs multi-basis measurement (Z, X, Y), and computes statistical fidelity F.
          </p>

          <div className="space-y-1.5 text-[10px] font-mono bg-[#040812] p-2.5 rounded-lg border border-blue-950 text-slate-300">
            <div className="flex justify-between items-center">
              <span className="text-slate-400 flex items-center gap-1">
                <Activity className="w-3 h-3 text-emerald-400" /> Basis Measurement:
              </span>
              <span className="text-emerald-300">Z, X, Y Multi-Basis</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-400 flex items-center gap-1">
                <Zap className="w-3 h-3 text-cyan-400" /> Quantum Fidelity (F):
              </span>
              <span className={isAttacked ? 'text-red-400 font-bold' : 'text-emerald-400 font-bold'}>
                {isAttacked ? 'F < 0.90 (Degraded)' : 'F ≥ 0.99 (Authentic)'}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-400 flex items-center gap-1">
                <CheckCircle2 className="w-3 h-3 text-emerald-400" /> Final Decision:
              </span>
              <span className={isAttacked ? 'text-red-400 font-extrabold' : 'text-emerald-400 font-extrabold'}>
                {isAttacked ? 'ATTACK DETECTED' : 'LEGITIMATE'}
              </span>
            </div>
          </div>

          {onNavigate && (
            <div className="mt-3 text-right">
              <span className="text-[10px] text-emerald-400 group-hover:text-emerald-200 font-semibold flex items-center justify-end gap-1">
                Open Bob's Verifier &rarr;
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
