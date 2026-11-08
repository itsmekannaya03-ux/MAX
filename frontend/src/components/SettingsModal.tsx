import React, { useState, useEffect } from 'react';
import { 
  X, Save, Cpu, Key, Volume2, Shield, 
  Sparkles, CheckCircle2, HardDrive, Battery
} from 'lucide-react';
import { SystemSettings, SystemDiagnostics } from '../types';
import { api } from '../api/client';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const SettingsModal: React.FC<SettingsModalProps> = ({ isOpen, onClose }) => {
  const [settings, setSettings] = useState<SystemSettings | null>(null);
  const [diagnostics, setDiagnostics] = useState<SystemDiagnostics | null>(null);
  const [geminiKey, setGeminiKey] = useState('');
  const [openaiKey, setOpenaiKey] = useState('');
  const [groqKey, setGroqKey] = useState('');
  const [aiProvider, setAiProvider] = useState('offline');
  const [aiModel, setAiModel] = useState('gemini-2.5-flash');
  const [saveSuccess, setSaveSuccess] = useState(false);

  useEffect(() => {
    if (isOpen) {
      loadData();
    }
  }, [isOpen]);

  const loadData = async () => {
    try {
      const [s, d] = await Promise.all([api.getSettings(), api.getDiagnostics()]);
      setSettings(s);
      setDiagnostics(d);
      setAiProvider(s.AI_PROVIDER || 'offline');
      setAiModel(s.AI_MODEL || 'gemini-2.5-flash');
    } catch (e) {
      console.error(e);
    }
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const payload: any = {
        AI_PROVIDER: aiProvider,
        AI_MODEL: aiModel
      };
      if (geminiKey.trim()) payload.GEMINI_API_KEY = geminiKey.trim();
      if (openaiKey.trim()) payload.OPENAI_API_KEY = openaiKey.trim();
      if (groqKey.trim()) payload.GROQ_API_KEY = groqKey.trim();

      await api.updateSettings(payload);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
      loadData();
    } catch (e) {
      console.error(e);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto p-6 shadow-2xl space-y-5">
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-brand-400" />
            <h3 className="text-base font-bold text-white">MAX Executive Settings</h3>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white">
            <X className="w-5 h-5" />
          </button>
        </div>

        {saveSuccess && (
          <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
            <span>Settings successfully saved and loaded!</span>
          </div>
        )}

        <form onSubmit={handleSave} className="space-y-5">
          {/* AI Provider Configuration */}
          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-3">
            <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-brand-400">
              <Key className="w-4 h-4 text-brand-400" />
              <span>AI Intelligence Engine Provider</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Active AI Provider</label>
                <select
                  value={aiProvider}
                  onChange={(e) => setAiProvider(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-800 rounded-xl p-2.5 text-xs text-slate-200 focus:outline-none focus:border-brand-500"
                >
                  <option value="offline">Offline / Local Heuristic (Zero Cost)</option>
                  <option value="gemini">Google Gemini (Recommended)</option>
                  <option value="openai">OpenAI (GPT-4o / GPT-4o-mini)</option>
                  <option value="groq">Groq (Ultra-fast LLaMA)</option>
                  <option value="ollama">Ollama (Local LLM)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Model Name</label>
                <input
                  type="text"
                  value={aiModel}
                  onChange={(e) => setAiModel(e.target.value)}
                  placeholder="e.g. gemini-2.5-flash or gpt-4o-mini"
                  className="w-full bg-slate-900 border border-slate-800 rounded-xl p-2.5 text-xs text-slate-200 focus:outline-none focus:border-brand-500"
                />
              </div>
            </div>

            {/* API Keys */}
            <div className="space-y-2 pt-2 border-t border-slate-850">
              <div>
                <label className="block text-[11px] font-semibold text-slate-400 mb-1">
                  Google Gemini API Key {settings?.GEMINI_API_KEY_MASKED && `(Current: ${settings.GEMINI_API_KEY_MASKED})`}
                </label>
                <input
                  type="password"
                  value={geminiKey}
                  onChange={(e) => setGeminiKey(e.target.value)}
                  placeholder="Paste new Gemini API key here..."
                  className="w-full bg-slate-900 border border-slate-800 rounded-xl p-2 text-xs text-slate-200 focus:outline-none focus:border-brand-500 font-mono"
                />
              </div>

              <div>
                <label className="block text-[11px] font-semibold text-slate-400 mb-1">
                  OpenAI API Key {settings?.OPENAI_API_KEY_MASKED && `(Current: ${settings.OPENAI_API_KEY_MASKED})`}
                </label>
                <input
                  type="password"
                  value={openaiKey}
                  onChange={(e) => setOpenaiKey(e.target.value)}
                  placeholder="Paste new OpenAI API key here..."
                  className="w-full bg-slate-900 border border-slate-800 rounded-xl p-2 text-xs text-slate-200 focus:outline-none focus:border-brand-500 font-mono"
                />
              </div>

              <div>
                <label className="block text-[11px] font-semibold text-slate-400 mb-1">
                  Groq API Key {settings?.GROQ_API_KEY_MASKED && `(Current: ${settings.GROQ_API_KEY_MASKED})`}
                </label>
                <input
                  type="password"
                  value={groqKey}
                  onChange={(e) => setGroqKey(e.target.value)}
                  placeholder="Paste new Groq API key here..."
                  className="w-full bg-slate-900 border border-slate-800 rounded-xl p-2 text-xs text-slate-200 focus:outline-none focus:border-brand-500 font-mono"
                />
              </div>
            </div>
          </div>

          {/* System Diagnostics Display */}
          {diagnostics && (
            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
              <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-slate-400">
                <Cpu className="w-4 h-4 text-brand-400" />
                <span>Host Diagnostics</span>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-1 text-xs">
                <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-850">
                  <span className="text-[10px] text-slate-500 uppercase">OS</span>
                  <p className="font-semibold text-slate-200 mt-0.5 truncate">{diagnostics.os}</p>
                </div>
                <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-850">
                  <span className="text-[10px] text-slate-500 uppercase">Memory</span>
                  <p className="font-semibold text-slate-200 mt-0.5">{diagnostics.memory_used_gb} / {diagnostics.memory_total_gb} GB</p>
                </div>
                <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-850">
                  <span className="text-[10px] text-slate-500 uppercase">CPU Usage</span>
                  <p className="font-semibold text-slate-200 mt-0.5">{diagnostics.cpu_percent}%</p>
                </div>
                <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-850">
                  <span className="text-[10px] text-slate-500 uppercase">Disk Used</span>
                  <p className="font-semibold text-slate-200 mt-0.5">{diagnostics.disk_percent}%</p>
                </div>
              </div>
            </div>
          )}

          <div className="flex justify-end gap-2 pt-2 border-t border-slate-800">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold"
            >
              Close
            </button>
            <button
              type="submit"
              className="flex items-center gap-1.5 px-5 py-2 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold shadow-md shadow-brand-500/20"
            >
              <Save className="w-3.5 h-3.5" />
              <span>Save Settings</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

