import React, { useEffect, useState } from 'react';
import {
  ShieldCheck,
  ShieldAlert,
  Clock,
  Activity,
  Cpu,
  RefreshCw,
  CheckCircle2
} from 'lucide-react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  CartesianGrid
} from 'recharts';
import { MetricCard } from '../components/common/MetricCard';
import { api } from '../services/api';
import type { AnalyticsSummaryResponse, AnalyticsTrendsResponse } from '../types';

export const AnalyticsPage: React.FC = () => {
  const [summary, setSummary] = useState<AnalyticsSummaryResponse | null>(null);
  const [trends, setTrends] = useState<AnalyticsTrendsResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<string>('Just now');
  const [error, setError] = useState<string | null>(null);

  const loadAnalytics = async (isBackground = false) => {
    try {
      if (!isBackground) setLoading(true);
      const [sumRes, trRes] = await Promise.all([
        api.getAnalyticsSummary(),
        api.getAnalyticsTrends()
      ]);
      setSummary(sumRes);
      setTrends(trRes);
      setLastUpdated(new Date().toLocaleTimeString());
      setError(null);
    } catch (err: any) {
      if (!isBackground) setError(err.message || 'Failed to fetch analytics data.');
    } finally {
      if (!isBackground) setLoading(false);
    }
  };

  useEffect(() => {
    loadAnalytics();
  }, []);

  // Live real-time polling
  useEffect(() => {
    if (!autoRefresh) return;
    const interval = setInterval(() => {
      loadAnalytics(true);
    }, 3500);
    return () => clearInterval(interval);
  }, [autoRefresh]);

  const attackDistData = trends?.attack_type_distribution
    ? Object.entries(trends.attack_type_distribution).map(([type, count]) => ({
        type: type.replace(' Attack', ''),
        count
      }))
    : [];

  const fidelityData = trends?.fidelity_distribution || [
    {"range": "0.95 - 1.00", "count": 0, "color": "#10b981"},
    {"range": "0.85 - 0.94", "count": 0, "color": "#f59e0b"},
    {"range": "0.70 - 0.84", "count": 0, "color": "#f97316"},
    {"range": "< 0.70", "count": 0, "color": "#ef4444"}
  ];

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            Analytics &amp; Security Intelligence
          </h1>
          <p className="text-xs text-slate-400">
            Live system performance, quantum fidelity metrics, and threat detection analytics
          </p>
        </div>
        <div className="flex items-center gap-3">
          {/* Live Sync Badge */}
          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-mono border transition-all cursor-pointer ${
              autoRefresh
                ? 'bg-emerald-950/60 border-emerald-500/40 text-emerald-300 shadow-sm shadow-emerald-950'
                : 'bg-slate-900/60 border-slate-700 text-slate-400'
            }`}
            title="Toggle Live Auto-Syncing (every 3.5s)"
          >
            <span className={`w-2 h-2 rounded-full ${autoRefresh ? 'bg-emerald-400 animate-pulse' : 'bg-slate-500'}`}></span>
            <span>{autoRefresh ? 'LIVE INTELLIGENCE (3.5s)' : 'SYNC PAUSED'}</span>
          </button>

          <button
            onClick={() => loadAnalytics(false)}
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

      {error && (
        <div className="p-3 rounded-lg bg-red-950/60 border border-red-500/40 text-red-300 text-xs">
          {error}
        </div>
      )}

      {/* Top 4 Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Total Simulations"
          value={summary?.total_simulations ?? 0}
          subtitle="Quantum circuit executions"
          icon={Activity}
          variant="blue"
        />
        <MetricCard
          title="Verification Accuracy"
          value={`${summary?.verification_accuracy ?? 100}%`}
          subtitle="Statistical consistency"
          icon={ShieldCheck}
          variant="emerald"
        />
        <MetricCard
          title="Attacks Detected"
          value={summary?.attacks_detected ?? 0}
          subtitle={`detection rate ${summary?.detection_rate ?? 100}%`}
          icon={ShieldAlert}
          variant="red"
        />
        <MetricCard
          title="Avg Verification Time"
          value={`${summary?.avg_verification_time_ms ?? 1.25} ms`}
          subtitle="Aer simulator latency"
          icon={Clock}
          variant="purple"
        />
      </div>

      {/* Calculated Quantum & Security Metrics Strip */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        {[
          { label: 'Detection Rate', val: `${summary?.detection_rate ?? 100}%`, color: 'text-emerald-400' },
          { label: 'False Positive Rate', val: `${summary?.false_positive_rate ?? 0.0}%`, color: 'text-cyan-400' },
          { label: 'False Negative Rate', val: `${summary?.false_negative_rate ?? 0.0}%`, color: 'text-cyan-400' },
          { label: 'Precision', val: `${summary?.precision ?? 100}%`, color: 'text-purple-300' },
          { label: 'Average Fidelity', val: `${summary?.avg_fidelity ?? 1.000}`, color: 'text-emerald-400' },
          { label: 'Active Qubits', val: '1 - 3 Qubits', color: 'text-slate-200' }
        ].map((m) => (
          <div key={m.label} className="p-3 rounded-xl bg-[#0a1122]/90 border border-blue-500/20 text-center font-mono">
            <span className="text-[10px] text-slate-400 font-sans block truncate">{m.label}</span>
            <span className={`text-base font-bold ${m.color}`}>{m.val}</span>
          </div>
        ))}
      </div>

      {/* Row 1: Activity Trend & Attack Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Simulation Activity Over Time */}
        <div className="p-5 rounded-xl bg-[#0a1122]/90 border border-blue-500/20 shadow-lg space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider font-sans flex items-center gap-2">
              <Activity className="w-4 h-4 text-cyan-400" />
              Simulation Activity Over Time
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

          <div className="h-56 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={trends?.activity_trend || []} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="time_label" stroke="#64748b" fontSize={11} fontFamily="monospace" />
                <YAxis stroke="#64748b" fontSize={11} />
                <RechartsTooltip contentStyle={{ backgroundColor: '#0c1427', borderColor: '#0284c7', fontSize: 12 }} />
                <Line type="monotone" dataKey="legitimate_count" stroke="#10b981" strokeWidth={2} dot={{ r: 3 }} />
                <Line type="monotone" dataKey="attack_count" stroke="#ef4444" strokeWidth={2} dot={{ r: 3 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Attack Type Distribution */}
        <div className="p-5 rounded-xl bg-[#0a1122]/90 border border-blue-500/20 shadow-lg space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider font-sans flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 text-red-400" />
              Attack Type Distribution
            </h2>
            <span className="text-xs text-slate-400 font-mono">5 Threat Vectors</span>
          </div>

          <div className="h-56 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={attackDistData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="type" stroke="#64748b" fontSize={11} fontFamily="monospace" />
                <YAxis stroke="#64748b" fontSize={11} />
                <RechartsTooltip contentStyle={{ backgroundColor: '#0c1427', borderColor: '#ef4444', fontSize: 12 }} />
                <Bar dataKey="count" fill="#ef4444" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Row 2: Fidelity Distribution & System Load History */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Verification Fidelity Distribution */}
        <div className="p-5 rounded-xl bg-[#0a1122]/90 border border-blue-500/20 shadow-lg space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider font-sans flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              Quantum State Fidelity Breakdown
            </h2>
          </div>

          <div className="h-52 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={fidelityData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="range" stroke="#64748b" fontSize={10} fontFamily="monospace" />
                <YAxis stroke="#64748b" fontSize={11} />
                <RechartsTooltip contentStyle={{ backgroundColor: '#0c1427', borderColor: '#10b981', fontSize: 12 }} />
                <Bar dataKey="count" fill="#10b981" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* System Load History */}
        <div className="p-5 rounded-xl bg-[#0a1122]/90 border border-blue-500/20 shadow-lg space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider font-sans flex items-center gap-2">
              <Cpu className="w-4 h-4 text-purple-400" />
              Simulator Performance &amp; Resource Load
            </h2>
            <div className="flex items-center gap-3 text-[11px]">
              <span className="flex items-center gap-1 text-cyan-400">
                <span className="w-2.5 h-2.5 rounded-full bg-cyan-500"></span> CPU
              </span>
              <span className="flex items-center gap-1 text-purple-400">
                <span className="w-2.5 h-2.5 rounded-full bg-purple-500"></span> Memory
              </span>
            </div>
          </div>

          <div className="h-52 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={trends?.system_load_history || []} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="time" stroke="#64748b" fontSize={11} fontFamily="monospace" />
                <YAxis stroke="#64748b" fontSize={11} />
                <RechartsTooltip contentStyle={{ backgroundColor: '#0c1427', borderColor: '#a855f7', fontSize: 12 }} />
                <Line type="monotone" dataKey="cpu" stroke="#06b6d4" strokeWidth={2} dot={{ r: 3 }} />
                <Line type="monotone" dataKey="memory" stroke="#a855f7" strokeWidth={2} dot={{ r: 3 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};
