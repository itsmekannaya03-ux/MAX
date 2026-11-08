import React, { useState, useEffect } from 'react';
import { 
  ShieldAlert, Settings as SettingsIcon, Volume2, VolumeX, 
  LayoutDashboard, MessageSquare, Calendar, Activity, 
  GraduationCap, Database, Sparkles, Clock, Eye
} from 'lucide-react';
import { ProductivityStatus } from '../types';

interface HeaderProps {
  currentTab: string;
  setCurrentTab: (tab: string) => void;
  openSettings: () => void;
  productivityStatus?: ProductivityStatus;
  onEmergencyStop: () => void;
  speechEnabled: boolean;
  setSpeechEnabled: (val: boolean) => void;
}

export const Header: React.FC<HeaderProps> = ({
  currentTab,
  setCurrentTab,
  openSettings,
  productivityStatus,
  onEmergencyStop,
  speechEnabled,
  setSpeechEnabled
}) => {
  const [time, setTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'chat', label: 'Chat & Voice', icon: MessageSquare },
    { id: 'timetable', label: 'Timetable', icon: Calendar },
    { id: 'productivity', label: 'Productivity', icon: Activity },
    { id: 'teacher', label: 'AI Teacher', icon: GraduationCap },
    { id: 'memory', label: 'Memory', icon: Database },
  ];

  return (
    <header className="border-b border-slate-800 bg-slate-900/90 backdrop-blur sticky top-0 z-40 px-4 py-2.5 flex flex-wrap items-center justify-between gap-3 shadow-md">
      {/* Brand & Identity */}
      <div className="flex items-center gap-3">
        <div className="relative">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-600 to-indigo-600 flex items-center justify-center shadow-lg shadow-brand-500/20">
            <span className="font-extrabold tracking-wider text-white text-base">MAX</span>
          </div>
          <span className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-emerald-500 border-2 border-slate-900 rounded-full animate-pulse" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h1 className="font-bold text-slate-100 text-sm tracking-wide">MAX</h1>
            <span className="text-[10px] uppercase font-semibold tracking-wider px-1.5 py-0.5 rounded bg-brand-500/10 text-brand-400 border border-brand-500/20">
              AI Executive
            </span>
          </div>
          <p className="text-[11px] text-slate-400">My AI eXecutive Assistant</p>
        </div>
      </div>

      {/* Nav Tabs */}
      <nav className="flex items-center bg-slate-950/80 p-1 rounded-xl border border-slate-800 overflow-x-auto">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setCurrentTab(item.id)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all whitespace-nowrap ${
                isActive
                  ? 'bg-brand-600 text-white shadow-sm shadow-brand-500/20 font-semibold'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      {/* Real-time Clock & Global Actions */}
      <div className="flex items-center gap-2.5">
        {/* Live Camera Indicator if active */}
        {productivityStatus?.camera_active && (
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs font-semibold animate-pulse">
            <Eye className="w-3.5 h-3.5 text-rose-500" />
            <span>Camera Active</span>
          </div>
        )}

        {/* Local Clock */}
        <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-950 border border-slate-800 text-xs font-mono text-slate-300">
          <Clock className="w-3.5 h-3.5 text-brand-400" />
          <span>{time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}</span>
        </div>

        {/* Voice Audio Toggle */}
        <button
          onClick={() => setSpeechEnabled(!speechEnabled)}
          title={speechEnabled ? "Mute Spoken Responses" : "Unmute Spoken Responses"}
          className={`p-2 rounded-lg border text-xs transition-colors ${
            speechEnabled 
              ? 'bg-brand-500/10 border-brand-500/30 text-brand-400 hover:bg-brand-500/20' 
              : 'bg-slate-800/60 border-slate-700 text-slate-400 hover:text-slate-200'
          }`}
        >
          {speechEnabled ? <Volume2 className="w-4 h-4" /> : <VolumeX className="w-4 h-4" />}
        </button>

        {/* Emergency Stop Button */}
        <button
          onClick={onEmergencyStop}
          title="Emergency Stop: Instantly Halts All Monitoring and Camera"
          className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-red-600/20 hover:bg-red-600 text-red-400 hover:text-white border border-red-500/40 text-xs font-semibold transition-all shadow-sm"
        >
          <ShieldAlert className="w-3.5 h-3.5" />
          <span className="hidden md:inline">Emergency Stop</span>
        </button>

        {/* Settings Button */}
        <button
          onClick={openSettings}
          title="Configure AI Models, Keys, and Settings"
          className="p-2 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-300 hover:text-white border border-slate-700 text-xs transition-colors"
        >
          <SettingsIcon className="w-4 h-4" />
        </button>
      </div>
    </header>
  );
};

