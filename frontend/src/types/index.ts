export interface Task {
  id: string;
  name: string;
  start_time: string;
  end_time: string;
  duration: number;
  priority: 'low' | 'medium' | 'high';
  description?: string;
  completion_status: 'pending' | 'in_progress' | 'completed' | 'skipped';
  progress_percentage: number;
  reminders?: number[];
  dependencies?: string[];
  notes?: string;
  schedule_date: string;
}

export interface Memory {
  id: number;
  category: string;
  key: string;
  value: string;
  confidence: number;
  source: string;
  created_at?: string;
  updated_at?: string;
}

export interface ProductivityStatus {
  monitoring_enabled: boolean;
  camera_permitted: boolean;
  camera_active: boolean;
  active_window: string;
  active_app: string;
  is_idle: boolean;
  idle_seconds: number;
  focus_mode_active: boolean;
  current_task_id?: string;
  current_task_name?: string;
  today_focus_minutes: number;
  completion_rate_percentage: number;
}

export interface ProductivityCheckIn {
  prompt_needed: boolean;
  question?: string;
  current_task_name?: string;
  suggested_actions: string[];
}

export interface ChatMessage {
  id?: number;
  role: 'user' | 'assistant' | 'system';
  content: string;
  message_type?: string;
  created_at?: string;
}

export interface QuizQuestion {
  id: number;
  question: string;
  options: string[];
  correct_option_index: number;
  explanation: string;
}

export interface LessonExplainResponse {
  topic: string;
  level: string;
  concept_summary: string;
  breakdown_steps: string[];
  everyday_analogy: string;
  practical_code_or_example: string;
  comprehension_check: string;
}

export interface QuizResponse {
  session_id: number;
  topic: string;
  questions: QuizQuestion[];
}

export interface QuizResultResponse {
  session_id: number;
  score: number;
  total: number;
  percentage: number;
  feedback: string;
  detailed_answers: {
    question: string;
    your_answer: string;
    correct_answer: string;
    is_correct: boolean;
    explanation: string;
  }[];
}

export interface SearchResultItem {
  title: string;
  link: string;
  snippet: string;
}

export interface SearchResponse {
  query: string;
  summary: string;
  results: SearchResultItem[];
  verified: boolean;
}

export interface SystemSettings {
  AI_PROVIDER: string;
  AI_MODEL: string;
  GEMINI_API_KEY_MASKED: string;
  OPENAI_API_KEY_MASKED: string;
  GROQ_API_KEY_MASKED: string;
  OLLAMA_BASE_URL: string;
  DEFAULT_TTS_VOICE: string;
  DEFAULT_TTS_SPEED: number;
  ALLOW_WEBCAM_MONITORING: boolean;
  ACTIVITY_MONITOR_ENABLED: boolean;
  IDLE_THRESHOLD_SECONDS: number;
}

export interface SystemDiagnostics {
  os: string;
  hostname: string;
  cpu_percent: number;
  memory_used_gb: number;
  memory_total_gb: number;
  memory_percent: number;
  disk_percent: number;
  battery_percent?: number | null;
  battery_plugged?: boolean | null;
  current_time: string;
}

