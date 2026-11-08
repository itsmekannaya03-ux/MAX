import React, { useState, useEffect, useRef } from 'react';
import { Header } from './components/Header';
import { DashboardView } from './components/DashboardView';
import { ChatView } from './components/ChatView';
import { TimetableView } from './components/TimetableView';
import { ProductivityView } from './components/ProductivityView';
import { TeacherView } from './components/TeacherView';
import { MemoryView } from './components/MemoryView';
import { SettingsModal } from './components/SettingsModal';
import { Task, ProductivityStatus, ProductivityCheckIn, ChatMessage } from './types';
import { api } from './api/client';

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<string>('dashboard');
  const [isSettingsOpen, setIsSettingsOpen] = useState<boolean>(false);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [productivityStatus, setProductivityStatus] = useState<ProductivityStatus | undefined>();
  const [checkIn, setCheckIn] = useState<ProductivityCheckIn | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [speechEnabled, setSpeechEnabled] = useState<boolean>(true);
  const [isSpeaking, setIsSpeaking] = useState<boolean>(false);
  const wsRef = useRef<WebSocket | null>(null);

  // Load initial state
  useEffect(() => {
    fetchTasks();
    fetchProductivity();
    fetchChatHistory();

    // Setup periodic polling for background monitoring & check-in
    const interval = setInterval(() => {
      fetchProductivity();
      checkForCheckIn();
    }, 15000);

    // Setup WebSocket connection for real-time notifications
    setupWebSocket();

    return () => {
      clearInterval(interval);
      wsRef.current?.close();
    };
  }, []);

  const setupWebSocket = () => {
    try {
      const ws = new WebSocket('ws://127.0.0.1:8000/ws');
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'notification') {
            // Native notification received from backend
            if (speechEnabled && data.message) {
              speakText(data.message);
            }
          }
        } catch (e) {
          console.error('WS parse error', e);
        }
      };
      ws.onclose = () => {
        setTimeout(setupWebSocket, 5000); // Reconnect loop
      };
      wsRef.current = ws;
    } catch (e) {
      console.warn('WS connection failed, polling fallback active', e);
    }
  };

  const fetchTasks = async () => {
    try {
      const t = await api.getTimetable();
      setTasks(t);
    } catch (e) {
      console.error(e);
    }
  };

  const fetchProductivity = async () => {
    try {
      const s = await api.getProductivityStatus();
      setProductivityStatus(s);
    } catch (e) {
      console.error(e);
    }
  };

  const checkForCheckIn = async () => {
    try {
      const c = await api.getCheckIn();
      if (c && c.prompt_needed) {
        setCheckIn(c);
        if (speechEnabled && c.question) {
          speakText(c.question);
        }
      } else {
        setCheckIn(null);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const fetchChatHistory = async () => {
    try {
      const h = await api.getChatHistory();
      setMessages(h);
    } catch (e) {
      console.error(e);
    }
  };

  // Text to Speech
  const speakText = (text: string) => {
    if (!('speechSynthesis' in window)) return;
    window.speechSynthesis.cancel();

    // Clean markdown and symbols
    const clean = text
      .replace(/```[\s\S]*?```/g, 'Code example shown on screen.')
      .replace(/`([^`]+)`/g, '$1')
      .replace(/\*\*([^*]+)\*\*/g, '$1')
      .replace(/#+\s*/g, '')
      .replace(/http[s]?:\/\/\S+/g, '')
      .trim();

    if (!clean) return;

    const utterance = new SpeechSynthesisUtterance(clean);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;

    // Pick a natural English voice if available
    const voices = window.speechSynthesis.getVoices();
    const naturalVoice = voices.find(
      (v) => v.lang.startsWith('en') && (v.name.includes('Natural') || v.name.includes('Online') || v.name.includes('Google') || v.name.includes('Jenny') || v.name.includes('Guy'))
    ) || voices.find((v) => v.lang.startsWith('en'));

    if (naturalVoice) utterance.voice = naturalVoice;

    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);

    window.speechSynthesis.speak(utterance);
  };

  const stopSpeaking = () => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }
    setIsSpeaking(false);
  };

  const handleSendMessage = async (msg: string, voice = false) => {
    // Add user message optimistically
    const userMsg: ChatMessage = { role: 'user', content: msg };
    setMessages((prev) => [...prev, userMsg]);

    try {
      const res = await api.sendChatMessage(msg, voice);
      const botMsg: ChatMessage = { role: 'assistant', content: res.reply, message_type: res.action_type };
      setMessages((prev) => [...prev, botMsg]);

      // If timetable was created or adjusted, refresh timetable
      if (res.action_type.includes('timetable') || res.action_type.includes('task')) {
        fetchTasks();
      }

      // Speak response if voice or speech is enabled
      if (speechEnabled) {
        speakText(res.speech_text || res.reply);
      }
    } catch (e: any) {
      const errorMsg: ChatMessage = {
        role: 'assistant',
        content: `Error communicating with MAX: ${e.message || 'Please check if backend is running.'}`
      };
      setMessages((prev) => [...prev, errorMsg]);
    }
  };

  const handleClearChat = async () => {
    try {
      await api.clearChatHistory();
      setMessages([]);
    } catch (e) {
      console.error(e);
    }
  };

  const handleEmergencyStop = async () => {
    try {
      await api.emergencyStop();
      stopSpeaking();
      fetchProductivity();
      alert("EMERGENCY STOP EXECUTED: All monitoring, camera access, and active processes have been stopped immediately.");
    } catch (e) {
      console.error(e);
    }
  };

  const handleAnswerCheckIn = async (working: boolean, reason?: string, adjust = false) => {
    try {
      await api.answerCheckIn(working, reason, adjust);
      setCheckIn(null);
      fetchTasks();
      fetchProductivity();
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      {/* Top Navigation & Executive Header */}
      <Header
        currentTab={currentTab}
        setCurrentTab={setCurrentTab}
        openSettings={() => setIsSettingsOpen(true)}
        productivityStatus={productivityStatus}
        onEmergencyStop={handleEmergencyStop}
        speechEnabled={speechEnabled}
        setSpeechEnabled={setSpeechEnabled}
      />

      {/* Main View Container */}
      <main className="flex-1 p-4 md:p-6 overflow-y-auto">
        {currentTab === 'dashboard' && (
          <DashboardView
            tasks={tasks}
            productivityStatus={productivityStatus}
            checkIn={checkIn}
            onRefreshTasks={fetchTasks}
            onOpenTab={setCurrentTab}
            onSendMessage={handleSendMessage}
            onAnswerCheckIn={handleAnswerCheckIn}
          />
        )}

        {currentTab === 'chat' && (
          <ChatView
            messages={messages}
            onSendMessage={handleSendMessage}
            onClearChat={handleClearChat}
            speechEnabled={speechEnabled}
            setSpeechEnabled={setSpeechEnabled}
            isSpeaking={isSpeaking}
            onStopSpeaking={stopSpeaking}
            onSpeakText={speakText}
          />
        )}

        {currentTab === 'timetable' && (
          <TimetableView
            tasks={tasks}
            onRefreshTasks={fetchTasks}
          />
        )}

        {currentTab === 'productivity' && (
          <ProductivityView
            status={productivityStatus}
            checkIn={checkIn}
            onRefreshStatus={fetchProductivity}
            onEmergencyStop={handleEmergencyStop}
            onAnswerCheckIn={handleAnswerCheckIn}
          />
        )}

        {currentTab === 'teacher' && (
          <TeacherView />
        )}

        {currentTab === 'memory' && (
          <MemoryView />
        )}
      </main>

      {/* Settings Modal */}
      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
      />
    </div>
  );
};

