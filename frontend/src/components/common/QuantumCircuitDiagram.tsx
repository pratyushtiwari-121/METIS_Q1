import React from 'react';
import { Gauge } from 'lucide-react';

interface GateNode {
  type: string;
  qubit: number;
  target?: number;
  control?: number;
  param?: string;
  step: number;
}

interface QuantumCircuitDiagramProps {
  qubits?: number;
  title?: string;
  preset?: 'signature_gen' | 'bell_state' | 'teleportation' | 'verification' | 'custom';
  customGates?: GateNode[];
}

export const QuantumCircuitDiagram: React.FC<QuantumCircuitDiagramProps> = ({
  qubits = 3,
  title = 'Quantum Circuit',
  preset = 'signature_gen',
  customGates
}) => {
  // Preset circuit visual layout definitions matching the screenshots
  if (preset === 'signature_gen') {
    return (
      <div className="p-4 rounded-xl bg-[#0a1122]/90 border border-blue-500/20 overflow-x-auto select-none">
        <div className="min-w-[480px] space-y-4 font-mono text-xs">
          {/* Qubit 0 (Message State) */}
          <div className="flex items-center gap-2">
            <span className="w-16 text-slate-300 font-semibold text-[11px] shrink-0">q0 |ψ⟩</span>
            <div className="flex-1 flex items-center relative">
              <div className="h-[2px] bg-blue-500/40 w-full absolute top-1/2 -translate-y-1/2"></div>
              <div className="flex items-center justify-between w-full relative z-10 px-2">
                <div className="w-10 h-10 rounded-lg bg-purple-600/90 border border-purple-400/50 flex items-center justify-center font-bold text-white shadow-md shadow-purple-900/40">
                  H
                </div>
                <div className="w-4 h-4 rounded-full bg-cyan-400 flex items-center justify-center mx-auto"></div>
                <div className="w-10 h-10 rounded-lg bg-blue-900/80 border border-blue-400/50 flex items-center justify-center text-cyan-300 font-bold">
                  <Gauge className="w-5 h-5" />
                </div>
                <div className="w-10 h-10 rounded-lg bg-blue-900/80 border border-blue-400/50 flex items-center justify-center text-cyan-300 font-bold">
                  M
                </div>
              </div>
            </div>
          </div>

          {/* Qubit 1 (Entangled Pair Sender) */}
          <div className="flex items-center gap-2">
            <span className="w-16 text-slate-300 font-semibold text-[11px] shrink-0">q1 |0⟩</span>
            <div className="flex-1 flex items-center relative">
              <div className="h-[2px] bg-blue-500/40 w-full absolute top-1/2 -translate-y-1/2"></div>
              <div className="flex items-center justify-between w-full relative z-10 px-2">
                <div className="w-10 h-10 rounded-lg bg-purple-600/90 border border-purple-400/50 flex items-center justify-center font-bold text-white shadow-md shadow-purple-900/40">
                  H
                </div>
                <div className="w-10 h-10 rounded-lg bg-blue-600/90 border border-blue-400/50 flex items-center justify-center font-bold text-white shadow-md shadow-blue-900/40">
                  X
                </div>
                <div className="w-10 h-10 rounded-lg bg-blue-900/80 border border-blue-400/50 flex items-center justify-center text-cyan-300 font-bold">
                  <Gauge className="w-5 h-5" />
                </div>
                <div className="w-10 h-10 rounded-lg bg-blue-900/80 border border-blue-400/50 flex items-center justify-center text-cyan-300 font-bold">
                  M
                </div>
              </div>
            </div>
          </div>

          {/* Qubit 2 (Receiver Qubit) */}
          <div className="flex items-center gap-2">
            <span className="w-16 text-slate-300 font-semibold text-[11px] shrink-0">q2 |0⟩</span>
            <div className="flex-1 flex items-center relative">
              <div className="h-[2px] bg-blue-500/40 w-full absolute top-1/2 -translate-y-1/2"></div>
              <div className="flex items-center justify-between w-full relative z-10 px-2">
                <div className="w-10 h-10 flex items-center justify-center">
                  <div className="w-6 h-6 rounded-full border-2 border-cyan-400 flex items-center justify-center text-cyan-400 font-bold">+</div>
                </div>
                <div className="w-10 h-10"></div>
                <div className="w-10 h-10 rounded-lg bg-slate-800 border border-slate-600 flex items-center justify-center font-bold text-slate-300">
                  Z
                </div>
                <div className="w-10 h-10 rounded-lg bg-blue-600/90 border border-blue-400/50 flex items-center justify-center font-bold text-white">
                  X
                </div>
              </div>
            </div>
          </div>

          {/* Legend Footer */}
          <div className="flex items-center gap-6 pt-3 border-t border-slate-800 text-[11px] font-sans text-slate-400">
            <div className="flex items-center gap-2">
              <span className="w-4 h-[2px] bg-blue-400"></span> Quantum Bit Line
            </div>
            <div className="flex items-center gap-2">
              <span className="w-4 h-[2px] border-b border-dashed border-slate-400"></span> Classical Bit
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (preset === 'bell_state') {
    return (
      <div className="p-4 rounded-xl bg-[#0a1122]/90 border border-blue-500/20 overflow-x-auto select-none">
        <div className="min-w-[360px] space-y-6 font-mono text-xs">
          {/* q0 */}
          <div className="flex items-center gap-3">
            <span className="w-14 text-slate-300 font-semibold text-[11px] shrink-0">q0 |0⟩</span>
            <div className="flex-1 flex items-center relative">
              <div className="h-[2px] bg-blue-500/40 w-full absolute top-1/2 -translate-y-1/2"></div>
              <div className="flex items-center justify-around w-full relative z-10">
                <div className="w-11 h-11 rounded-lg bg-purple-600/90 border border-purple-400/50 flex items-center justify-center font-bold text-white shadow-lg shadow-purple-900/40">
                  H
                </div>
                <div className="w-5 h-5 rounded-full bg-cyan-400 shadow-md shadow-cyan-400/50"></div>
                <div className="w-11 h-11 rounded-lg bg-blue-900/80 border border-blue-400/50 flex items-center justify-center text-cyan-300 font-bold">
                  M
                </div>
              </div>
            </div>
          </div>

          {/* q1 */}
          <div className="flex items-center gap-3">
            <span className="w-14 text-slate-300 font-semibold text-[11px] shrink-0">q1 |0⟩</span>
            <div className="flex-1 flex items-center relative">
              <div className="h-[2px] bg-blue-500/40 w-full absolute top-1/2 -translate-y-1/2"></div>
              <div className="flex items-center justify-around w-full relative z-10">
                <div className="w-11 h-11"></div>
                <div className="w-8 h-8 rounded-full border-2 border-cyan-400 bg-[#090e1a] flex items-center justify-center text-cyan-400 font-bold shadow-md">
                  ⊕
                </div>
                <div className="w-11 h-11 rounded-lg bg-blue-900/80 border border-blue-400/50 flex items-center justify-center text-cyan-300 font-bold">
                  M
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Default fallback
  return (
    <div className="p-4 rounded-xl bg-[#0a1122]/90 border border-blue-500/20 text-xs font-mono text-cyan-300">
      <div className="p-3 bg-black/40 rounded border border-slate-800">
        q0: ───[ Ry(θ) ]───[ Rz(φ) ]───[ M ]───
      </div>
    </div>
  );
};
