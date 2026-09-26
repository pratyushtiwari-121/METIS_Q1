import React, { useState, useEffect } from 'react';
import {
  FileText,
  Filter,
  Download,
  Search,
  RefreshCw,
  Eye,
  ShieldCheck,
  ShieldAlert,
  AlertTriangle,
  X
} from 'lucide-react';
import { api } from '../services/api';
import type { LogListResponse, LogItemResponse } from '../types';

export const LogsPage: React.FC = () => {
  const [data, setData] = useState<LogListResponse | null>(null);
  const [category, setCategory] = useState<string>('All');
  const [status, setStatus] = useState<string>('All');
  const [search, setSearch] = useState<string>('');
  const [page, setPage] = useState<number>(1);
  const [selectedLog, setSelectedLog] = useState<LogItemResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [liveStream, setLiveStream] = useState<boolean>(true);
  const [lastUpdated, setLastUpdated] = useState<string>('Just now');
  const [error, setError] = useState<string | null>(null);

  const fetchLogs = async (isBackground = false) => {
    try {
      if (!isBackground) setLoading(true);
      const res = await api.getLogs({
        category: category !== 'All' ? category : undefined,
        status: status !== 'All' ? status : undefined,
        search: search.trim() || undefined,
        page,
        pageSize: 20
      });
      setData(res);
      setLastUpdated(new Date().toLocaleTimeString());
      setError(null);
    } catch (err: any) {
      if (!isBackground) setError(err.message || 'Failed to fetch logs.');
    } finally {
      if (!isBackground) setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [category, status, page]);

  // Live real-time stream polling
  useEffect(() => {
    if (!liveStream) return;
    const interval = setInterval(() => {
      fetchLogs(true);
    }, 3000);
    return () => clearInterval(interval);
  }, [liveStream, category, status, page, search]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchLogs();
  };

  const handleExportCSV = () => {
    window.open(api.getExportLogsUrl(), '_blank');
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            System &amp; Quantum Audit Logs
          </h1>
          <p className="text-xs text-slate-400">
            Real-time security auditing, signature traces, and quantum threat detection logs
          </p>
        </div>
        <div className="flex items-center gap-3">
          {/* Live Stream Toggle */}
          <button
            onClick={() => setLiveStream(!liveStream)}
            className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-mono border transition-all cursor-pointer ${
              liveStream
                ? 'bg-emerald-950/60 border-emerald-500/40 text-emerald-300 shadow-sm shadow-emerald-950'
                : 'bg-slate-900/60 border-slate-700 text-slate-400'
            }`}
            title="Toggle Live Log Streaming"
          >
            <span className={`w-2 h-2 rounded-full ${liveStream ? 'bg-emerald-400 animate-pulse' : 'bg-slate-500'}`}></span>
            <span>{liveStream ? 'LIVE STREAM (3s)' : 'STREAM PAUSED'}</span>
          </button>

          <button
            onClick={() => fetchLogs(false)}
            disabled={loading}
            className="px-3 py-1.5 rounded-lg bg-[#0d162a] border border-blue-500/30 text-xs text-cyan-300 flex items-center gap-1.5 hover:bg-blue-900/30 transition-colors cursor-pointer"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>

          <button
            onClick={handleExportCSV}
            className="px-3 py-1.5 rounded-lg bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500 text-white text-xs font-semibold flex items-center gap-1.5 transition-all shadow-md shadow-purple-900/30 cursor-pointer"
          >
            <Download className="w-3.5 h-3.5" />
            Export CSV
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

      {/* Log Summary Statistics Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        {[
          { label: 'Total Logs', val: data?.summary?.total_logs ?? 0, color: 'text-cyan-300' },
          { label: 'Successful Events', val: data?.summary?.successful_events ?? 0, color: 'text-emerald-400' },
          { label: 'Detected Attacks', val: data?.summary?.detected_attacks ?? 0, color: 'text-red-400' },
          { label: 'Blocked Attempts', val: data?.summary?.blocked_attempts ?? 0, color: 'text-amber-400' },
          { label: 'System Events', val: data?.summary?.system_events ?? 0, color: 'text-purple-300' },
          { label: 'Unauthorized Access', val: data?.summary?.unauthorized_access ?? 0, color: 'text-rose-400' }
        ].map((s) => (
          <div key={s.label} className="p-3 rounded-xl bg-[#0a1122]/90 border border-blue-500/20 text-center font-mono">
            <span className="text-[10px] text-slate-400 font-sans block truncate">{s.label}</span>
            <span className={`text-xl font-bold ${s.color}`}>{s.val}</span>
          </div>
        ))}
      </div>

      {/* Filter & Search Bar */}
      <div className="p-4 rounded-xl bg-[#0a1122]/90 border border-blue-500/20 shadow-lg flex flex-col md:flex-row items-center justify-between gap-4">
        <form onSubmit={handleSearchSubmit} className="flex items-center gap-2 w-full md:w-auto flex-1 max-w-md">
          <div className="relative w-full">
            <Search className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search logs by keyword, signature ID, or details..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-3 py-2 rounded-lg bg-[#070b16] border border-blue-900/40 text-xs text-slate-200 focus:outline-none focus:border-cyan-400"
            />
          </div>
          <button
            type="submit"
            className="px-3 py-2 rounded-lg bg-blue-900/40 hover:bg-blue-800/60 border border-blue-500/30 text-xs text-cyan-300 font-semibold shrink-0"
          >
            Search
          </button>
        </form>

        <div className="flex items-center gap-3 w-full md:w-auto">
          {/* Category Filter */}
          <div className="flex items-center gap-1.5 text-xs">
            <Filter className="w-3.5 h-3.5 text-slate-400" />
            <select
              value={category}
              onChange={(e) => {
                setCategory(e.target.value);
                setPage(1);
              }}
              className="p-1.5 rounded bg-[#070b16] border border-slate-800 text-xs text-slate-300 focus:outline-none focus:border-cyan-400"
            >
              <option value="All">All Categories</option>
              <option value="Signature">Signature</option>
              <option value="Verification">Verification</option>
              <option value="Attack">Attack</option>
              <option value="Quantum">Quantum</option>
              <option value="Security">Security</option>
            </select>
          </div>

          {/* Status Filter */}
          <select
            value={status}
            onChange={(e) => {
              setStatus(e.target.value);
              setPage(1);
            }}
            className="p-1.5 rounded bg-[#070b16] border border-slate-800 text-xs text-slate-300 focus:outline-none focus:border-cyan-400"
          >
            <option value="All">All Statuses</option>
            <option value="Success">Success / Legitimate</option>
            <option value="Detected">Detected</option>
            <option value="Blocked">Blocked</option>
            <option value="Warning">Warning</option>
          </select>
        </div>
      </div>

      {/* Main Logs Table */}
      <div className="p-5 rounded-xl bg-[#0a1122]/90 border border-blue-500/20 shadow-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-sans">
                <th className="pb-3 w-12">#</th>
                <th className="pb-3">Timestamp</th>
                <th className="pb-3">Event Type</th>
                <th className="pb-3">Category</th>
                <th className="pb-3">Details</th>
                <th className="pb-3">Status</th>
                <th className="pb-3">Source</th>
                <th className="pb-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {data?.logs && data.logs.length > 0 ? (
                data.logs.map((log) => {
                  const isThreat =
                    log.status.toLowerCase().includes('detected') ||
                    log.status.toLowerCase().includes('attack');
                  const isBlocked = log.status.toLowerCase().includes('blocked');
                  const isSuccess =
                    log.status.toLowerCase().includes('success') ||
                    log.status.toLowerCase().includes('legitimate');

                  return (
                    <tr key={log.id} className="hover:bg-slate-800/30 transition-colors">
                      <td className="py-3 text-slate-500">{log.id}</td>
                      <td className="py-3 text-slate-400">{log.timestamp}</td>
                      <td className="py-3 font-semibold text-slate-200">{log.event_type}</td>
                      <td className="py-3 text-purple-300 font-sans">{log.category}</td>
                      <td className="py-3 text-slate-300 font-sans max-w-sm truncate">{log.details}</td>
                      <td className="py-3">
                        <span
                          className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold ${
                            isThreat
                              ? 'bg-red-950/70 text-red-400 border border-red-500/40'
                              : isBlocked
                              ? 'bg-amber-950/70 text-amber-400 border border-amber-500/40'
                              : isSuccess
                              ? 'bg-emerald-950/70 text-emerald-400 border border-emerald-500/40'
                              : 'bg-blue-950/70 text-cyan-400 border border-blue-500/40'
                          }`}
                        >
                          <span
                            className={`w-1.5 h-1.5 rounded-full ${
                              isThreat
                                ? 'bg-red-400'
                                : isBlocked
                                ? 'bg-amber-400'
                                : isSuccess
                                ? 'bg-emerald-400'
                                : 'bg-cyan-400'
                            }`}
                          ></span>
                          {log.status}
                        </span>
                      </td>
                      <td className="py-3 text-slate-400 font-sans">{log.source}</td>
                      <td className="py-3 text-right">
                        <button
                          onClick={() => setSelectedLog(log)}
                          className="p-1.5 rounded bg-blue-900/30 hover:bg-blue-800/50 text-cyan-300 transition-colors"
                          title="View Details"
                        >
                          <Eye className="w-3.5 h-3.5" />
                        </button>
                      </td>
                    </tr>
                  );
                })
              ) : (
                <tr>
                  <td colSpan={8} className="py-8 text-center text-slate-500">
                    No logs found matching criteria.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Bar */}
        {data && data.total_count > data.page_size && (
          <div className="flex items-center justify-between pt-4 border-t border-slate-800 text-xs">
            <span className="text-slate-400">
              Showing page {data.page} of {Math.ceil(data.total_count / data.page_size)}
            </span>
            <div className="flex items-center gap-2">
              <button
                disabled={page <= 1}
                onClick={() => setPage(page - 1)}
                className="px-3 py-1 rounded bg-slate-800 text-slate-300 disabled:opacity-40"
              >
                Previous
              </button>
              <button
                disabled={page >= Math.ceil(data.total_count / data.page_size)}
                onClick={() => setPage(page + 1)}
                className="px-3 py-1 rounded bg-slate-800 text-slate-300 disabled:opacity-40"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Log Detail Modal */}
      {selectedLog && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="w-full max-w-lg p-6 rounded-2xl bg-[#0a1122] border border-cyan-500/40 shadow-2xl shadow-cyan-950/80 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="font-bold text-slate-100 flex items-center gap-2">
                <FileText className="w-4 h-4 text-cyan-400" />
                Log Event #{selectedLog.id}
              </h3>
              <button
                onClick={() => setSelectedLog(null)}
                className="text-slate-400 hover:text-white transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-2 text-xs font-mono">
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400 font-sans">Timestamp</span>
                <span className="text-slate-200">{selectedLog.timestamp}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400 font-sans">Event Type</span>
                <span className="text-cyan-300 font-bold">{selectedLog.event_type}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400 font-sans">Category</span>
                <span className="text-purple-300">{selectedLog.category}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400 font-sans">Status</span>
                <span className="text-emerald-400 font-bold">{selectedLog.status}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400 font-sans">Source</span>
                <span className="text-slate-200">{selectedLog.source}</span>
              </div>
              {selectedLog.signature_id && (
                <div className="flex justify-between py-1 border-b border-slate-800">
                  <span className="text-slate-400 font-sans">Signature ID</span>
                  <span className="text-cyan-300">{selectedLog.signature_id}</span>
                </div>
              )}
            </div>

            <div>
              <span className="text-[11px] text-slate-400 block mb-1">Details &amp; Audit Trace</span>
              <div className="p-3 rounded-lg bg-[#070b16] border border-blue-900/40 text-xs text-slate-200 font-sans leading-relaxed">
                {selectedLog.details}
              </div>
            </div>

            <div className="pt-2">
              <button
                onClick={() => setSelectedLog(null)}
                className="w-full py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
