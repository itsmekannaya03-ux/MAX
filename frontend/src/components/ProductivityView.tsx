import React from 'react';
import { 
  Activity, Camera, CameraOff, Eye, EyeOff, ShieldCheck, 
  ShieldAlert, Clock, Monitor, Play, Pause, AlertCircle, CheckCircle2
} from 'lucide-react';
import { ProductivityStatus, ProductivityCheckIn } from '../types';
import { api } from '../api/client';

interface ProductivityViewProps {
  status?: ProductivityStatus;
  checkIn?: ProductivityCheckIn | null;
  onRefreshStatus: () => void;
  onEmergencyStop: () => void;
  onAnswerCheckIn: (working: boolean, reason?: string, adjust?: boolean) => void;
}

export const ProductivityView: React.FC<ProductivityViewProps> = ({
  status,
  checkIn,
  onRefreshStatus,
  onEmergencyStop,
  onAnswerCheckIn
}) => {
  const handleToggleMonitoring = async () => {
    if (!status) return;
    try {
      await api.toggleMonitoring(!status.monitoring_enabled);
      onRefreshStatus();
    } catch (e) {
      console.error(e);
    }
  };

  const handleToggleCamera = async () => {
    if (!status) return;
    const nextVal = !status.camera_permitted;
    if (nextVal) {
      const confirmConsent = confirm(
        "ENABLE OPTIONAL WEBCAM PRESENCE MONITORING?\n\n" +
        "Privacy Guarantee:\n" +
        "1. Snapshots are processed locally in memory for presence only.\n" +
        "2. No webcam photos or video are ever saved to disk or uploaded to any server.\n" +
        "3. A visible active camera indicator is displayed whenever active.\n" +
        "4. You can pause or stop monitoring anytime."
      );
      if (!confirmConsent) return;
    }
    try {
      await api.toggleCamera(nextVal);
      onRefreshStatus();
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto pb-12">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-5 rounded-2xl bg-slate-900 border border-slate-800 shadow-xl">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
            <Activity className="w-5 h-5 text-brand-400" />
            <span>Productivity & Focus Center</span>
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Real-time activity tracking, optional presence monitoring, and intelligent check-ins.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={onEmergencyStop}
            className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-red-600/20 hover:bg-red-600 text-red-400 hover:text-white border border-red-500/40 text-xs font-semibold transition-all shadow-sm"
          >
            <ShieldAlert className="w-3.5 h-3.5" />
            <span>Emergency Stop</span>
          </button>
        </div>
      </div>

      {/* Intelligent Check-in Card if Active */}
      {checkIn?.prompt_needed && (
        <div className="p-5 rounded-2xl bg-amber-500/10 border border-amber-500/30 text-amber-200 shadow-lg">
          <div className="flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
            <div className="flex-1">
              <span className="text-[11px] font-bold uppercase tracking-wider text-amber-400">Intelligent Check-In</span>
              <p className="text-sm font-semibold mt-1 text-slate-100">{checkIn.question}</p>
              
              <div className="mt-4 flex flex-wrap gap-2">
                <button
                  onClick={() => onAnswerCheckIn(true)}
                  className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold transition-all"
                >
                  Yes, I'm Working On It
                </button>
                <button
                  onClick={() => onAnswerCheckIn(false, 'Browsing', true)}
                  className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition-all"
                >
                  No, Reschedule Timetable
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Main Monitoring Controls Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {/* Activity Tracking Card */}
        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 shadow-lg space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Monitor className="w-4 h-4 text-brand-400" />
              <h3 className="text-sm font-bold text-white">System Activity Tracking</h3>
            </div>
            <button
              onClick={handleToggleMonitoring}
              className={`px-3 py-1 rounded-lg text-xs font-semibold border transition-all ${
                status?.monitoring_enabled
                  ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
                  : 'bg-slate-800 border-slate-700 text-slate-400'
              }`}
            >
              {status?.monitoring_enabled ? 'Active' : 'Disabled'}
            </button>
          </div>

          <p className="text-xs text-slate-400">
            Monitors foreground applications and idle time to calculate your productivity scores without storing personal data.
          </p>

          <div className="space-y-2 pt-2 border-t border-slate-800 text-xs">
            <div className="flex justify-between py-1 border-b border-slate-800/60">
              <span className="text-slate-400">Active Foreground App:</span>
              <span className="font-mono text-slate-200 font-semibold">{status?.active_app || 'Desktop / Explorer'}</span>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-800/60">
              <span className="text-slate-400">Window Title:</span>
              <span className="font-mono text-slate-300 truncate max-w-[200px]" title={status?.active_window}>
                {status?.active_window || 'System'}
              </span>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-800/60">
              <span className="text-slate-400">Current Task Match:</span>
              <span className={`font-semibold ${status?.current_task_name ? 'text-brand-400' : 'text-slate-500'}`}>
                {status?.current_task_name || 'No task active'}
              </span>
            </div>
            <div className="flex justify-between py-1">
              <span className="text-slate-400">Idle Seconds:</span>
              <span className="font-mono text-slate-300">{status?.idle_seconds || 0}s</span>
            </div>
          </div>
        </div>

        {/* Webcam Presence Card */}
        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 shadow-lg space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Camera className="w-4 h-4 text-brand-400" />
              <h3 className="text-sm font-bold text-white">Webcam Presence (Opt-In)</h3>
            </div>
            <button
              onClick={handleToggleCamera}
              className={`px-3 py-1 rounded-lg text-xs font-semibold border transition-all ${
                status?.camera_permitted
                  ? 'bg-rose-500/10 border-rose-500/30 text-rose-400'
                  : 'bg-slate-800 border-slate-700 text-slate-400'
              }`}
            >
              {status?.camera_permitted ? 'Permitted' : 'Off'}
            </button>
          </div>

          <p className="text-xs text-slate-400">
            Periodic snapshots for desk presence detection. Never saved to disk or uploaded to the cloud. Zero face recognition.
          </p>

          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-3">
            <div className="flex items-center justify-between text-xs">
              <span className="text-slate-400">Camera Status:</span>
              {status?.camera_active ? (
                <span className="flex items-center gap-1.5 text-rose-400 font-bold animate-pulse">
                  <span className="w-2 h-2 rounded-full bg-rose-500" /> Active Sensing
                </span>
              ) : (
                <span className="text-slate-500 font-medium">Standby / Inactive</span>
              )}
            </div>

            <div className="flex items-center justify-between text-xs">
              <span className="text-slate-400">Privacy Safeguard:</span>
              <span className="flex items-center gap-1 text-emerald-400 font-medium">
                <ShieldCheck className="w-3.5 h-3.5" /> 100% Local In-Memory
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

