import {
  Task, Memory, ProductivityStatus, ProductivityCheckIn,
  ChatMessage, LessonExplainResponse, QuizResponse, QuizResultResponse,
  SearchResponse, SystemSettings, SystemDiagnostics
} from '../types';

const BASE_URL = 'http://127.0.0.1:8000';

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const fullUrl = url.startsWith('http') ? url : `${BASE_URL}${url}`;
  const res = await fetch(fullUrl, {
    headers: {
      'Content-Type': 'application/json',
      ...(options?.headers || {})
    },
    ...options
  });
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`HTTP ${res.status}: ${errorText || res.statusText}`);
  }
  return res.json();
}

export const api = {
  // Health
  getHealth: () => fetchJson<{ status: string; app: string; local_time: string; ai_provider: string }>(`/api/health`),

  // Chat & Commands
  sendChatMessage: (message: string, voice_input = false, context_date?: string) =>
    fetchJson<{ reply: string; speech_text?: string; action_type: string; action_payload?: any }>(
      `/api/chat`,
      { method: 'POST', body: JSON.stringify({ message, voice_input, context_date }) }
    ),
  getChatHistory: () => fetchJson<ChatMessage[]>(`/api/chat/history`),
  clearChatHistory: () => fetchJson<{ status: string }>(`/api/chat/history`, { method: 'DELETE' }),

  // Timetable
  getTimetable: (date?: string) =>
    fetchJson<Task[]>(date ? `/api/timetable?date=${date}` : `/api/timetable`),
  generateTimetable: (tasks: string[], working_hours_end = '22:00', include_breaks = true) =>
    fetchJson<Task[]>(`/api/timetable/generate`, {
      method: 'POST',
      body: JSON.stringify({ tasks_to_accomplish: tasks, working_hours_end, include_breaks })
    }),
  adjustTimetable: (user_prompt: string, target_date?: string) =>
    fetchJson<{ success: boolean; message: string; action?: string; adjusted_tasks?: Task[] }>(
      `/api/timetable/adjust`,
      { method: 'POST', body: JSON.stringify({ user_prompt, target_date }) }
    ),
  createTask: (task: Partial<Task>) =>
    fetchJson<Task>(`/api/timetable/task`, { method: 'POST', body: JSON.stringify(task) }),
  updateTask: (taskId: string, updates: Partial<Task>) =>
    fetchJson<Task>(`/api/timetable/task/${taskId}`, { method: 'PUT', body: JSON.stringify(updates) }),
  deleteTask: (taskId: string) =>
    fetchJson<{ status: string }>(`/api/timetable/task/${taskId}`, { method: 'DELETE' }),

  // Productivity
  getProductivityStatus: () => fetchJson<ProductivityStatus>(`/api/productivity/status`),
  toggleMonitoring: (enabled: boolean) =>
    fetchJson<{ status: string; monitoring_enabled: boolean }>(`/api/productivity/toggle-monitoring?enabled=${enabled}`, { method: 'POST' }),
  toggleCamera: (permitted: boolean) =>
    fetchJson<{ status: string; camera_permitted: boolean }>(`/api/productivity/toggle-camera?permitted=${permitted}`, { method: 'POST' }),
  emergencyStop: () =>
    fetchJson<{ status: string; message: string }>(`/api/productivity/emergency-stop`, { method: 'POST' }),
  getCheckIn: () => fetchJson<ProductivityCheckIn>(`/api/productivity/check-in`),
  answerCheckIn: (working_on_task: boolean, actual_activity?: string, adjust_schedule?: boolean) =>
    fetchJson<{ status: string; message: string }>(`/api/productivity/check-in/answer`, {
      method: 'POST',
      body: JSON.stringify({ working_on_task, actual_activity, adjust_schedule })
    }),

  // AI Teacher
  explainTopic: (topic: string, user_level = 'beginner') =>
    fetchJson<LessonExplainResponse>(`/api/learning/explain`, {
      method: 'POST',
      body: JSON.stringify({ topic, user_level })
    }),
  generateQuiz: (topic: string, num_questions = 3, level = 'beginner') =>
    fetchJson<QuizResponse>(`/api/learning/quiz`, {
      method: 'POST',
      body: JSON.stringify({ topic, num_questions, level })
    }),
  submitQuiz: (session_id: number, answers: number[]) =>
    fetchJson<QuizResultResponse>(`/api/learning/quiz/submit`, {
      method: 'POST',
      body: JSON.stringify({ session_id, answers })
    }),
  getLearningHistory: () => fetchJson<any[]>(`/api/learning/history`),

  // Search
  searchWeb: (query: string, limit = 5) =>
    fetchJson<SearchResponse>(`/api/search?q=${encodeURIComponent(query)}&limit=${limit}`),

  // Memory
  getMemories: (category?: string) =>
    fetchJson<Memory[]>(category ? `/api/memory?category=${category}` : `/api/memory`),
  createOrUpdateMemory: (mem: { category: string; key: string; value: string; confidence?: number; source?: string }) =>
    fetchJson<Memory>(`/api/memory`, { method: 'POST', body: JSON.stringify(mem) }),
  deleteMemory: (id: number) =>
    fetchJson<{ status: string }>(`/api/memory/${id}`, { method: 'DELETE' }),
  searchMemories: (q: string) =>
    fetchJson<Memory[]>(`/api/memory/search?q=${encodeURIComponent(q)}`),

  // Settings & Diagnostics
  getSettings: () => fetchJson<SystemSettings>(`/api/settings`),
  updateSettings: (settings: Partial<SystemSettings>) =>
    fetchJson<{ status: string; message: string }>(`/api/settings`, { method: 'POST', body: JSON.stringify(settings) }),
  getDiagnostics: () => fetchJson<SystemDiagnostics>(`/api/settings/diagnostics`),
};

