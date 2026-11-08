import React, { useState } from 'react';
import { 
  Calendar, Plus, Sparkles, CheckCircle2, Clock, Trash2, 
  RotateCcw, Play, AlertCircle, Coffee, ChevronRight, X
} from 'lucide-react';
import { Task } from '../types';
import { api } from '../api/client';

interface TimetableViewProps {
  tasks: Task[];
  onRefreshTasks: () => void;
}

export const TimetableView: React.FC<TimetableViewProps> = ({ tasks, onRefreshTasks }) => {
  const [showGenerateModal, setShowGenerateModal] = useState(false);
  const [showAddTaskModal, setShowAddTaskModal] = useState(false);
  const [reschedulePrompt, setReschedulePrompt] = useState('');
  const [rescheduleResult, setRescheduleResult] = useState<string | null>(null);

  // Generate Wizard form states
  const [rawTasksInput, setRawTasksInput] = useState('Study Python programming 60 mins\nPractice Math calculus 60 mins\nRevise Physics formulas 45 mins');
  const [completedSoFar, setCompletedSoFar] = useState('');
  const [endTime, setEndTime] = useState('22:00');
  const [includeBreaks, setIncludeBreaks] = useState(true);

  // New task form state
  const [newTaskName, setNewTaskName] = useState('');
  const [newTaskStart, setNewTaskStart] = useState('14:00');
  const [newTaskEnd, setNewTaskEnd] = useState('15:00');
  const [newTaskDuration, setNewTaskDuration] = useState(60);
  const [newTaskPriority, setNewTaskPriority] = useState<'low' | 'medium' | 'high'>('medium');

  const handleToggleStatus = async (task: Task) => {
    const nextStatus = task.completion_status === 'completed' ? 'pending' : 'completed';
    const nextPct = nextStatus === 'completed' ? 100 : 0;
    try {
      await api.updateTask(task.id, { completion_status: nextStatus, progress_percentage: nextPct });
      onRefreshTasks();
    } catch (e) {
      console.error(e);
    }
  };

  const handleDeleteTask = async (taskId: string) => {
    if (!confirm('Are you sure you want to delete this task?')) return;
    try {
      await api.deleteTask(taskId);
      onRefreshTasks();
    } catch (e) {
      console.error(e);
    }
  };

  const handleGenerateSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const taskList = rawTasksInput.split('\n').map((s) => s.trim()).filter(Boolean);
    if (taskList.length === 0) return;
    try {
      await api.generateTimetable(taskList, endTime, includeBreaks);
      setShowGenerateModal(false);
      onRefreshTasks();
    } catch (e) {
      console.error(e);
    }
  };

  const handleRescheduleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!reschedulePrompt.trim()) return;
    try {
      const res = await api.adjustTimetable(reschedulePrompt);
      setRescheduleResult(res.message);
      setReschedulePrompt('');
      onRefreshTasks();
      setTimeout(() => setRescheduleResult(null), 8000);
    } catch (e) {
      console.error(e);
    }
  };

  const handleCreateTaskSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTaskName.trim()) return;
    try {
      await api.createTask({
        name: newTaskName.trim(),
        start_time: newTaskStart,
        end_time: newTaskEnd,
        duration: newTaskDuration,
        priority: newTaskPriority,
        completion_status: 'pending',
        progress_percentage: 0,
        schedule_date: new Date().toISOString().slice(0, 10)
      });
      setShowAddTaskModal(false);
      setNewTaskName('');
      onRefreshTasks();
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto pb-12">
      {/* Timetable Header & Action Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-5 rounded-2xl bg-slate-900 border border-slate-800 shadow-xl">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
            <Calendar className="w-5 h-5 text-brand-400" />
            <span>Intelligent Daily Timetable</span>
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Dynamic, non-overlapping schedule automatically synchronized by MAX.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowAddTaskModal(true)}
            className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition-all"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Add Single Task</span>
          </button>
          <button
            onClick={() => setShowGenerateModal(true)}
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold shadow-md shadow-brand-500/20 transition-all"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Plan My Day</span>
          </button>
        </div>
      </div>

      {/* Dynamic NLP Reschedule Box */}
      <div className="p-4 rounded-2xl bg-slate-900 border border-slate-800 shadow-md">
        <div className="flex items-center gap-1.5 mb-2">
          <RotateCcw className="w-3.5 h-3.5 text-brand-400" />
          <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
            Natural Language Rescheduler
          </h4>
        </div>
        <form onSubmit={handleRescheduleSubmit} className="flex gap-2">
          <input
            type="text"
            value={reschedulePrompt}
            onChange={(e) => setReschedulePrompt(e.target.value)}
            placeholder="Try: 'I need another 30 mins', 'I need to go outside for 1 hour', 'Move coding to evening'..."
            className="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-4 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-brand-500 transition-colors"
          />
          <button
            type="submit"
            className="px-4 py-2 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold transition-all shrink-0"
          >
            Recalculate
          </button>
        </form>

        {/* Reschedule confirmation toast banner */}
        {rescheduleResult && (
          <div className="mt-3 p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
            <span>{rescheduleResult}</span>
          </div>
        )}
      </div>

      {/* Visual Timeline of Tasks */}
      <div className="space-y-3">
        {tasks.length === 0 ? (
          <div className="p-10 rounded-2xl bg-slate-900/60 border border-dashed border-slate-800 text-center">
            <Calendar className="w-10 h-10 text-slate-600 mx-auto mb-2" />
            <h4 className="text-sm font-semibold text-slate-300">No timetable generated for today</h4>
            <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
              Click 'Plan My Day' above and list your goals, subjects, or projects. MAX will automatically arrange realistic time blocks.
            </p>
          </div>
        ) : (
          tasks.map((task) => {
            const isCompleted = task.completion_status === 'completed';
            const isBreak = task.name.toLowerCase().includes('break') || task.name.toLowerCase().includes('recharge');
            return (
              <div
                key={task.id}
                className={`flex items-center justify-between p-4 rounded-xl border transition-all ${
                  isCompleted
                    ? 'bg-slate-950/40 border-slate-900 opacity-60'
                    : isBreak
                    ? 'bg-amber-950/10 border-amber-500/20'
                    : 'bg-slate-900 border-slate-800 hover:border-slate-700 shadow-md'
                }`}
              >
                <div className="flex items-center gap-3">
                  {/* Status Toggle Button */}
                  <button
                    onClick={() => handleToggleStatus(task)}
                    className={`w-6 h-6 rounded-lg flex items-center justify-center transition-all ${
                      isCompleted
                        ? 'bg-emerald-600 text-white'
                        : 'border border-slate-700 hover:border-brand-500 text-transparent'
                    }`}
                  >
                    <CheckCircle2 className="w-4 h-4" />
                  </button>

                  <div>
                    <div className="flex items-center gap-2">
                      <span className={`text-sm font-bold ${isCompleted ? 'line-through text-slate-500' : 'text-slate-100'}`}>
                        {task.name}
                      </span>
                      {isBreak && <Coffee className="w-3.5 h-3.5 text-amber-400" />}
                      <span className={`text-[10px] font-semibold px-2 py-0.5 rounded uppercase tracking-wider ${
                        task.priority === 'high' ? 'bg-rose-500/10 text-rose-400 border border-rose-500/30' :
                        task.priority === 'low' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30' :
                        'bg-brand-500/10 text-brand-400 border border-brand-500/30'
                      }`}>
                        {task.priority}
                      </span>
                    </div>
                    <div className="flex items-center gap-3 text-xs text-slate-400 mt-1">
                      <span className="flex items-center gap-1 font-mono">
                        <Clock className="w-3 h-3 text-slate-500" />
                        {task.start_time} - {task.end_time}
                      </span>
                      <span>•</span>
                      <span>{task.duration} mins</span>
                      {task.description && (
                        <>
                          <span>•</span>
                          <span className="truncate max-w-xs">{task.description}</span>
                        </>
                      )}
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleDeleteTask(task.id)}
                    className="p-1.5 rounded-lg text-slate-500 hover:text-rose-400 hover:bg-slate-800 transition-colors"
                    title="Delete Task"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Plan My Day Modal */}
      {showGenerateModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-lg p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-brand-400" />
                <h3 className="text-base font-bold text-white">Plan Your Daily Timetable</h3>
              </div>
              <button onClick={() => setShowGenerateModal(false)} className="text-slate-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleGenerateSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  What do you need to accomplish today? (One per line)
                </label>
                <textarea
                  rows={4}
                  value={rawTasksInput}
                  onChange={(e) => setRawTasksInput(e.target.value)}
                  placeholder="e.g.&#10;Complete Python OOP project 60 mins&#10;Study Math calculus 60 mins&#10;Read Chemistry chapter 45 mins"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-slate-200 focus:outline-none focus:border-brand-500 font-mono"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">Working End Limit</label>
                  <input
                    type="time"
                    value={endTime}
                    onChange={(e) => setEndTime(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-xs text-slate-200 focus:outline-none focus:border-brand-500"
                  />
                </div>
                <div className="flex items-center pt-5">
                  <label className="flex items-center gap-2 cursor-pointer text-xs text-slate-300">
                    <input
                      type="checkbox"
                      checked={includeBreaks}
                      onChange={(e) => setIncludeBreaks(e.target.checked)}
                      className="rounded border-slate-700 text-brand-600 focus:ring-0"
                    />
                    <span>Include 15m wellness breaks</span>
                  </label>
                </div>
              </div>

              <div className="flex justify-end gap-2 pt-3 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowGenerateModal(false)}
                  className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold shadow-md shadow-brand-500/20"
                >
                  Generate Timetable
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Add Single Task Modal */}
      {showAddTaskModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-md p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <h3 className="text-base font-bold text-white">Add Single Task</h3>
              <button onClick={() => setShowAddTaskModal(false)} className="text-slate-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateTaskSubmit} className="space-y-3">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Task Name</label>
                <input
                  type="text"
                  value={newTaskName}
                  onChange={(e) => setNewTaskName(e.target.value)}
                  placeholder="e.g. JavaScript Async Practice"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-xs text-slate-200 focus:outline-none focus:border-brand-500"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">Start Time</label>
                  <input
                    type="time"
                    value={newTaskStart}
                    onChange={(e) => setNewTaskStart(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-xs text-slate-200 focus:outline-none focus:border-brand-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">End Time</label>
                  <input
                    type="time"
                    value={newTaskEnd}
                    onChange={(e) => setNewTaskEnd(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-xs text-slate-200 focus:outline-none focus:border-brand-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Priority</label>
                <select
                  value={newTaskPriority}
                  onChange={(e: any) => setNewTaskPriority(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-xs text-slate-200 focus:outline-none focus:border-brand-500"
                >
                  <option value="low">Low Priority</option>
                  <option value="medium">Medium Priority</option>
                  <option value="high">High Priority</option>
                </select>
              </div>

              <div className="flex justify-end gap-2 pt-3 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowAddTaskModal(false)}
                  className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold"
                >
                  Create Task
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

