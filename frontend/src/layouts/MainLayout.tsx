import React from 'react';
import { Sidebar } from '../components/common/Sidebar';
import { TopNavbar } from '../components/common/TopNavbar';

interface MainLayoutProps {
  currentRoute: string;
  onNavigate: (route: string) => void;
  children: React.ReactNode;
}

export const MainLayout: React.FC<MainLayoutProps> = ({
  currentRoute,
  onNavigate,
  children
}) => {
  return (
    <div className="flex min-h-screen bg-[#070b14] text-slate-100 selection:bg-cyan-500/30 selection:text-cyan-200">
      {/* Persistent Left Sidebar */}
      <Sidebar currentRoute={currentRoute} onNavigate={onNavigate} />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        <TopNavbar currentRoute={currentRoute} />

        <main className="flex-1 p-6 md:p-8 max-w-7xl w-full mx-auto overflow-y-auto">
          {children}
        </main>

        {/* Global Footer matching screenshots */}
        <footer className="h-12 px-6 bg-[#070b14]/90 border-t border-blue-900/20 flex items-center justify-between text-[11px] text-slate-500 font-mono shrink-0">
          <div>
            Quantum Digital Signature Security &nbsp;|&nbsp; SIH 2025 &nbsp;|&nbsp; Mentis-Q Framework
          </div>
          <div className="hidden sm:block text-slate-400">
            Powered by Quantum Computing for a Safer Tomorrow
          </div>
        </footer>
      </div>
    </div>
  );
};
