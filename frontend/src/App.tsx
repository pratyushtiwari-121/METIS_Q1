import React, { useState, useEffect, lazy, Suspense } from 'react';
import { MainLayout } from './layouts/MainLayout';
import type { SignatureGenerateResponse } from './types';

const DashboardPage = lazy(() => import('./pages/DashboardPage').then(m => ({ default: m.DashboardPage })));
const SignatureGenPage = lazy(() => import('./pages/SignatureGenPage').then(m => ({ default: m.SignatureGenPage })));
const VerificationPage = lazy(() => import('./pages/VerificationPage').then(m => ({ default: m.VerificationPage })));
const AttackSimPage = lazy(() => import('./pages/AttackSimPage').then(m => ({ default: m.AttackSimPage })));
const QuantumCircuitPage = lazy(() => import('./pages/QuantumCircuitPage').then(m => ({ default: m.QuantumCircuitPage })));
const KeyDistributionPage = lazy(() => import('./pages/KeyDistributionPage').then(m => ({ default: m.KeyDistributionPage })));
const ForgeryAnalysisPage = lazy(() => import('./pages/ForgeryAnalysisPage').then(m => ({ default: m.ForgeryAnalysisPage })));
const PerformancePage = lazy(() => import('./pages/PerformancePage').then(m => ({ default: m.PerformancePage })));
const PhysicsLabPage = lazy(() => import('./pages/PhysicsLabPage').then(m => ({ default: m.PhysicsLabPage })));
const PqcComparisonPage = lazy(() => import('./pages/PqcComparisonPage').then(m => ({ default: m.PqcComparisonPage })));
const AnalyticsPage = lazy(() => import('./pages/AnalyticsPage').then(m => ({ default: m.AnalyticsPage })));
const LogsPage = lazy(() => import('./pages/LogsPage').then(m => ({ default: m.LogsPage })));
const SettingsPage = lazy(() => import('./pages/SettingsPage').then(m => ({ default: m.SettingsPage })));

function PageLoadingFallback() {
  return (
    <div className="flex items-center justify-center min-h-[400px] w-full">
      <div className="flex flex-col items-center gap-3">
        <div className="w-8 h-8 rounded-full border-2 border-cyan-500/20 border-t-cyan-400 animate-spin" />
        <span className="text-xs text-slate-400 font-mono tracking-wider">LOADING MODULE...</span>
      </div>
    </div>
  );
}

const VALID_ROUTES = new Set([
  'dashboard',
  'signature-generation',
  'verification',
  'attack-simulation',
  'quantum-circuit',
  'key-distribution',
  'forgery-analysis',
  'performance',
  'physics-lab',
  'pqc-comparison',
  'analytics',
  'logs',
  'settings',
]);

export function App() {
  const [currentRoute, setCurrentRoute] = useState<string>('dashboard');
  const [selectedSignature, setSelectedSignature] = useState<SignatureGenerateResponse | null>(null);
  const [selectedAttack, setSelectedAttack] = useState<any | null>(null);

  // Sync with window.location.hash for direct URL bookmarking without page reload.
  // On initial load: if there is no hash (new tab / fresh open), always land on dashboard.
  // On hashchange: follow the hash only when it is a known valid route.
  useEffect(() => {
    const getRouteFromHash = () =>
      window.location.hash.replace('#/', '').replace('#', '');

    // Initial load — only honour the hash if it maps to a real page.
    const initialHash = getRouteFromHash();
    if (initialHash && VALID_ROUTES.has(initialHash)) {
      setCurrentRoute(initialHash);
    } else {
      // No hash or unrecognised hash → go to dashboard and update the URL.
      setCurrentRoute('dashboard');
      window.location.hash = '#/dashboard';
    }

    const handleHashChange = () => {
      const hash = getRouteFromHash();
      if (hash && VALID_ROUTES.has(hash)) {
        setCurrentRoute(hash);
      }
    };

    window.addEventListener('hashchange', handleHashChange);
    return () => window.removeEventListener('hashchange', handleHashChange);
  }, []);

  const navigate = (route: string) => {
    setCurrentRoute(route);
    window.location.hash = `#/${route}`;
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const renderCurrentPage = () => {
    switch (currentRoute) {
      case 'dashboard':
        return <DashboardPage onNavigate={navigate} />;
      case 'signature-generation':
        return (
          <SignatureGenPage
            onNavigate={navigate}
            onSelectSignatureForVerify={(sig) => setSelectedSignature(sig)}
          />
        );
      case 'verification':
        return (
          <VerificationPage
            onNavigate={navigate}
            preselectedSignature={selectedSignature}
            preselectedAttack={selectedAttack}
            onClearAttack={() => setSelectedAttack(null)}
          />
        );
      case 'attack-simulation':
        return (
          <AttackSimPage
            onNavigate={navigate}
            activeAttack={selectedAttack}
            onUpdateAttack={(atk) => setSelectedAttack(atk)}
            onSelectAttackForVerify={(atk) => {
              setSelectedAttack(atk);
              navigate('verification');
            }}
          />
        );
      case 'quantum-circuit':
        return <QuantumCircuitPage />;
      case 'key-distribution':
        return <KeyDistributionPage />;
      case 'forgery-analysis':
        return <ForgeryAnalysisPage />;
      case 'performance':
        return <PerformancePage />;
      case 'physics-lab':
        return <PhysicsLabPage />;
      case 'pqc-comparison':
        return <PqcComparisonPage />;
      case 'analytics':
        return <AnalyticsPage />;
      case 'logs':
        return <LogsPage />;
      case 'settings':
        return <SettingsPage />;
      default:
        return <DashboardPage onNavigate={navigate} />;
    }
  };

  return (
    <MainLayout currentRoute={currentRoute} onNavigate={navigate}>
      <Suspense fallback={<PageLoadingFallback />}>
        {renderCurrentPage()}
      </Suspense>
    </MainLayout>
  );
}

export default App;
