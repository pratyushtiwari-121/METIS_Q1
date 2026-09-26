import React from 'react';
import type { StateVectorInfo } from '../../types';

interface BlochSphereProps {
  stateInfo: StateVectorInfo;
  tamperedState?: StateVectorInfo | null;
  size?: number;
  showDetails?: boolean;
}

export const BlochSphere: React.FC<BlochSphereProps> = ({
  stateInfo,
  tamperedState,
  size = 220,
  showDetails = true
}) => {
  // Center and Radius
  const cx = size / 2;
  const cy = size / 2;
  const r = (size / 2) * 0.78;

  // Calculate 3D projected endpoint for primary vector
  // x = sin(theta) * cos(phi)
  // y = sin(theta) * sin(phi)
  // z = cos(theta)
  // Isometric/Cabinet 2D projection:
  // screen_x = cx + r * (x * cos(-30°) + y * cos(60°))
  // screen_y = cy - r * z + r * 0.35 * (x * sin(-30°) + y * sin(60°))
  const getProjectedCoords = (theta: number, phi: number) => {
    const x = Math.sin(theta) * Math.cos(phi);
    const y = Math.sin(theta) * Math.sin(phi);
    const z = Math.cos(theta);

    // 2D projection angles
    const px = cx + r * (0.866 * y - 0.707 * x * 0.6);
    const py = cy - r * z + r * (0.35 * x + 0.2 * y);

    return { px, py, z };
  };

  const primary = getProjectedCoords(stateInfo.theta_rad, stateInfo.phi_rad);
  const tampered = tamperedState
    ? getProjectedCoords(tamperedState.theta_rad, tamperedState.phi_rad)
    : null;

  return (
    <div className="flex flex-col md:flex-row items-center gap-6 p-4 rounded-xl bg-[#0a1122]/90 border border-blue-500/20">
      {/* 3D SVG Bloch Sphere Sphere */}
      <div className="relative shrink-0 flex items-center justify-center" style={{ width: size, height: size }}>
        <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} className="overflow-visible select-none">
          <defs>
            {/* Sphere radial gradient glow */}
            <radialGradient id="sphereGrad" cx="40%" cy="40%" r="65%">
              <stop offset="0%" stopColor="#1e3a8a" stopOpacity="0.4" />
              <stop offset="70%" stopColor="#0f172a" stopOpacity="0.8" />
              <stop offset="100%" stopColor="#020617" stopOpacity="0.95" />
            </radialGradient>

            {/* Glowing marker for vector head */}
            <filter id="glowCyan" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="3" result="blur" />
              <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
            <filter id="glowRed" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="3" result="blur" />
              <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
          </defs>

          {/* Sphere Body */}
          <circle cx={cx} cy={cy} r={r} fill="url(#sphereGrad)" stroke="#38bdf8" strokeWidth="1.2" strokeOpacity="0.4" />

          {/* Latitude Equator (Elliptical) */}
          <ellipse cx={cx} cy={cy} rx={r} ry={r * 0.32} fill="none" stroke="#0284c7" strokeWidth="1" strokeDasharray="3,3" strokeOpacity="0.5" />

          {/* Meridian Longitude (Vertical Ellipse) */}
          <ellipse cx={cx} cy={cy} rx={r * 0.32} ry={r} fill="none" stroke="#0284c7" strokeWidth="1" strokeDasharray="3,3" strokeOpacity="0.4" />

          {/* Z-Axis (Vertical: |0> to |1>) */}
          <line x1={cx} y1={cy - r - 12} x2={cx} y2={cy + r + 12} stroke="#64748b" strokeWidth="1" strokeOpacity="0.6" />
          <text x={cx} y={cy - r - 16} fill="#38bdf8" fontSize="10" textAnchor="middle" fontWeight="bold" fontFamily="monospace">|0⟩ (Z)</text>
          <text x={cx} y={cy + r + 24} fill="#94a3b8" fontSize="10" textAnchor="middle" fontWeight="bold" fontFamily="monospace">|1⟩</text>

          {/* X-Axis (Diagonal left-down) */}
          <line x1={cx - r * 0.7} y1={cy + r * 0.45} x2={cx + r * 0.7} y2={cy - r * 0.45} stroke="#64748b" strokeWidth="1" strokeOpacity="0.6" />
          <text x={cx - r * 0.7 - 8} y={cy + r * 0.45 + 10} fill="#94a3b8" fontSize="10" textAnchor="middle" fontWeight="bold" fontFamily="monospace">X</text>

          {/* Y-Axis (Horizontal right) */}
          <line x1={cx - r - 8} y1={cy} x2={cx + r + 8} y2={cy} stroke="#64748b" strokeWidth="1" strokeOpacity="0.6" />
          <text x={cx + r + 16} y={cy + 4} fill="#94a3b8" fontSize="10" textAnchor="middle" fontWeight="bold" fontFamily="monospace">Y</text>

          {/* Center Dot */}
          <circle cx={cx} cy={cy} r="2.5" fill="#38bdf8" />

          {/* Primary State Vector (Cyan / Purple Needle) */}
          <line
            x1={cx}
            y1={cy}
            x2={primary.px}
            y2={primary.py}
            stroke="#a855f7"
            strokeWidth="2.5"
            filter="url(#glowCyan)"
          />
          <circle
            cx={primary.px}
            cy={primary.py}
            r="4.5"
            fill="#c084fc"
            stroke="#ffffff"
            strokeWidth="1.5"
            filter="url(#glowCyan)"
          />

          {/* Tampered / Modified State Vector (Red Needle if present) */}
          {tampered && (
            <>
              <line
                x1={cx}
                y1={cy}
                x2={tampered.px}
                y2={tampered.py}
                stroke="#ef4444"
                strokeWidth="2.5"
                filter="url(#glowRed)"
              />
              <circle
                cx={tampered.px}
                cy={tampered.py}
                r="4.5"
                fill="#ef4444"
                stroke="#ffffff"
                strokeWidth="1.5"
                filter="url(#glowRed)"
              />
            </>
          )}
        </svg>
      </div>

      {/* State Parameters Card */}
      {showDetails && (
        <div className="flex-1 w-full space-y-3 font-mono text-xs">
          <div>
            <p className="text-slate-400 text-[11px] font-sans">State Vector |ψ⟩</p>
            <div className="p-2 mt-1 rounded bg-[#070b16] border border-blue-900/40 text-cyan-300 font-semibold tracking-wide">
              {stateInfo.state_str}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-2 text-[11px]">
            <div className="p-2 rounded bg-[#070b16]/80 border border-slate-800">
              <span className="text-slate-400 block font-sans">α (|0⟩)</span>
              <span className="text-slate-200 font-bold">{stateInfo.alpha.real.toFixed(4)}</span>
              <span className="text-[10px] text-slate-500 block">Prob: {(stateInfo.prob_0 * 100).toFixed(1)}%</span>
            </div>
            <div className="p-2 rounded bg-[#070b16]/80 border border-slate-800">
              <span className="text-slate-400 block font-sans">β (|1⟩)</span>
              <span className="text-slate-200 font-bold">
                {stateInfo.beta.real.toFixed(4)} {stateInfo.beta.imag >= 0 ? '+' : ''}{stateInfo.beta.imag.toFixed(4)}i
              </span>
              <span className="text-[10px] text-slate-500 block">Prob: {(stateInfo.prob_1 * 100).toFixed(1)}%</span>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-2 text-[11px]">
            <div className="p-2 rounded bg-[#070b16]/80 border border-slate-800">
              <span className="text-slate-400 block font-sans">θ (theta)</span>
              <span className="text-purple-300 font-semibold">{stateInfo.theta_rad.toFixed(4)} rad</span>
              <span className="text-[10px] text-slate-500 block">({stateInfo.theta_deg.toFixed(1)}°)</span>
            </div>
            <div className="p-2 rounded bg-[#070b16]/80 border border-slate-800">
              <span className="text-slate-400 block font-sans">φ (phi)</span>
              <span className="text-purple-300 font-semibold">{stateInfo.phi_rad.toFixed(4)} rad</span>
              <span className="text-[10px] text-slate-500 block">({stateInfo.phi_deg.toFixed(1)}°)</span>
            </div>
          </div>

          {tamperedState && (
            <div className="flex items-center gap-3 pt-1 text-[11px]">
              <span className="flex items-center gap-1.5 text-purple-400">
                <span className="w-2.5 h-2.5 rounded-full bg-purple-500"></span> Expected State
              </span>
              <span className="flex items-center gap-1.5 text-red-400">
                <span className="w-2.5 h-2.5 rounded-full bg-red-500"></span> Tampered State
              </span>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
