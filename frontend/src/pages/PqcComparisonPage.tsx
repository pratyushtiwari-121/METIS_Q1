import React from 'react';
import { Shield, Key, Cpu, Zap, Lock } from 'lucide-react';

export const PqcComparisonPage: React.FC = () => {
  return (
    <div className="space-y-6 pb-16">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
          <Shield className="w-6 h-6 text-purple-400" />
          Cryptographic Paradigm Comparison: Classical vs PQC vs QKD vs QDS
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Rigorous distinction between Post-Quantum Cryptography (PQC), Quantum Key Distribution (QKD), and Quantum Digital Signatures (QDS).
        </p>
      </div>

      {/* Critical Alert */}
      <div className="p-4 rounded-xl bg-blue-950/40 border border-cyan-500/30 text-xs text-slate-200 flex items-start gap-3">
        <Zap className="w-5 h-5 text-cyan-400 shrink-0 mt-0.5" />
        <div>
          <span className="font-bold text-cyan-300 block mb-1 font-sans uppercase tracking-wider">
            Critical Conceptual Distinction: PQC ≠ QKD ≠ QDS
          </span>
          <p className="leading-relaxed text-slate-300">
            These four paradigms solve different security problems on fundamentally different hardware layers:
            <span className="text-purple-300 font-semibold"> PQC</span> is classical math designed to resist quantum attacks;
            <span className="text-emerald-300 font-semibold"> QKD</span> generates symmetric encryption keys; and
            <span className="text-cyan-300 font-semibold"> QDS</span> provides non-repudiation and authentication using quantum mechanics.
          </p>
        </div>
      </div>

      {/* Comparison Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: Classical Public Key */}
        <div className="p-5 rounded-xl bg-[#0a1122]/90 border border-red-500/30 shadow-lg space-y-3 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-red-950 border border-red-500/40 text-red-300">
                Vulnerable to Shor
              </span>
              <Lock className="w-4 h-4 text-red-400" />
            </div>
            <h2 className="text-base font-bold text-slate-100">1. Classical Cryptography</h2>
            <p className="text-[11px] text-slate-400 mt-1">
              Standard public-key schemes based on unproven computational complexity assumptions.
            </p>
            <div className="space-y-1.5 pt-3 text-xs font-mono">
              <div className="text-slate-300"><span className="text-slate-500 font-sans">Algorithms:</span> RSA, ECDSA, Ed25519</div>
              <div className="text-slate-300"><span className="text-slate-500 font-sans">Hard Problem:</span> Factoring, Discrete Log</div>
              <div className="text-slate-300"><span className="text-slate-500 font-sans">Hardware:</span> Standard Classical CPU/ASIC</div>
              <div className="text-red-400 font-bold"><span className="text-slate-500 font-sans">Quantum Status:</span> BROKEN by Shor's algorithm</div>
            </div>
          </div>
          <div className="p-2 rounded bg-red-950/40 border border-red-900/40 text-[10px] text-red-300">
            Polynomial-time factorization on fault-tolerant quantum computers (FTQC).
          </div>
        </div>

        {/* Card 2: NIST PQC */}
        <div className="p-5 rounded-xl bg-[#0a1122]/90 border border-purple-500/30 shadow-lg space-y-3 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-purple-950 border border-purple-500/40 text-purple-300">
                NIST Standardized
              </span>
              <Cpu className="w-4 h-4 text-purple-400" />
            </div>
            <h2 className="text-base font-bold text-slate-100">2. Post-Quantum (PQC)</h2>
            <p className="text-[11px] text-slate-400 mt-1">
              Classical mathematical algorithms designed to resist quantum algorithms.
            </p>
            <div className="space-y-1.5 pt-3 text-xs font-mono">
              <div className="text-slate-300"><span className="text-slate-500 font-sans">Algorithms:</span> ML-DSA (Dilithium), SLH-DSA, Falcon</div>
              <div className="text-slate-300"><span className="text-slate-500 font-sans">Hard Problem:</span> Lattice Shortest Vector, Hash Trees</div>
              <div className="text-slate-300"><span className="text-slate-500 font-sans">Hardware:</span> Classical (runs on laptops, servers)</div>
              <div className="text-purple-300 font-bold"><span className="text-slate-500 font-sans">Quantum Status:</span> Computationally secure</div>
            </div>
          </div>
          <div className="p-2 rounded bg-purple-950/40 border border-purple-900/40 text-[10px] text-purple-300">
            No quantum hardware required. Security relies on classical mathematical hardness.
          </div>
        </div>

        {/* Card 3: QKD */}
        <div className="p-5 rounded-xl bg-[#0a1122]/90 border border-emerald-500/30 shadow-lg space-y-3 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-emerald-950 border border-emerald-500/40 text-emerald-300">
                Physical Key Exchange
              </span>
              <Key className="w-4 h-4 text-emerald-400" />
            </div>
            <h2 className="text-base font-bold text-slate-100">3. Quantum Key Distribution</h2>
            <p className="text-[11px] text-slate-400 mt-1">
              Physics-based protocol to securely establish secret symmetric keys between two parties.
            </p>
            <div className="space-y-1.5 pt-3 text-xs font-mono">
              <div className="text-slate-300"><span className="text-slate-500 font-sans">Protocols:</span> BB84, E91, Decoy-State</div>
              <div className="text-slate-300"><span className="text-slate-500 font-sans">Physical Basis:</span> No-Cloning Theorem, Conjugate Bases</div>
              <div className="text-slate-300"><span className="text-slate-500 font-sans">Hardware:</span> Optical Fibers, Single-Photon Detectors</div>
              <div className="text-emerald-300 font-bold"><span className="text-slate-500 font-sans">Functionality:</span> Key Exchange ONLY (No signatures)</div>
            </div>
          </div>
          <div className="p-2 rounded bg-emerald-950/40 border border-emerald-900/40 text-[10px] text-emerald-300">
            Cannot provide digital signatures or non-repudiation directly without separate machinery.
          </div>
        </div>

        {/* Card 4: QDS */}
        <div className="p-5 rounded-xl bg-[#0a1122]/90 border border-cyan-500/40 shadow-lg space-y-3 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-cyan-950 border border-cyan-500/50 text-cyan-300">
                Quantum Authentication
              </span>
              <Zap className="w-4 h-4 text-cyan-400" />
            </div>
            <h2 className="text-base font-bold text-slate-100">4. Quantum Digital Signatures</h2>
            <p className="text-[11px] text-slate-400 mt-1">
              Guarantees message authenticity, integrity, and non-repudiation via quantum states.
            </p>
            <div className="space-y-1.5 pt-3 text-xs font-mono">
              <div className="text-slate-300"><span className="text-slate-500 font-sans">Protocols:</span> Gottesman-Chuang, Teleportation QDS</div>
              <div className="text-slate-300"><span className="text-slate-500 font-sans">Physical Basis:</span> Teleportation, Bell Pairs, Projective Meas.</div>
              <div className="text-slate-300"><span className="text-slate-500 font-sans">Hardware:</span> Quantum Optical Network / Qiskit Aer</div>
              <div className="text-cyan-300 font-bold"><span className="text-slate-500 font-sans">Functionality:</span> Non-repudiation, Anti-forgery</div>
            </div>
          </div>
          <div className="p-2 rounded bg-cyan-950/40 border border-cyan-500/30 text-[10px] text-cyan-200">
            Eavesdropping and forgery are detected directly through state collapse and quantum measurement deviation.
          </div>
        </div>
      </div>

      {/* Comparison Table */}
      <div className="p-5 rounded-xl bg-[#0a1122]/90 border border-blue-500/20 shadow-lg space-y-4">
        <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider font-sans">
          Technical Feature Comparison Matrix
        </h2>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono border-collapse">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-sans">
                <th className="py-2 px-3">Security Metric / Property</th>
                <th className="py-2 px-3">Classical (RSA/ECC)</th>
                <th className="py-2 px-3">NIST PQC (Lattice/Hash)</th>
                <th className="py-2 px-3">QKD (e.g. BB84)</th>
                <th className="py-2 px-3 text-cyan-300">QDS (Teleportation)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              <tr>
                <td className="py-2.5 px-3 font-sans font-medium text-slate-200">Security Foundation</td>
                <td className="py-2.5 px-3 text-red-400">Computational hardness</td>
                <td className="py-2.5 px-3 text-purple-300">Computational hardness</td>
                <td className="py-2.5 px-3 text-emerald-400">Laws of Quantum Physics</td>
                <td className="py-2.5 px-3 text-cyan-300 font-bold">Laws of Quantum Physics</td>
              </tr>
              <tr>
                <td className="py-2.5 px-3 font-sans font-medium text-slate-200">Resistant to Shor's Algorithm</td>
                <td className="py-2.5 px-3 text-red-400">NO (Broken)</td>
                <td className="py-2.5 px-3 text-emerald-400">YES</td>
                <td className="py-2.5 px-3 text-emerald-400">YES</td>
                <td className="py-2.5 px-3 text-cyan-300 font-bold">YES</td>
              </tr>
              <tr>
                <td className="py-2.5 px-3 font-sans font-medium text-slate-200">Primary Cryptographic Purpose</td>
                <td className="py-2.5 px-3">Signatures & Encryption</td>
                <td className="py-2.5 px-3">Signatures & KEM</td>
                <td className="py-2.5 px-3 text-amber-300">Symmetric Key Distribution ONLY</td>
                <td className="py-2.5 px-3 text-cyan-300 font-bold">Signatures & Non-Repudiation</td>
              </tr>
              <tr>
                <td className="py-2.5 px-3 font-sans font-medium text-slate-200">Requires Quantum Channel</td>
                <td className="py-2.5 px-3">No</td>
                <td className="py-2.5 px-3">No</td>
                <td className="py-2.5 px-3 text-emerald-300">Yes (Optical fiber / free space)</td>
                <td className="py-2.5 px-3 text-cyan-300 font-bold">Yes (EPR Bell channel / Qiskit)</td>
              </tr>
              <tr>
                <td className="py-2.5 px-3 font-sans font-medium text-slate-200">Detection of Tampering</td>
                <td className="py-2.5 px-3">Hash mismatch only</td>
                <td className="py-2.5 px-3">Hash/Signature mismatch</td>
                <td className="py-2.5 px-3 text-emerald-300">Physical disturbance (QBER)</td>
                <td className="py-2.5 px-3 text-cyan-300 font-bold">Fidelity, TVD, QBER, Hoeffding</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
