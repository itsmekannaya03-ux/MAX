import React, { useState, useEffect } from 'react';
import { 
  CheckCircle2, Clock, Play, ArrowRight, Sparkles, 
  PlusCircle, Coffee, RotateCcw, Monitor, Flame, AlertCircle, ChevronRight
} from 'lucide-react';
import { Task, ProductivityStatus, ProductivityCheckIn } from '../types';
import { api } from '../api/client';

interface DashboardViewProps {
  tasks: Task[];
  productivityStatus?: ProductivityStatus;
  checkIn?: ProductivityCheckIn | null;
  onRefreshTasks: () => void;
  onOpenTab: (tab: string) => void;
  onSendMessage: (msg: string) => void;
  onAnswerCheckIn: (working: boolean, reason?: string, adjust?: boolean) => void;
}

export const DashboardView: React.FC<DashboardViewProps> = ({
  tasks,
  productivityStatus,
  checkIn,
  onRefreshTasks,
  onOpenTab,
  onSendMessage,
  onAnswerCheckIn
}) => {
  const [quickInput, setQuickInput] = useState('');
  const [nowTime, setNowTime] = useState(new Date());

  useEffect(() => {
    const t = setInterval(() => setNowTime(new Date()), 1000);
    return () => clearInterval(t);
  }, []);

  const nowHour = nowTime.getHours();
  const greeting = nowHour < 12 ? 'Good morning' : nowHour < 17 ? 'Good afternoon' : 'Good evening';
  const nowStr = nowTime.toTimeString().slice(0, 5); // HH:MM

  // Find active task and next task
  const activeTask = tasks.find(
    (t) => t.completion_status !== 'completed' && t.completion_status !== 'skipped' && t.start_time <= nowStr && nowStr <= t.end_time
  ) || tasks.find((t) => t.completion_status === 'in_progress');

  const upcomingTasks = tasks.filter(
    (t) => t.completion_status !== 'completed' && t.completion_status !== 'skipped' && t.start_time > nowStr
  );
  const nextTask = upcomingTasks[0];

  const completedCount = tasks.filter((t) => t.completion_status === 'completed').length;
  const progressPct = tasks.length > 0 ? Math.round((completedCount / tasks.length) * 100) : 0;

  // Calculate minutes remaining in active task
  let minutesRemaining = 0;
  if (activeTask) {
    const [eh, em] = activeTask.end_time.split(':').map(Number);
    const endMinutes = eh * 60 + em;
    const currentMinutes = nowTime.getHours() * 60 + nowTime.getMinutes();
    minutesRemaining = Math.max(0, endMinutes - currentMinutes);
  }

  const handleMarkComplete = async (taskId: string) => {
    try {
      await api.updateTask(taskId, { completion_status: 'completed', progress_percentage: 100 });
      onRefreshTasks();
    } catch (e) {
      console.error(e);
    }
  };

  const handleQuickAdjust = async (prompt: string) => {
    try {
      await api.adjustTimetable(prompt);
      onRefreshTasks();
    } catch (e) {
      console.error(e);
    }
  };

  const handleQuickSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!quickInput.trim()) return;
    onSendMessage(quickInput.trim());
    setQuickInput('');
  };

  return (
    <div className="space-y-5 max-w-6xl mx-auto pb-10">
      {/* Executive Welcome & Proactive Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-5 rounded-2xl bg-gradient-to-r from-slate-900 via-slate-850 to-brand-950/40 border border-slate-800 shadow-xl">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-bold text-white tracking-tight">{greeting}, Executive</h2>
            <Sparkles className="w-4 h-4 text-brand-400" />
          </div>
          <p className="text-xs text-slate-400 mt-1">
            {new Date().toLocaleDateString(undefined, { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' })}
            {' • '}
            MAX is actively coordinating your schedule and focus.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => onOpenTab('timetable')}
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold shadow-md shadow-brand-500/20 transition-all"
          >
            <PlusCircle className="w-3.5 h-3.5" />
            <span>Plan / Adjust Day</span>
          </button>
          <button
            onClick={() => onOpenTab('chat')}
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition-all"
          >
            <span>Ask MAX</span>
            <ChevronRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Proactive Check-In Banner if needed */}
      {checkIn?.prompt_needed && (
        <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-200 flex flex-col md:flex-row items-start md:items-center justify-between gap-3 shadow-lg">
          <div className="flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
            <div>
              <h4 className="text-xs font-bold uppercase tracking-wider text-amber-400">Intelligent Check-In</h4>
              <p className="text-sm mt-0.5">{checkIn.question}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => onAnswerCheckIn(true)}
              className="px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold transition-all shadow-sm"
            >
              Yes, On Track
            </button>
            <button
              onClick={() => onAnswerCheckIn(false, 'Distracted', true)}
              className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition-all"
            >
              Reschedule
            </button>
          </div>
        </div>
      )}

      {/* Core Grid: Active Task & Today's Progress */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        {/* Active Task Card (2 columns wide on large screens) */}
        <div className="lg:col-span-2 p-5 rounded-2xl bg-slate-900 border border-slate-800 shadow-lg relative overflow-hidden flex flex-col justify-between">
          <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-brand-500 to-indigo-500" />
          
          <div>
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-bold uppercase tracking-wider text-brand-400 flex items-center gap-1.5">
                <Flame className="w-3.5 h-3.5 text-brand-400" /> Current Scheduled Block
              </span>
              {activeTask && (
                <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full uppercase tracking-wider ${
                  activeTask.priority === 'high' ? 'bg-rose-500/10 text-rose-400 border border-rose-500/30' :
                  activeTask.priority === 'low' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30' :
                  'bg-brand-500/10 text-brand-400 border border-brand-500/30'
                }`}>
                  {activeTask.priority} Priority
                </span>
              )}
            </div>

            {activeTask ? (
              <div className="mt-4">
                <h3 className="text-2xl font-bold text-white tracking-tight">{activeTask.name}</h3>
                <p className="text-xs text-slate-400 mt-1">{activeTask.description || 'Focus session in progress.'}</p>
                
                {/* Time slot & Countdown */}
                <div className="mt-5 grid grid-cols-2 sm:grid-cols-3 gap-3">
                  <div className="p-3 rounded-xl bg-slate-950/80 border border-slate-800">
                    <span className="text-[10px] text-slate-500 uppercase font-semibold">Time Slot</span>
                    <p className="text-sm font-semibold text-slate-200 mt-0.5">
                      {activeTask.start_time} - {activeTask.end_time}
                    </p>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-950/80 border border-slate-800">
                    <span className="text-[10px] text-slate-500 uppercase font-semibold">Total Duration</span>
                    <p className="text-sm font-semibold text-slate-200 mt-0.5">{activeTask.duration} Minutes</p>
                  </div>
                  <div className="p-3 rounded-xl bg-brand-950/30 border border-brand-500/30 col-span-2 sm:col-span-1">
                    <span className="text-[10px] text-brand-400 uppercase font-semibold">Remaining</span>
                    <p className="text-sm font-bold text-brand-300 mt-0.5">{minutesRemaining} Mins</p>
                  </div>
                </div>

                {/* Quick In-Task Actions */}
                <div className="mt-5 flex flex-wrap items-center gap-2 pt-4 border-t border-slate-800/80">
                  <button
                    onClick={() => handleMarkComplete(activeTask.id)}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold transition-all shadow-sm"
                  >
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>Mark Complete</span>
                  </button>
                  <button
                    onClick={() => handleQuickAdjust('I need another 15 minutes')}
                    className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium border border-slate-700 transition-all"
                  >
                    <span>+15 Mins</span>
                  </button>
                  <button
                    onClick={() => handleQuickAdjust('I need another 30 minutes')}
                    className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium border border-slate-700 transition-all"
                  >
                    <span>+30 Mins</span>
                  </button>
                  <button
                    onClick={() => handleQuickAdjust('I need a 15-minute break')}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium border border-slate-700 transition-all"
                  >
                    <Coffee className="w-3.5 h-3.5 text-amber-400" />
                    <span>Quick Break</span>
                  </button>
                </div>
              </div>
            ) : (
              <div className="py-8 text-center">
                <Clock className="w-10 h-10 text-slate-600 mx-auto mb-2" />
                <h4 className="text-base font-semibold text-slate-300">No Task Active Right Now</h4>
                <p className="text-xs text-slate-500 mt-1">
                  You are between tasks or have not generated today's timetable yet.
                </p>
                <button
                  onClick={() => onOpenTab('timetable')}
                  className="mt-4 px-4 py-2 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold transition-all"
                >
                  Generate Daily Schedule
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Next Task & Productivity Status */}
        <div className="space-y-5">
          {/* Next Task Card */}
          <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 shadow-lg">
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
              <ArrowRight className="w-3.5 h-3.5 text-indigo-400" /> Next Upcoming Task
            </span>
            {nextTask ? (
              <div className="mt-3">
                <h4 className="text-lg font-bold text-white">{nextTask.name}</h4>
                <p className="text-xs text-slate-400 mt-0.5">Starts at {nextTask.start_time} ({nextTask.duration} mins)</p>
                <div className="mt-3">
                  <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                    {nextTask.priority.toUpperCase()} PRIORITY
                  </span>
                </div>
              </div>
            ) : (
              <p className="text-xs text-slate-500 mt-3">All scheduled tasks for today are completed!</p>
            )}
          </div>

          {/* Today's Productivity Metrics */}
          <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 shadow-lg">
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
              <Monitor className="w-3.5 h-3.5 text-brand-400" /> Activity & Progress
            </span>
            <div className="mt-4 space-y-3">
              <div>
                <div className="flex items-center justify-between text-xs mb-1">
                  <span className="text-slate-400">Timetable Completion</span>
                  <span className="font-bold text-white">{progressPct}% ({completedCount}/{tasks.length})</span>
                </div>
                <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-brand-500 to-indigo-500 transition-all duration-500 rounded-full"
                    style={{ width: `${progressPct}%` }}
                  />
                </div>
              </div>

              <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-xs">
                <span className="text-slate-400">Focused Window:</span>
                <span className="font-mono text-slate-200 truncate max-w-[150px]" title={productivityStatus?.active_app}>
                  {productivityStatus?.active_app || 'Desktop'}
                </span>
              </div>

              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-400">State:</span>
                <span className={`font-semibold ${productivityStatus?.is_idle ? 'text-amber-400' : 'text-emerald-400'}`}>
                  {productivityStatus?.is_idle ? 'Away / Idle' : 'Active & Interacting'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Command & AI Bar */}
      <div className="p-4 rounded-2xl bg-slate-900 border border-slate-800 shadow-lg">
        <form onSubmit={handleQuickSubmit} className="flex items-center gap-2">
          <input
            type="text"
            value={quickInput}
            onChange={(e) => setQuickInput(e.target.value)}
            placeholder="Tell MAX anything: 'Move coding to evening', 'Explain binary trees', 'I completed math'..."
            className="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-brand-500 transition-colors"
          />
          <button
            type="submit"
            className="px-4 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold shadow-md shadow-brand-500/20 transition-all shrink-0"
          >
            Execute
          </button>
        </form>
      </div>
    </div>
  );
};

