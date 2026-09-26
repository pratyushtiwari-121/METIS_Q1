import React, { useState } from 'react';
import {
  KeyRound,
  FileText,
  Copy,
  Check,
  Send,
  Download,
  ArrowRight,
  ShieldCheck,
  Cpu,
  Layers,
  Sparkles,
  X
} from 'lucide-react';
import { BlochSphere } from '../components/common/BlochSphere';
import { QuantumCircuitDiagram } from '../components/common/QuantumCircuitDiagram';
import { EducationalTooltip } from '../components/common/EducationalTooltip';
import { AliceBobPipeline } from '../components/common/AliceBobPipeline';
import { api } from '../services/api';
import type { SignatureGenerateResponse, StateVectorInfo } from '../types';

interface SignatureGenPageProps {
  onNavigate: (route: string) => void;
  onSelectSignatureForVerify?: (sig: SignatureGenerateResponse) => void;
}

export const SignatureGenPage: React.FC<SignatureGenPageProps> = ({
  onNavigate,
  onSelectSignatureForVerify
}) => {
  const [message, setMessage] = useState('Secure communication with quantum signatures!');
  const [hashFunc, setHashFunc] = useState('SHA-256');
  const [encodingScheme, setEncodingScheme] = useState('Amplitude Encoding');
  const [activeTab, setActiveTab] = useState<'bloch' | 'statevector'>('bloch');
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);
  const [showCircuitModal, setShowCircuitModal] = useState(false);
  const [saveSuccessMsg, setSaveSuccessMsg] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<SignatureGenerateResponse | null>(null);

  // Default preview state vector before generation
  const defaultPreviewState: StateVectorInfo = {
    alpha: { real: 0.815, imag: 0.0 },
    beta: { real: 0.408, imag: 0.408 },
    theta_rad: 1.234,
    theta_deg: 70.7,
    phi_rad: 0.785,
    phi_deg: 45.0,
    prob_0: 0.664,
    prob_1: 0.336,
    state_str: '0.8150|0⟩ + (0.4080 + 0.4080i)|1⟩'
  };

  const handleGenerate = async () => {
    if (!message.trim()) return;
    try {
      setLoading(true);
      setError(null);
      const res = await api.generateSignature({
        message: message.trim(),
        hash_function: hashFunc,
        encoding_scheme: encodingScheme,
        shots: 1024
      });
      setResult(res);
      if (onSelectSignatureForVerify) {
        onSelectSignatureForVerify(res);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to generate quantum signature.');
    } finally {
      setLoading(false);
    }
  };

  const handleCopyHash = () => {
    const hashToCopy = result?.message_hash || '3f7a9c8e4d2b1e6f0c9a8d7e5b4c3a2d1e0f9a8b7c6d5e4f3a2b1c0d9e8f7a6';
    navigator.clipboard.writeText(hashToCopy);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleSaveSignature = () => {
    const sigData = result || {
      signature_id: 'QSIG-2025-0510-001',
      message: message,
      message_hash: '3f7a9c8e4d2b1e6f0c9a8d7e5b4c3a2d1e0f9a8b7c6d5e4f3a2b1c0d9e8f7a6',
      state_vector: defaultPreviewState,
      classical_bits: '10',
      quantum_fidelity: 0.992,
      timestamp: new Date().toISOString()
    };
    const blob = new Blob([JSON.stringify(sigData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${sigData.signature_id}.json`;
    a.click();
    URL.revokeObjectURL(url);
    setSaveSuccessMsg(`Signature ${sigData.signature_id} downloaded as JSON file!`);
    setTimeout(() => setSaveSuccessMsg(null), 3500);
  };

  const handleSendToVerify = () => {
    if (result && onSelectSignatureForVerify) {
      onSelectSignatureForVerify(result);
    }
    onNavigate('verification');
  };

  const currentDisplayState = result ? result.state_vector : defaultPreviewState;

  return (
    <div className="space-y-6 pb-12">
      {/* Top Header & Subtitle */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            Signature Generation (Alice)
          </h1>
          <p className="text-xs text-slate-400">
            Alice (Sender) computes SHA-256 digest and encodes quantum state vector <span className="font-mono text-purple-300">|&psi;_A&rang;</span>
          </p>
          <div className="flex flex-wrap items-center gap-2 mt-2">
            <span className="px-2.5 py-0.5 rounded text-[10px] font-mono font-bold bg-amber-950/80 border border-amber-500/40 text-amber-300">
              LEGACY DEMO (NOT SECURE)
            </span>
            <span className="text-[11px] text-slate-400">
              For information-theoretically secure QDS, see{' '}
              <button
                type="button"
                onClick={() => onNavigate('key-distribution')}
                className="text-cyan-400 hover:underline cursor-pointer"
              >
                Key Distribution
              </button>{' '}
              and{' '}
              <button
                type="button"
                onClick={() => onNavigate('forgery-analysis')}
                className="text-cyan-400 hover:underline cursor-pointer"
              >
                Forgery Analysis
              </button>.
            </span>
          </div>
        </div>
        <div className="text-xs font-mono text-slate-500">
          Alice &amp; Bob Pipeline &gt; <span className="text-cyan-400">Stage 1: Alice (Sender)</span>
        </div>
      </div>

      {/* Protocol Pipeline Banner */}
      <AliceBobPipeline onNavigate={onNavigate} activeStep="alice" />

      {/* Step Indicators */}
      <div className="flex items-center justify-center p-3 rounded-xl bg-[#0a1122]/80 border border-blue-500/20 max-w-2xl mx-auto">
        <div className="flex items-center gap-2 sm:gap-6 text-xs font-medium">
          {[
            { num: 1, label: 'Input Message' },
            { num: 2, label: 'State Encoding' },
            { num: 3, label: 'Quantum Circuit' },
            { num: 4, label: 'Signature Output' }
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

      {saveSuccessMsg && (
        <div className="p-3 rounded-lg bg-emerald-950/70 border border-emerald-500/40 text-emerald-300 text-xs flex items-center gap-2">
          <Check className="w-4 h-4 text-emerald-400" />
          {saveSuccessMsg}
        </div>
      )}

      {error && (
        <div className="p-3 rounded-lg bg-red-950/60 border border-red-500/40 text-red-300 text-xs">
          {error}
        </div>
      )}

      {/* Main 2-Column Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 1. Input Message Card */}
        <div className="p-5 rounded-xl bg-[#0a1122]/90 border border-blue-500/20 shadow-lg space-y-4">
          <div className="flex items-center gap-2">
            <FileText className="w-4 h-4 text-cyan-400" />
            <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider font-sans">
              1. Input Message
            </h2>
          </div>

          <div>
            <div className="flex justify-between text-xs text-slate-400 mb-1">
              <span>Enter Message</span>
              <span className="font-mono">{message.length}/500</span>
            </div>
            <textarea
              value={message}
              onChange={(e) => setMessage(e.target.value.slice(0, 500))}
              rows={4}
              placeholder="Enter message to digitally sign..."
              className="w-full p-3 rounded-lg bg-[#070b16] border border-blue-900/40 text-xs text-slate-200 font-sans focus:outline-none focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400 resize-none"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-[11px] text-slate-400 flex items-center gap-1 mb-1">
                Hash Function
                <EducationalTooltip
                  term="Cryptographic Hash (SHA-256)"
                  explanation="Produces a deterministic 256-bit hash digest from the message payload."
                />
              </label>
              <select
                value={hashFunc}
                onChange={(e) => setHashFunc(e.target.value)}
                className="w-full p-2 rounded bg-[#070b16] border border-slate-800 text-xs text-slate-300 focus:outline-none focus:border-cyan-400 cursor-pointer"
              >
                <option value="SHA-256">SHA-256</option>
                <option value="SHA3-256">SHA3-256 (Post-Quantum)</option>
              </select>
            </div>

            <div>
              <label className="text-[11px] text-slate-400 flex items-center gap-1 mb-1">
                Encoding Scheme
                <EducationalTooltip
                  term="Amplitude Encoding"
                  explanation="Maps hash digest values into continuous quantum state parameters theta and phi."
                />
              </label>
              <select
                value={encodingScheme}
                onChange={(e) => setEncodingScheme(e.target.value)}
                className="w-full p-2 rounded bg-[#070b16] border border-slate-800 text-xs text-slate-300 focus:outline-none focus:border-cyan-400 cursor-pointer"
              >
                <option value="Amplitude Encoding">Amplitude Encoding</option>
                <option value="Angle Encoding">Angle Encoding</option>
              </select>
            </div>
          </div>

          <button
            onClick={handleGenerate}
            disabled={loading || !message.trim()}
            className="w-full py-2.5 px-4 rounded-lg bg-gradient-to-r from-blue-600 via-purple-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white font-semibold text-xs transition-all shadow-lg shadow-purple-900/30 flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
          >
            {loading ? (
              <span className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 animate-spin" />
                Executing Qiskit Simulation...
              </span>
            ) : (
              <>
                <ArrowRight className="w-4 h-4" />
                Proceed to State Encoding &amp; Sign
              </>
            )}
          </button>
        </div>

        {/* 2. Quantum State Encoding Card */}
        <div className="p-5 rounded-xl bg-[#0a1122]/90 border border-blue-500/20 shadow-lg space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Layers className="w-4 h-4 text-purple-400" />
              <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider font-sans">
                2. Quantum State Encoding
              </h2>
            </div>
            <div className="flex rounded-lg bg-[#070b16] p-0.5 border border-slate-800">
              <button
                onClick={() => setActiveTab('bloch')}
                className={`px-2.5 py-1 text-[11px] rounded font-medium transition-colors cursor-pointer ${
                  activeTab === 'bloch' ? 'bg-purple-600 text-white' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                Bloch Sphere View
              </button>
              <button
                onClick={() => setActiveTab('statevector')}
                className={`px-2.5 py-1 text-[11px] rounded font-medium transition-colors cursor-pointer ${
                  activeTab === 'statevector' ? 'bg-purple-600 text-white' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                State Vector
              </button>
            </div>
          </div>

          {activeTab === 'bloch' ? (
            <BlochSphere stateInfo={currentDisplayState} size={200} showDetails={true} />
          ) : (
            <div className="p-4 rounded-xl bg-[#070b16] border border-blue-900/40 space-y-4 font-mono text-xs">
              <div>
                <span className="text-slate-400 text-[11px] font-sans block">Matrix Amplitude Representation:</span>
                <div className="p-3 mt-1 rounded bg-[#090e1a] border border-purple-500/30 text-cyan-300 font-bold">
                  |ψ⟩ = [{currentDisplayState.alpha.real.toFixed(4)} , {currentDisplayState.beta.real.toFixed(4)} + {currentDisplayState.beta.imag.toFixed(4)}i]ᵀ
                </div>
              </div>
              <div className="space-y-2 text-[11px]">
                <div className="flex justify-between p-2 rounded bg-slate-900/60 border border-slate-800">
                  <span className="text-slate-400 font-sans">Basis |0⟩ Amplitude (α):</span>
                  <span className="text-slate-200 font-bold">{currentDisplayState.alpha.real.toFixed(4)}</span>
                </div>
                <div className="flex justify-between p-2 rounded bg-slate-900/60 border border-slate-800">
                  <span className="text-slate-400 font-sans">Basis |1⟩ Amplitude (β):</span>
                  <span className="text-slate-200 font-bold">{currentDisplayState.beta.real.toFixed(4)} + {currentDisplayState.beta.imag.toFixed(4)}i</span>
                </div>
                <div className="flex justify-between p-2 rounded bg-slate-900/60 border border-slate-800">
                  <span className="text-slate-400 font-sans">Normalization Condition:</span>
                  <span className="text-emerald-400 font-bold">|α|² + |β|² = 1.0000</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Message Hash & Encoding Details (Side Column) */}
        <div className="p-5 rounded-xl bg-[#0a1122]/90 border border-blue-500/20 shadow-lg space-y-4 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 mb-3">
              <KeyRound className="w-4 h-4 text-cyan-400" />
              <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider font-sans">
                Message Hash &amp; Encoding
              </h2>
            </div>

            <div className="space-y-3">
              <div>
                <div className="flex items-center justify-between text-[11px] text-slate-400 mb-1">
                  <span>SHA-256 Hash (hex)</span>
                  <button
                    onClick={handleCopyHash}
                    className="text-cyan-400 hover:text-cyan-300 flex items-center gap-1 text-[10px] cursor-pointer"
                  >
                    {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                    {copied ? 'Copied' : 'Copy'}
                  </button>
                </div>
                <div className="p-2.5 rounded bg-[#070b16] border border-blue-900/40 font-mono text-[11px] text-cyan-300 break-all leading-relaxed">
                  {result?.message_hash || '3f7a9c8e4d2b1e6f0c9a8d7e5b4c3a2d1e0f9a8b7c6d5e4f3a2b1c0d9e8f7a6'}
                </div>
              </div>

              <div>
                <span className="text-[11px] text-slate-400 block mb-1">Binary Representation (first 32 bits)</span>
                <div className="p-2 rounded bg-[#070b16] border border-slate-800 font-mono text-[11px] text-purple-300 tracking-wider">
                  {result?.binary_hash
                    ? result.binary_hash.slice(0, 32).match(/.{1,8}/g)?.join(' ')
                    : '00111111 01111010 10011100 10001110'}
                </div>
              </div>
            </div>
          </div>

          <div className="p-3 rounded-lg bg-blue-950/30 border border-blue-500/20 text-xs text-slate-300 flex items-start gap-2">
            <Sparkles className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
            <p className="text-[11px] leading-relaxed">
              The message is hashed and encoded into a quantum state. This state will be used for signature generation using entanglement and teleportation.
            </p>
          </div>
        </div>
      </div>

      {/* Row 2: 3. Quantum Circuit & 4. Signature Output */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 3. Quantum Circuit for Signature Generation */}
        <div className="lg:col-span-2 p-5 rounded-xl bg-[#0a1122]/90 border border-blue-500/20 shadow-lg space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Cpu className="w-4 h-4 text-cyan-400" />
              <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider font-sans">
                3. Quantum Circuit for Signature Generation
              </h2>
            </div>
            <button
              onClick={() => setShowCircuitModal(true)}
              className="text-xs text-cyan-400 hover:text-cyan-300 font-medium cursor-pointer"
            >
              View Full Circuit Details →
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-center">
            <div className="md:col-span-2">
              <QuantumCircuitDiagram preset="signature_gen" />
            </div>

            <div className="p-4 rounded-xl bg-[#060b17] border border-slate-800 space-y-2 text-xs">
              <h3 className="font-semibold text-slate-300 text-xs font-sans">Circuit Protocol</h3>
              <ol className="space-y-1.5 text-[11px] text-slate-400 font-sans list-decimal list-inside">
                <li>Apply Hadamard to create superposition</li>
                <li>Create entanglement (Bell state)</li>
                <li>Encode message quantum state</li>
                <li>Perform teleportation protocol</li>
                <li>Measure &amp; obtain classical bits</li>
                <li>Apply Pauli corrections</li>
              </ol>
            </div>
          </div>
        </div>

        {/* 4. Quantum Signature Output */}
        <div className="p-5 rounded-xl bg-[#0a1122]/90 border border-blue-500/20 shadow-lg space-y-4 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 mb-3">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider font-sans">
                4. Quantum Signature Output
              </h2>
            </div>

            <div className="p-3 rounded-lg bg-emerald-950/50 border border-emerald-500/40 text-emerald-300 text-xs flex items-center gap-2 mb-4">
              <Check className="w-4 h-4 text-emerald-400 shrink-0" />
              <div>
                <p className="font-bold">Quantum Signature Generated Successfully!</p>
                <p className="text-[10px] text-slate-300">The quantum signature is ready for transmission.</p>
              </div>
            </div>

            <div className="space-y-2 text-xs font-mono">
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400 font-sans">Signature ID</span>
                <span className="text-cyan-300 font-bold">{result?.signature_id || 'QSIG-2025-0510-001'}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400 font-sans">Timestamp</span>
                <span className="text-slate-300 text-[11px]">{result?.timestamp ? result.timestamp.slice(0, 19).replace('T', ' ') : '2025-05-10 14:32:15'}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400 font-sans">Classical Bits</span>
                <span className="text-purple-300 font-bold">{result?.classical_bits || '10'}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400 font-sans">Signature Copies (L)</span>
                <span className="text-cyan-300 font-bold">64 Pauli States</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400 font-sans">SHA-256 Binding</span>
                <span className="text-purple-300 font-mono text-[10px]">Active &bull; Token Verified</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400 font-sans">Pauli Correction</span>
                <span className="text-slate-200 font-semibold">{result?.pauli_correction || 'XZ'}</span>
              </div>
              <div className="flex justify-between py-1">
                <span className="text-slate-400 font-sans">Signature Fidelity</span>
                <span className="text-emerald-400 font-bold">{result?.fidelity ?? 0.992}</span>
              </div>
            </div>
          </div>

          <div className="space-y-2 pt-2">
            <button
              onClick={handleSaveSignature}
              className="w-full py-2 px-3 rounded-lg bg-blue-900/40 hover:bg-blue-800/60 border border-blue-500/30 text-cyan-300 text-xs font-semibold flex items-center justify-center gap-1.5 transition-colors cursor-pointer"
            >
              <Download className="w-3.5 h-3.5" />
              Save Signature (.json)
            </button>
            <button
              onClick={handleSendToVerify}
              className="w-full py-2 px-3 rounded-lg bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500 text-white text-xs font-semibold flex items-center justify-center gap-1.5 transition-all shadow-md shadow-purple-900/30 cursor-pointer"
            >
              <Send className="w-3.5 h-3.5" />
              Send for Verification →
            </button>
          </div>
        </div>
      </div>

      {/* Circuit Details Modal */}
      {showCircuitModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="w-full max-w-2xl p-6 rounded-2xl bg-[#0a1122] border border-cyan-500/40 shadow-2xl shadow-cyan-950/80 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="font-bold text-slate-100 flex items-center gap-2">
                <Cpu className="w-4 h-4 text-cyan-400" />
                Quantum Teleportation Signature Circuit
              </h3>
              <button
                onClick={() => setShowCircuitModal(false)}
                className="text-slate-400 hover:text-white transition-colors cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-4 rounded-xl bg-[#070b16] border border-blue-900/40 font-mono text-xs text-cyan-300 whitespace-pre overflow-x-auto">
              {result?.circuit_ascii ||
                `q_0: ──[ Ry(θ) ]──[ Rz(φ) ]──■──[ H ]──M───────
                                    │          │  
q_1: ────────[ H ]──────■───────────■──────────┼──M────
                        │                      │  │
q_2: ───────────────────X──────────────────────┼──┼─[X]─[Z]─
                                               │  │  │   │
c: 2/══════════════════════════════════════════╩══╩══╪═══╪═
                                               0  1  0   1 `}
            </div>

            <div className="p-3 rounded-lg bg-blue-950/30 border border-blue-500/20 text-xs text-slate-300">
              <p>
                <strong>Protocol Step Breakdown:</strong> Alice prepares the message quantum state $|\psi\rangle$ on $q_0$, generates an EPR Bell pair on $(q_1, q_2)$, entangles $q_0$ and $q_1$, and measures both. The classical measurement outputs dictate Bob&apos;s Pauli $X$ and $Z$ corrections on $q_2$ to recover $|\psi\rangle$.
              </p>
            </div>

            <button
              onClick={() => setShowCircuitModal(false)}
              className="w-full py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold cursor-pointer"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
