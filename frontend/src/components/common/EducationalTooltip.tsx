import React, { useState } from 'react';
import { Info } from 'lucide-react';

interface EducationalTooltipProps {
  term: string;
  explanation: string;
  position?: 'top' | 'bottom' | 'left' | 'right';
}

export const EducationalTooltip: React.FC<EducationalTooltipProps> = ({
  term,
  explanation,
  position = 'top'
}) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="relative inline-flex items-center ml-1 group">
      <button
        type="button"
        onMouseEnter={() => setIsOpen(true)}
        onMouseLeave={() => setIsOpen(false)}
        onClick={() => setIsOpen(!isOpen)}
        className="text-slate-400 hover:text-cyan-400 transition-colors p-0.5 rounded focus:outline-none"
        aria-label={`Info about ${term}`}
      >
        <Info className="w-3.5 h-3.5" />
      </button>

      {isOpen && (
        <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-64 p-3 rounded-lg bg-[#0c1427] border border-cyan-500/40 shadow-xl shadow-cyan-950/50 z-50 text-xs text-slate-200 pointer-events-none animate-fadeIn">
          <div className="font-bold text-cyan-300 mb-1 flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400"></span>
            {term}
          </div>
          <p className="text-[11px] leading-relaxed text-slate-300 font-sans">{explanation}</p>
          <div className="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-[#0c1427]"></div>
        </div>
      )}
    </div>
  );
};
