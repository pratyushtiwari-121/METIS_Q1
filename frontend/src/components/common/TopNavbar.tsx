import React, { useState, useEffect } from 'react';
import { User, Shield, ChevronDown } from 'lucide-react';

interface TopNavbarProps {
  currentRoute: string;
}

export const TopNavbar: React.FC<TopNavbarProps> = ({ currentRoute }) => {
  const [currentTime, setCurrentTime] = useState('');

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      const dateStr = now.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
      });
      const timeStr = now.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        hour12: false
      });
      setCurrentTime(`${dateStr}   ${timeStr}`);
    };

    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  const getRouteSubtitle = () => {
    switch (currentRoute) {
      case 'dashboard':
        return 'Overview of Quantum Digital Signature System';
      case 'signature-generation':
        return 'Create a quantum digital signature for your message';
      case 'verification':
        return 'Verify the authenticity and integrity of a quantum digital signature';
      case 'attack-simulation':
        return 'Test the resilience of quantum digital signatures against various attack scenarios';
      case 'quantum-circuit':
        return 'Design, simulate, and visualize quantum circuits for signature generation and verification';
      case 'physics-lab':
        return 'Interactive quantum physics laboratory for state tomography, channels, and Bell tests';
      case 'pqc-comparison':
        return 'Comparison between classical cryptography, NIST PQC, QKD, and Quantum Digital Signatures';
      case 'analytics':
        return 'System performance, fidelity metrics, and threat detection analytics';
      case 'logs':
        return 'Real-time security auditing and quantum event logs';
      case 'settings':
        return 'System parameters, simulator configurations, and security policies';
      default:
        return 'Quantum Digital Signature Protocol Simulator';
    }
  };

  return (
    <header className="h-16 px-6 bg-[#090e1a]/90 backdrop-blur-md border-b border-blue-900/30 flex items-center justify-between shrink-0 sticky top-0 z-30">
      {/* Page Title & Subtitle */}
      <div>
        <h2 className="text-base font-bold text-slate-100 flex items-center gap-2">
          Quantum Digital Signature Security
        </h2>
        <p className="text-xs text-slate-400">{getRouteSubtitle()}</p>
      </div>

      {/* Status, Date & Profile */}
      <div className="flex items-center gap-4">
        {/* Simulator Online Status */}
        <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-950/70 border border-emerald-500/40 text-emerald-300 text-xs font-semibold shadow-sm shadow-emerald-950/50 font-mono">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
          <span>LIVE SIMULATOR (Qiskit Aer)</span>
        </div>

        {/* Date & Time */}
        <div className="hidden sm:block text-xs font-mono text-slate-400 px-2 py-1 bg-slate-900/60 rounded border border-slate-800">
          {currentTime || 'May 10, 2025  14:32'}
        </div>

        {/* User / Team Profile */}
        <div className="flex items-center gap-2.5 pl-3 border-l border-slate-800">
          <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-cyan-600 to-purple-600 flex items-center justify-center text-white text-xs font-semibold shadow-inner">
            <User className="w-4 h-4" />
          </div>
          <div className="hidden md:block text-left">
            <p className="text-xs font-semibold text-slate-200 leading-tight">Security Operator</p>
            <p className="text-[10px] text-cyan-400/80 font-medium">Mentis-Q System</p>
          </div>
        </div>
      </div>
    </header>
  );
};
