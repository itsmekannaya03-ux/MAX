import React, { useState, useEffect } from 'react';
import { 
  Database, Plus, Search, Trash2, Edit3, 
  Sparkles, ShieldCheck, Tag, X
} from 'lucide-react';
import { Memory } from '../types';
import { api } from '../api/client';

export const MemoryView: React.FC = () => {
  const [memories, setMemories] = useState<Memory[]>([]);
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);

  // Form states
  const [newCategory, setNewCategory] = useState('preference');
  const [newKey, setNewKey] = useState('');
  const [newValue, setNewValue] = useState('');

  const loadMemories = async () => {
    try {
      if (searchQuery.trim()) {
        const res = await api.searchMemories(searchQuery.trim());
        setMemories(res);
      } else {
        const cat = categoryFilter === 'all' ? undefined : categoryFilter;
        const res = await api.getMemories(cat);
        setMemories(res);
      }
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    loadMemories();
  }, [categoryFilter, searchQuery]);

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this memory?')) return;
    try {
      await api.deleteMemory(id);
      loadMemories();
    } catch (e) {
      console.error(e);
    }
  };

  const handleAddSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newKey.trim() || !newValue.trim()) return;
    try {
      await api.createOrUpdateMemory({
        category: newCategory,
        key: newKey.trim(),
        value: newValue.trim(),
        source: 'user_explicit'
      });
      setShowAddModal(false);
      setNewKey('');
      setNewValue('');
      loadMemories();
    } catch (e) {
      console.error(e);
    }
  };

  const categories = ['all', 'preference', 'goal', 'routine', 'learning_history', 'project', 'note'];

  return (
    <div className="space-y-6 max-w-5xl mx-auto pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-5 rounded-2xl bg-slate-900 border border-slate-800 shadow-xl">
        <div>
          <div className="flex items-center gap-2">
            <Database className="w-5 h-5 text-brand-400" />
            <h2 className="text-xl font-bold text-white tracking-tight">AI Persistent Memory System</h2>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            MAX remembers your ongoing projects, goals, learning habits, and preferences across sessions.
          </p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold shadow-md shadow-brand-500/20 transition-all shrink-0"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>Add Memory</span>
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row gap-3 items-center justify-between">
        <div className="flex items-center gap-1 bg-slate-900 p-1 rounded-xl border border-slate-800 overflow-x-auto w-full sm:w-auto">
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => {
                setCategoryFilter(cat);
                setSearchQuery('');
              }}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium capitalize whitespace-nowrap transition-all ${
                categoryFilter === cat
                  ? 'bg-brand-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>

        <div className="relative w-full sm:w-64">
          <Search className="w-3.5 h-3.5 text-slate-500 absolute left-3 top-3" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search memories..."
            className="w-full bg-slate-900 border border-slate-800 rounded-xl pl-8 pr-3 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-brand-500 transition-colors"
          />
        </div>
      </div>

      {/* Memories Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {memories.length === 0 ? (
          <div className="col-span-full p-10 rounded-2xl bg-slate-900/60 border border-dashed border-slate-800 text-center">
            <Database className="w-10 h-10 text-slate-600 mx-auto mb-2" />
            <h4 className="text-sm font-semibold text-slate-300">No memory entries found</h4>
            <p className="text-xs text-slate-500 mt-1">
              Tell MAX 'Remember that I study better in the morning' or click 'Add Memory' above.
            </p>
          </div>
        ) : (
          memories.map((mem) => (
            <div
              key={mem.id}
              className="p-4 rounded-xl bg-slate-900 border border-slate-800 shadow-md space-y-2 hover:border-slate-700 transition-all flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between">
                  <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-brand-500/10 text-brand-400 border border-brand-500/20">
                    {mem.category}
                  </span>
                  <div className="flex items-center gap-1">
                    <span className="text-[10px] text-slate-500 capitalize">{mem.source.replace('_', ' ')}</span>
                    <button
                      onClick={() => handleDelete(mem.id)}
                      className="p-1 text-slate-500 hover:text-rose-400 rounded transition-colors"
                      title="Delete Memory"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>

                <h4 className="text-sm font-bold text-white mt-2">{mem.key}</h4>
                <p className="text-xs text-slate-300 leading-relaxed mt-1">{mem.value}</p>
              </div>

              <div className="text-[10px] text-slate-500 pt-2 border-t border-slate-800/80">
                Confidence: {Math.round(mem.confidence * 100)}%
              </div>
            </div>
          ))
        )}
      </div>

      {/* Add Memory Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-md p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <h3 className="text-base font-bold text-white">Save New Memory</h3>
              <button onClick={() => setShowAddModal(false)} className="text-slate-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleAddSubmit} className="space-y-3">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Category</label>
                <select
                  value={newCategory}
                  onChange={(e) => setNewCategory(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-xs text-slate-200 focus:outline-none focus:border-brand-500"
                >
                  <option value="preference">Preference</option>
                  <option value="goal">Goal</option>
                  <option value="routine">Routine</option>
                  <option value="project">Ongoing Project</option>
                  <option value="learning_history">Learning History</option>
                  <option value="note">General Note</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Title / Key</label>
                <input
                  type="text"
                  value={newKey}
                  onChange={(e) => setNewKey(e.target.value)}
                  placeholder="e.g. Study Preference"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-xs text-slate-200 focus:outline-none focus:border-brand-500"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Content / Fact</label>
                <textarea
                  rows={3}
                  value={newValue}
                  onChange={(e) => setNewValue(e.target.value)}
                  placeholder="e.g. Prefers studying math in the morning with 45-minute focus intervals"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-xs text-slate-200 focus:outline-none focus:border-brand-500"
                  required
                />
              </div>

              <div className="flex justify-end gap-2 pt-3 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold"
                >
                  Save Fact
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

