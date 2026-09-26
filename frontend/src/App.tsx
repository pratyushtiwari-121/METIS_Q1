import React, { useState, useEffect } from 'react';
import { MainLayout } from './layouts/MainLayout';
import { DashboardPage } from './pages/DashboardPage';
import { SignatureGenPage } from './pages/SignatureGenPage';
import { VerificationPage } from './pages/VerificationPage';
import { AttackSimPage } from './pages/AttackSimPage';
import { QuantumCircuitPage } from './pages/QuantumCircuitPage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { LogsPage } from './pages/LogsPage';
import { SettingsPage } from './pages/SettingsPage';
import { PhysicsLabPage } from './pages/PhysicsLabPage';
import { PqcComparisonPage } from './pages/PqcComparisonPage';
import { KeyDistributionPage } from './pages/KeyDistributionPage';
import { ForgeryAnalysisPage } from './pages/ForgeryAnalysisPage';
import { PerformancePage } from './pages/PerformancePage';
import type { SignatureGenerateResponse } from './types';

export function App() {
  const [currentRoute, setCurrentRoute] = useState<string>('dashboard');
  const [selectedSignature, setSelectedSignature] = useState<SignatureGenerateResponse | null>(null);
  const [selectedAttack, setSelectedAttack] = useState<any | null>(null);

  // Sync with window.location.hash for direct URL bookmarking without page reload
  useEffect(() => {
    const handleHashChange = () => {
      const hash = window.location.hash.replace('#/', '').replace('#', '');
      if (hash) {
        setCurrentRoute(hash);
      }
    };

    handleHashChange();
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
      {renderCurrentPage()}
    </MainLayout>
  );
}

export default App;
