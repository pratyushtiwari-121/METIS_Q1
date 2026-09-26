import React, { useState, useEffect } from 'react';
import {
  Settings,
  Cpu,
  Shield,
  FileText,
  Bell,
  Sliders,
  Save,
  RotateCcw,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';
import { api } from '../services/api';
import type { SystemSettings } from '../types';

export const SettingsPage: React.FC = () => {
  const [settings, setSettings] = useState<SystemSettings>({
    app_name: 'Quantum Digital Signature Security',
    theme: 'dark-quantum',
    language: 'en',
    timezone: 'Asia/Kolkata',
    default_shots: 1024,
    default_qubits: 2,
    simulator_backend: 'Qiskit Aer Simulator (Local)',
    measurement_basis: 'Computational (Z-basis)',
    verification_threshold: 0.1,
    fidelity_threshold: 0.85,
    max_verification_attempts: 5,
    replay_protection: true,
    attack_detection_sensitivity: 'High',
    enable_logging: true,
    log_retention_days: 30,
    security_alerts: true,
    alert_on_attack: true,
    alert_on_verification_failure: true,
    noise_model_enabled: false,
    debug_mode: false,
    simulation_seed: 42
  });

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchSettings = async () => {
    try {
      setLoading(true);
      const res = await api.getSettings();
      setSettings(res);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to load system settings.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSettings();
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setSaving(true);
      setError(null);
      const updated = await api.updateSettings(settings);
      setSettings(updated);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (err: any) {
      setError(err.message || 'Failed to persist settings.');
    } finally {
      setSaving(false);
    }
  };

  const handleReset = async () => {
    if (!window.confirm('Reset all settings to system defaults?')) return;
    try {
      setSaving(true);
      const res = await api.resetSettings();
      setSettings(res);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (err: any) {
      setError(err.message || 'Failed to reset settings.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            System Settings &amp; Configuration
          </h1>
          <p className="text-xs text-slate-400">
            Configure quantum simulator thresholds, security policies, and application preferences
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={handleReset}
            disabled={saving}
            className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs text-slate-300 flex items-center gap-1.5 transition-colors"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            Reset Defaults
          </button>
          <button
            type="button"
            onClick={handleSave}
            disabled={saving}
            className="px-4 py-1.5 rounded-lg bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-semibold text-xs flex items-center gap-1.5 transition-all shadow-md shadow-cyan-900/30"
          >
            <Save className="w-3.5 h-3.5" />
            {saving ? 'Saving...' : 'Save Settings'}
          </button>
        </div>
      </div>

      {saveSuccess && (
        <div className="p-3 rounded-lg bg-emerald-950/60 border border-emerald-500/40 text-emerald-300 text-xs flex items-center gap-2 animate-fadeIn">
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          Settings saved and persisted successfully in SQLite database!
        </div>
      )}

      {error && (
        <div className="p-3 rounded-lg bg-red-950/60 border border-red-500/40 text-red-300 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-red-400" />
          {error}
        </div>
      )}

      <form onSubmit={handleSave} className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 1. GENERAL SETTINGS */}
        <div className="p-5 rounded-xl bg-[#0a1122]/90 border border-blue-500/20 shadow-lg space-y-4">
          <div className="flex items-center gap-2 border-b border-slate-800 pb-3">
            <Settings className="w-4 h-4 text-cyan-400" />
            <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider font-sans">
              General Configuration
            </h2>
          </div>

          <div className="space-y-3 text-xs">
            <div>
              <label className="text-[11px] text-slate-400 block mb-1">Application Name</label>
              <input
                type="text"
                value={settings.app_name}
                onChange={(e) => setSettings({ ...settings, app_name: e.target.value })}
                className="w-full p-2.5 rounded bg-[#070b16] border border-blue-900/40 text-slate-200 font-sans focus:outline-none focus:border-cyan-400"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-[11px] text-slate-400 block mb-1">Theme</label>
                <select
                  value={settings.theme}
                  onChange={(e) => setSettings({ ...settings, theme: e.target.value })}
                  className="w-full p-2 rounded bg-[#070b16] border border-slate-800 text-slate-300 focus:outline-none focus:border-cyan-400"
                >
                  <option value="dark-quantum">Dark Quantum (Default)</option>
                  <option value="cyber-neon">Cyber Neon</option>
                  <option value="deep-space">Deep Space</option>
                </select>
              </div>

              <div>
                <label className="text-[11px] text-slate-400 block mb-1">Timezone</label>
                <input
                  type="text"
                  value={settings.timezone}
                  onChange={(e) => setSettings({ ...settings, timezone: e.target.value })}
                  className="w-full p-2 rounded bg-[#070b16] border border-slate-800 text-slate-200 font-mono text-[11px] focus:outline-none focus:border-cyan-400"
                />
              </div>
            </div>
          </div>
        </div>

        {/* 2. QUANTUM SIMULATOR SETTINGS */}
        <div className="p-5 rounded-xl bg-[#0a1122]/90 border border-blue-500/20 shadow-lg space-y-4">
          <div className="flex items-center gap-2 border-b border-slate-800 pb-3">
            <Cpu className="w-4 h-4 text-purple-400" />
            <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider font-sans">
              Quantum Simulator Parameters
            </h2>
          </div>

          <div className="space-y-3 text-xs">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-[11px] text-slate-400 block mb-1">Default Shots</label>
                <select
                  value={settings.default_shots}
                  onChange={(e) => setSettings({ ...settings, default_shots: parseInt(e.target.value) })}
                  className="w-full p-2 rounded bg-[#070b16] border border-slate-800 text-slate-300 font-mono focus:outline-none focus:border-cyan-400"
                >
                  <option value={512}>512 shots</option>
                  <option value={1024}>1024 shots (Standard)</option>
                  <option value={2048}>2048 shots</option>
                  <option value={4096}>4096 shots</option>
                </select>
              </div>

              <div>
                <label className="text-[11px] text-slate-400 block mb-1">Default Qubits</label>
                <input
                  type="number"
                  min="1"
                  max="5"
                  value={settings.default_qubits}
                  onChange={(e) => setSettings({ ...settings, default_qubits: parseInt(e.target.value) })}
                  className="w-full p-2 rounded bg-[#070b16] border border-slate-800 text-slate-200 font-mono focus:outline-none focus:border-cyan-400"
                />
              </div>
            </div>

            <div>
              <label className="text-[11px] text-slate-400 block mb-1">Simulator Backend</label>
              <input
                type="text"
                disabled
                value={settings.simulator_backend}
                className="w-full p-2 rounded bg-[#070b16]/60 border border-slate-800 text-slate-400 font-mono text-[11px]"
              />
            </div>
          </div>
        </div>

        {/* 3. SECURITY & THRESHOLDS */}
        <div className="p-5 rounded-xl bg-[#0a1122]/90 border border-blue-500/20 shadow-lg space-y-4">
          <div className="flex items-center gap-2 border-b border-slate-800 pb-3">
            <Shield className="w-4 h-4 text-emerald-400" />
            <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider font-sans">
              Security &amp; Detection Policies
            </h2>
          </div>

          <div className="space-y-3 text-xs">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-[11px] text-slate-400 block mb-1">Verification Threshold (TVD)</label>
                <input
                  type="number"
                  step="0.01"
                  min="0.01"
                  max="0.5"
                  value={settings.verification_threshold}
                  onChange={(e) => setSettings({ ...settings, verification_threshold: parseFloat(e.target.value) })}
                  className="w-full p-2 rounded bg-[#070b16] border border-slate-800 text-cyan-300 font-mono focus:outline-none focus:border-cyan-400"
                />
              </div>

              <div>
                <label className="text-[11px] text-slate-400 block mb-1">Min State Fidelity (F)</label>
                <input
                  type="number"
                  step="0.01"
                  min="0.5"
                  max="0.99"
                  value={settings.fidelity_threshold}
                  onChange={(e) => setSettings({ ...settings, fidelity_threshold: parseFloat(e.target.value) })}
                  className="w-full p-2 rounded bg-[#070b16] border border-slate-800 text-emerald-400 font-mono focus:outline-none focus:border-cyan-400"
                />
              </div>
            </div>

            <div className="flex items-center justify-between p-2 rounded bg-[#070b16]">
              <span className="text-slate-300">Replay Protection (Nonce Guard)</span>
              <input
                type="checkbox"
                checked={settings.replay_protection}
                onChange={(e) => setSettings({ ...settings, replay_protection: e.target.checked })}
                className="w-4 h-4 rounded text-cyan-500 focus:ring-0"
              />
            </div>

            <div className="flex items-center justify-between p-2 rounded bg-[#070b16]">
              <span className="text-slate-300">Detection Sensitivity</span>
              <select
                value={settings.attack_detection_sensitivity}
                onChange={(e) => setSettings({ ...settings, attack_detection_sensitivity: e.target.value })}
                className="p-1 rounded bg-slate-800 text-xs text-slate-200"
              >
                <option value="High">High (Strict)</option>
                <option value="Medium">Medium</option>
                <option value="Low">Low</option>
              </select>
            </div>
          </div>
        </div>

        {/* 4. LOGGING & ALERTS */}
        <div className="p-5 rounded-xl bg-[#0a1122]/90 border border-blue-500/20 shadow-lg space-y-4">
          <div className="flex items-center gap-2 border-b border-slate-800 pb-3">
            <Bell className="w-4 h-4 text-amber-400" />
            <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider font-sans">
              Logging &amp; Alert Notifications
            </h2>
          </div>

          <div className="space-y-3 text-xs">
            <div className="flex items-center justify-between p-2 rounded bg-[#070b16]">
              <span className="text-slate-300">Enable Audit Logging</span>
              <input
                type="checkbox"
                checked={settings.enable_logging}
                onChange={(e) => setSettings({ ...settings, enable_logging: e.target.checked })}
                className="w-4 h-4 rounded text-cyan-500 focus:ring-0"
              />
            </div>

            <div className="flex items-center justify-between p-2 rounded bg-[#070b16]">
              <span className="text-slate-300">Alert on Attack Detected</span>
              <input
                type="checkbox"
                checked={settings.alert_on_attack}
                onChange={(e) => setSettings({ ...settings, alert_on_attack: e.target.checked })}
                className="w-4 h-4 rounded text-red-500 focus:ring-0"
              />
            </div>

            <div className="flex items-center justify-between p-2 rounded bg-[#070b16]">
              <span className="text-slate-300">Simulation Debug Mode</span>
              <input
                type="checkbox"
                checked={settings.debug_mode}
                onChange={(e) => setSettings({ ...settings, debug_mode: e.target.checked })}
                className="w-4 h-4 rounded text-purple-500 focus:ring-0"
              />
            </div>
          </div>
        </div>
      </form>
    </div>
  );
};
