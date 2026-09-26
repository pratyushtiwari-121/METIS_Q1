import React, { useEffect, useState } from 'react';
import {
  FileText,
  ShieldCheck,
  ShieldAlert,
  Cpu,
  ArrowRight,
  KeyRound,
  Zap,
  Activity,
  CheckCircle2,
  AlertTriangle,
  RefreshCw
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  CartesianGrid
} from 'recharts';
import { MetricCard } from '../components/common/MetricCard';
import { AliceBobPipeline } from '../components/common/AliceBobPipeline';
import { api, checkBackendHealth, isBackendConfigured } from '../services/api';
import type { DashboardSummaryResponse } from '../types';


interface DashboardPageProps {
  onNavigate: (route: string) => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({ onNavigate }) => {
  const [data, setData] = useState<DashboardSummaryResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<string>('Just now');
  const [error, setError] = useState<string | null>(null);
  const [backendOnline, setBackendOnline] = useState<boolean | null>(null);


  const loadDashboardData = async (isBackground = false) => {
    try {
      if (!isBackground) setLoading(true);
      const res = await api.getDashboardSummary();
      setData(res);
      setLastUpdated(new Date().toLocaleTimeString());
      setError(null);
      setBackendOnline(true);
    } catch (err: any) {
      setBackendOnline(false);
      if (!isBackground) {
        const msg: string = err.message || 'Failed to fetch dashboard summary.';
        // Only surface non-network errors as inline errors; network errors show the banner.
        if (!msg.toLowerCase().includes('backend unreachable')) {
          setError(msg);
        } else {
          setError(null);
        }
      }
    } finally {
      if (!isBackground) setLoading(false);
    }
  };


  useEffect(() => {
    // Run health check first, then load data
    checkBackendHealth().then(online => setBackendOnline(online));
    loadDashboardData();
  }, []);


  // Live real-time polling
  useEffect(() => {
    if (!autoRefresh) return;
    const interval = setInterval(() => {
      loadDashboardData(true);
    }, 3000);
    return () => clearInterval(interval);
  }, [autoRefresh]);

  const measurementData = data?.measurement_distribution
    ? [
        {
          state: '|0⟩',
          Expected: data.measurement_distribution.p0_exp,
          Observed: data.measurement_distribution.p0_obs
        },
        {
          state: '|1⟩',
          Expected: data.measurement_distribution.p1_exp,
          Observed: data.measurement_distribution.p1_obs
        }
      ]
    : [
        { state: '|0⟩', Expected: 0.50, Observed: 0.50 },
        { state: '|1⟩', Expected: 0.50, Observed: 0.50 }
      ];

  const threatTrendData = data?.threat_trend || [
    { time: '-30m', legitimate: 0, attacks: 0 },
    { time: '-25m', legitimate: 0, attacks: 0 },
    { time: '-20m', legitimate: 0, attacks: 0 },
    { time: '-15m', legitimate: 0, attacks: 0 },
    { time: '-10m', legitimate: 0, attacks: 0 },
    { time: '-5m', legitimate: 0, attacks: 0 },
    { time: 'Now', legitimate: 0, attacks: 0 }
  ];

  return (
    <div className="space-y-6 pb-12">
      {/* Top Banner & Heading */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            Dashboard
          </h1>
          <p className="text-xs text-slate-400">Live overview of Quantum Digital Signature System</p>
        </div>
        <div className="flex items-center gap-3">
          {/* Live Sync Status Toggle */}
          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-mono border transition-all cursor-pointer ${
              autoRefresh
                ? 'bg-emerald-950/60 border-emerald-500/40 text-emerald-300 shadow-sm shadow-emerald-950'
                : 'bg-slate-900/60 border-slate-700 text-slate-400'
            }`}
            title="Toggle Live Auto-Syncing (every 3 seconds)"
          >
            <span className={`w-2 h-2 rounded-full ${autoRefresh ? 'bg-emerald-400 animate-pulse' : 'bg-slate-500'}`}></span>
            <span>{autoRefresh ? 'LIVE SYNC (3s)' : 'SYNC PAUSED'}</span>
          </button>

          <button
            onClick={() => loadDashboardData(false)}
            disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#0d162a] border border-blue-500/30 text-xs font-medium text-cyan-300 hover:bg-blue-900/30 transition-colors cursor-pointer"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>

          <span className="text-[11px] font-mono text-slate-400 hidden lg:inline">
            Updated: {lastUpdated}
          </span>
        </div>
      </div>

      {/* Backend status banner */}
      {backendOnline === false && (
        <div className="p-3 rounded-lg bg-amber-950/60 border border-amber-500/40 text-amber-200 text-xs flex flex-col gap-1">
          <p className="font-bold flex items-center gap-1.5">
            <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
            {isBackendConfigured
              ? 'Backend Unreachable — Simulator running in offline mode'
              : 'No Backend Configured — Running in offline/simulator mode'}
          </p>
          <p className="text-amber-300/80">
            {isBackendConfigured
              ? 'Cannot connect to the configured API server. Check that VITE_API_BASE_URL is correct and the backend is running.'
              : 'Set VITE_API_BASE_URL in Vercel project settings (e.g. https://your-backend.onrender.com/api) and redeploy. Locally, start the FastAPI backend with python run.py.'}
          </p>
        </div>
      )}

      {error && (
        <div className="p-3 rounded-lg bg-red-950/60 border border-red-500/40 text-red-300 text-xs">
          {error}
        </div>
      )}


      {/* Top 4 Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Total Signatures"
          value={data?.total_signatures ?? 0}
          subtitle="live signatures in DB"
          trend={data?.signatures_trend_pct ? `↑ ${data.signatures_trend_pct}% today` : 'Real-time'}
          icon={FileText}
          variant="blue"
        />
        <MetricCard
          title="Verified Signatures"
          value={data?.verified_count ?? 0}
          subtitle={`success rate ${data?.verified_success_rate ?? 100}%`}
          trend={`${data?.verified_success_rate ?? 100}% rate`}
          icon={ShieldCheck}
          variant="emerald"
        />
        <MetricCard
          title="Detected Attacks"
          value={data?.detected_attacks ?? 0}
          subtitle={`detection rate ${data?.detection_rate_pct ?? 100}%`}
          trend={`${data?.detection_rate_pct ?? 100}% rate`}
          icon={ShieldAlert}
          variant="red"
        />
        <MetricCard
          title="System Status"
          value={data?.system_status ?? 'Healthy'}
          subtitle={data?.system_resources?.simulator_status || 'Qiskit Aer Ready'}
          icon={Cpu}
          variant="purple"
        />
      </div>

      {/* Alice & Bob End-to-End Quantum Protocol Pipeline */}
      <AliceBobPipeline
        onNavigate={onNavigate}
        isAttacked={(data?.detected_attacks ?? 0) > 0}
        currentAttackName={(data?.detected_attacks ?? 0) > 0 ? 'Eve Interception Detected' : 'None (Clean Channel)'}
      />

      {/* A. System Workflow & B. Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* A. System Workflow */}
        <div className="lg:col-span-2 p-5 rounded-xl bg-[#0a1122]/90 border border-blue-500/20 shadow-lg">
          <div className="flex items-center gap-2 mb-4">
            <Activity className="w-4 h-4 text-cyan-400" />
            <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider font-sans">
              System Workflow
            </h2>
          </div>
          <div className="flex flex-wrap items-center justify-between gap-2 p-4 rounded-xl bg-[#060b17] border border-blue-900/30">
            {[
              { title: 'Message Input', icon: FileText, desc: 'SHA-256' },
              { title: 'Quantum Signature', icon: KeyRound, desc: 'State Prep' },
              { title: 'Transmission', icon: Activity, desc: 'Teleportation' },
              { title: 'Verification', icon: ShieldCheck, desc: 'Measurement' },
              { title: 'Threat Detection', icon: ShieldAlert, desc: 'Statistical' },
              { title: 'Result', icon: CheckCircle2, desc: 'Decision' }
            ].map((step, idx, arr) => (
              <React.Fragment key={step.title}>
                <div className="flex flex-col items-center text-center p-2 rounded-lg bg-[#0d162a]/60 border border-blue-500/20 min-w-[90px] shadow-sm">
                  <step.icon className="w-5 h-5 text-cyan-400 mb-1" />
                  <span className="text-[11px] font-semibold text-slate-200">{step.title}</span>
                  <span className="text-[9px] text-slate-500 font-mono">{step.desc}</span>
                </div>
                {idx < arr.length - 1 && (
                  <ArrowRight className="w-4 h-4 text-blue-500/60 hidden xl:block" />
                )}
              </React.Fragment>
            ))}
          </div>
        </div>

        {/* B. Quick Actions */}
        <div className="p-5 rounded-xl bg-[#0a1122]/90 border border-blue-500/20 shadow-lg flex flex-col justify-between">
          <div className="flex items-center gap-2 mb-3">
            <Zap className="w-4 h-4 text-purple-400" />
            <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider font-sans">
              Quick Actions
            </h2>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <button
              onClick={() => onNavigate('signature-generation')}
              className="p-3 rounded-lg bg-gradient-to-r from-blue-900/40 to-blue-800/20 hover:from-blue-800/60 hover:to-blue-700/40 border border-blue-500/30 text-left transition-all group"
            >
              <FileText className="w-4 h-4 text-cyan-400 mb-1.5 group-hover:scale-110 transition-transform" />
              <p className="text-xs font-semibold text-slate-200">Generate Signature</p>
            </button>
            <button
              onClick={() => onNavigate('verification')}
              className="p-3 rounded-lg bg-gradient-to-r from-emerald-900/40 to-emerald-800/20 hover:from-emerald-800/60 hover:to-emerald-700/40 border border-emerald-500/30 text-left transition-all group"
            >
              <ShieldCheck className="w-4 h-4 text-emerald-400 mb-1.5 group-hover:scale-110 transition-transform" />
              <p className="text-xs font-semibold text-slate-200">Verify Signature</p>
            </button>
            <button
              onClick={() => onNavigate('attack-simulation')}
              className="p-3 rounded-lg bg-gradient-to-r from-red-900/40 to-red-800/20 hover:from-red-800/60 hover:to-red-700/40 border border-red-500/30 text-left transition-all group"
            >
              <ShieldAlert className="w-4 h-4 text-red-400 mb-1.5 group-hover:scale-110 transition-transform" />
              <p className="text-xs font-semibold text-slate-200">Run Attack Sim</p>
            </button>
            <button
              onClick={() => onNavigate('quantum-circuit')}
              className="p-3 rounded-lg bg-gradient-to-r from-purple-900/40 to-purple-800/20 hover:from-purple-800/60 hover:to-purple-700/40 border border-purple-500/30 text-left transition-all group"
            >
              <Cpu className="w-4 h-4 text-purple-400 mb-1.5 group-hover:scale-110 transition-transform" />
              <p className="text-xs font-semibold text-slate-200">Quantum Circuit</p>
            </button>
          </div>
        </div>
      </div>

      {/* C. Latest Result, D. Measurement Distribution, E. Threat Trend */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* C. Latest Simulation Result */}
        <div className="p-5 rounded-xl bg-[#0a1122]/90 border border-blue-500/20 shadow-lg flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 mb-3">
              <ShieldCheck className="w-4 h-4 text-cyan-400" />
              <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider font-sans">
                Latest Simulation Result
              </h2>
            </div>
            <div className={`p-4 rounded-xl mb-4 border ${data?.latest_result?.is_threat ? 'bg-red-950/40 border-red-500/40 text-red-300' : 'bg-emerald-950/40 border-emerald-500/40 text-emerald-300'}`}>
              <div className="flex items-center gap-2 font-bold text-base">
                {data?.latest_result?.is_threat ? (
                  <AlertTriangle className="w-5 h-5 text-red-400" />
                ) : (
                  <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                )}
                <span>{data?.latest_result?.title || 'Signature Verified'}</span>
              </div>
              <p className="text-xs text-slate-300 mt-1">
                {data?.latest_result?.status || 'The message is authentic and untampered.'}
              </p>
            </div>

            <div className="space-y-2 text-xs font-mono">
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400 font-sans">Message ID</span>
                <span className="text-slate-200 font-semibold">{data?.latest_result?.message_id || 'MSG-2025-0510-001'}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400 font-sans">Verification Fidelity</span>
                <span className="text-cyan-300 font-bold">{data?.latest_result?.verification_fidelity ?? 0.98}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400 font-sans">Measurement Deviation</span>
                <span className="text-purple-300 font-bold">{data?.latest_result?.measurement_deviation ?? 0.02}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400 font-sans">Threat Score</span>
                <span className={`font-bold ${data?.latest_result?.is_threat ? 'text-red-400' : 'text-emerald-400'}`}>
                  {data?.latest_result?.threat_score || '0.00 (Low)'}
                </span>
              </div>
              <div className="flex justify-between py-1">
                <span className="text-slate-400 font-sans">Final Decision</span>
                <span className={`font-bold ${data?.latest_result?.is_threat ? 'text-red-400' : 'text-emerald-400'}`}>
                  {data?.latest_result?.final_decision || 'LEGITIMATE'}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* D. Measurement Distribution Chart */}
        <div className="p-5 rounded-xl bg-[#0a1122]/90 border border-blue-500/20 shadow-lg">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider font-sans flex items-center gap-2">
              <Activity className="w-4 h-4 text-cyan-400" />
              Measurement Distribution
            </h2>
            <div className="flex items-center gap-3 text-[11px]">
              <span className="flex items-center gap-1 text-cyan-400">
                <span className="w-2.5 h-2.5 rounded-sm bg-cyan-500"></span> Expected
              </span>
              <span className="flex items-center gap-1 text-purple-400">
                <span className="w-2.5 h-2.5 rounded-sm bg-purple-500"></span> Observed
              </span>
            </div>
          </div>
          <div className="h-52 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={measurementData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="state" stroke="#64748b" fontSize={11} fontFamily="monospace" />
                <YAxis stroke="#64748b" fontSize={11} domain={[0, 1]} />
                <RechartsTooltip contentStyle={{ backgroundColor: '#0c1427', borderColor: '#0284c7', fontSize: 12 }} />
                <Bar dataKey="Expected" fill="#06b6d4" radius={[4, 4, 0, 0]} />
                <Bar dataKey="Observed" fill="#a855f7" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <p className="text-[11px] text-center text-slate-400 font-mono mt-1">Measurement Outcome</p>
        </div>

        {/* E. Threat Detection Trend Chart */}
        <div className="p-5 rounded-xl bg-[#0a1122]/90 border border-blue-500/20 shadow-lg">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider font-sans flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 text-red-400" />
              Threat Detection Trend
            </h2>
            <div className="flex items-center gap-3 text-[11px]">
              <span className="flex items-center gap-1 text-emerald-400">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span> Legitimate
              </span>
              <span className="flex items-center gap-1 text-red-400">
                <span className="w-2.5 h-2.5 rounded-full bg-red-500"></span> Attacks
              </span>
            </div>
          </div>
          <div className="h-52 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={threatTrendData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="time" stroke="#64748b" fontSize={11} fontFamily="monospace" />
                <YAxis stroke="#64748b" fontSize={11} />
                <RechartsTooltip contentStyle={{ backgroundColor: '#0c1427', borderColor: '#ef4444', fontSize: 12 }} />
                <Line type="monotone" dataKey="legitimate" stroke="#10b981" strokeWidth={2} dot={{ fill: '#10b981', r: 3 }} />
                <Line type="monotone" dataKey="attacks" stroke="#ef4444" strokeWidth={2} dot={{ fill: '#ef4444', r: 3 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <p className="text-[11px] text-center text-slate-400 font-mono mt-1">Time (minutes ago)</p>
        </div>
      </div>

      {/* F. Recent Activity Logs & G. System Resources */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* F. Recent Activity Logs */}
        <div className="lg:col-span-2 p-5 rounded-xl bg-[#0a1122]/90 border border-blue-500/20 shadow-lg">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider font-sans flex items-center gap-2">
              <FileText className="w-4 h-4 text-cyan-400" />
              Recent Activity Logs
            </h2>
            <button
              onClick={() => onNavigate('logs')}
              className="text-xs text-cyan-400 hover:text-cyan-300 font-medium"
            >
              View All →
            </button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 font-sans">
                  <th className="pb-2">Time</th>
                  <th className="pb-2">Event</th>
                  <th className="pb-2">Details</th>
                  <th className="pb-2">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {data?.recent_logs && data.recent_logs.length > 0 ? (
                  data.recent_logs.map((log) => {
                    const isThreat = log.status.toLowerCase().includes('attack') || log.status.toLowerCase().includes('blocked');
                    const isSuccess = log.status.toLowerCase().includes('success') || log.status.toLowerCase().includes('legitimate');
                    return (
                      <tr key={log.id} className="hover:bg-slate-800/30 transition-colors">
                        <td className="py-2.5 text-slate-400">{log.time}</td>
                        <td className="py-2.5 font-semibold text-slate-200">{log.event}</td>
                        <td className="py-2.5 text-slate-300 font-sans text-xs truncate max-w-xs">{log.details}</td>
                        <td className="py-2.5">
                          <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold ${isThreat ? 'bg-red-950/60 text-red-400 border border-red-500/30' : isSuccess ? 'bg-emerald-950/60 text-emerald-400 border border-emerald-500/30' : 'bg-blue-950/60 text-cyan-400 border border-blue-500/30'}`}>
                            <span className={`w-1.5 h-1.5 rounded-full ${isThreat ? 'bg-red-400' : isSuccess ? 'bg-emerald-400' : 'bg-cyan-400'}`}></span>
                            {log.status}
                          </span>
                        </td>
                      </tr>
                    );
                  })
                ) : (
                  <tr>
                    <td colSpan={4} className="py-4 text-center text-slate-500">No recent logs recorded.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* G. System Resources */}
        <div className="p-5 rounded-xl bg-[#0a1122]/90 border border-blue-500/20 shadow-lg flex flex-col justify-between">
          <div className="flex items-center gap-2 mb-4">
            <Cpu className="w-4 h-4 text-cyan-400" />
            <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider font-sans">
              System Resources
            </h2>
          </div>
          <div className="grid grid-cols-3 gap-3 text-center my-auto">
            {/* CPU Usage */}
            <div className="flex flex-col items-center">
              <div className="relative w-20 h-20 flex items-center justify-center rounded-full border-4 border-cyan-500/30 bg-[#070c18]">
                <span className="text-sm font-bold font-mono text-cyan-300">
                  {data?.system_resources?.cpu_usage_percent ?? 32}%
                </span>
              </div>
              <span className="text-[11px] text-slate-400 font-sans mt-2">CPU Usage</span>
            </div>

            {/* Memory Usage */}
            <div className="flex flex-col items-center">
              <div className="relative w-20 h-20 flex items-center justify-center rounded-full border-4 border-purple-500/30 bg-[#070c18]">
                <span className="text-sm font-bold font-mono text-purple-300">
                  {data?.system_resources?.memory_usage_percent ?? 54}%
                </span>
              </div>
              <span className="text-[11px] text-slate-400 font-sans mt-2">Memory Usage</span>
            </div>

            {/* Simulation Load */}
            <div className="flex flex-col items-center">
              <div className="relative w-20 h-20 flex items-center justify-center rounded-full border-4 border-emerald-500/30 bg-[#070c18]">
                <span className="text-sm font-bold font-mono text-emerald-300">
                  {data?.system_resources?.simulation_load_percent ?? 18}%
                </span>
              </div>
              <span className="text-[11px] text-slate-400 font-sans mt-2">Sim Load</span>
            </div>
          </div>
          <p className="text-[10px] text-slate-500 text-center font-mono mt-4">
            Backend: {data?.system_resources?.simulator_status || 'Qiskit Aer Simulator (Local)'}
          </p>
        </div>
      </div>
    </div>
  );
};
