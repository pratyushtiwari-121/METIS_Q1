import React from 'react';
import {
  LayoutDashboard,
  KeyRound,
  ShieldCheck,
  ShieldAlert,
  Cpu,
  BarChart3,
  FileText,
  Settings,
  Atom,
  FlaskConical,
  Scale,
  Share2,
  TrendingDown,
  Zap
} from 'lucide-react';

interface SidebarProps {
  currentRoute: string;
  onNavigate: (route: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentRoute, onNavigate }) => {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'key-distribution', label: 'Key Distribution', icon: Share2 },
    { id: 'signature-generation', label: 'Signature Generation', icon: KeyRound },
    { id: 'verification', label: 'Verification', icon: ShieldCheck },
    { id: 'attack-simulation', label: 'Attack Simulation', icon: ShieldAlert },
    { id: 'forgery-analysis', label: 'Forgery Analysis', icon: TrendingDown },
    { id: 'performance', label: 'Performance', icon: Zap },
    { id: 'quantum-circuit', label: 'Quantum Circuit', icon: Cpu },
    { id: 'physics-lab', label: 'Quantum Physics Lab', icon: FlaskConical },
    { id: 'pqc-comparison', label: 'PQC vs QDS', icon: Scale },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 },
    { id: 'logs', label: 'Logs', icon: FileText },
    { id: 'settings', label: 'Settings', icon: Settings }
  ];

  return (
    <aside className="w-64 bg-[#090e1a]/95 border-r border-blue-900/30 flex flex-col justify-between shrink-0 select-none min-h-screen">
      {/* Brand Header */}
      <div>
        <div className="p-5 border-b border-blue-900/30 flex items-center gap-3">
          <div className="relative flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-600 via-blue-600 to-purple-600 shadow-lg shadow-cyan-500/20">
            <Atom className="w-6 h-6 text-white animate-spin-slow" />
            <div className="absolute inset-0 rounded-xl bg-cyan-400/20 blur-sm"></div>
          </div>
          <div>
            <h1 className="font-bold text-sm leading-tight text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-blue-200 to-purple-300">
              Quantum Digital
            </h1>
            <p className="text-xs text-slate-400 font-medium">Signature Security</p>
          </div>
        </div>

        {/* Navigation List */}
        <nav className="p-3 space-y-1.5 mt-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentRoute === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onNavigate(item.id)}
                className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 ${
                  isActive
                    ? 'bg-gradient-to-r from-blue-600/30 via-cyan-600/20 to-transparent text-cyan-300 border-l-4 border-cyan-400 shadow-sm shadow-cyan-500/10'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
                }`}
              >
                <Icon className={`w-4 h-4 transition-colors ${isActive ? 'text-cyan-400' : 'text-slate-500'}`} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Futuristic Bottom Globe Widget */}
      <div className="p-4 m-3 rounded-xl bg-gradient-to-b from-[#0d162a]/80 to-[#0b1020]/90 border border-blue-500/20 relative overflow-hidden text-center">
        {/* Wireframe Orb Decorative Effect */}
        <div className="relative w-24 h-24 mx-auto my-1 flex items-center justify-center">
          <div className="absolute inset-0 rounded-full border border-cyan-500/30 animate-spin-slow"></div>
          <div className="absolute inset-2 rounded-full border border-purple-500/30 animate-reverse"></div>
          <div className="absolute inset-4 rounded-full border border-blue-400/20"></div>
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-cyan-500/20 to-purple-600/30 blur-md"></div>
          <Atom className="w-8 h-8 text-cyan-400/80 animate-pulse" />
        </div>
        <p className="text-[11px] text-cyan-300/80 italic font-mono mt-2">
          &ldquo;Quantum Security for a Safer Digital Tomorrow&rdquo;
        </p>
      </div>
    </aside>
  );
};
