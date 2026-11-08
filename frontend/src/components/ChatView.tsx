import React, { useState, useEffect, useRef } from 'react';
import { 
  Send, Mic, MicOff, Volume2, VolumeX, Trash2, 
  Sparkles, Bot, User, CheckCircle2, BookOpen, Search, Calendar
} from 'lucide-react';
import { ChatMessage } from '../types';
import { api } from '../api/client';

interface ChatViewProps {
  messages: ChatMessage[];
  onSendMessage: (text: string, voice?: boolean) => void;
  onClearChat: () => void;
  speechEnabled: boolean;
  setSpeechEnabled: (val: boolean) => void;
  isSpeaking: boolean;
  onStopSpeaking: () => void;
  onSpeakText: (text: string) => void;
}

export const ChatView: React.FC<ChatViewProps> = ({
  messages,
  onSendMessage,
  onClearChat,
  speechEnabled,
  setSpeechEnabled,
  isSpeaking,
  onStopSpeaking,
  onSpeakText
}) => {
  const [inputText, setInputText] = useState('');
  const [isListening, setIsListening] = useState(false);
  const recognitionRef = useRef<any>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Initialize Speech Recognition if supported in browser
  useEffect(() => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = 'en-US';

      recognition.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        setInputText(transcript);
        setIsListening(false);
        // Automatically send voice query to MAX
        onSendMessage(transcript, true);
      };

      recognition.onerror = () => setIsListening(false);
      recognition.onend = () => setIsListening(false);
      recognitionRef.current = recognition;
    }
  }, [onSendMessage]);

  const toggleMic = () => {
    if (!recognitionRef.current) {
      alert("Speech recognition is supported natively in modern Chromium browsers. You can type commands directly!");
      return;
    }
    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    } else {
      if (isSpeaking) onStopSpeaking();
      recognitionRef.current.start();
      setIsListening(true);
    }
  };

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim()) return;
    if (isSpeaking) onStopSpeaking();
    onSendMessage(inputText.trim(), false);
    setInputText('');
  };

  return (
    <div className="flex flex-col h-[calc(100vh-140px)] max-w-4xl mx-auto rounded-2xl bg-slate-900 border border-slate-800 shadow-xl overflow-hidden">
      {/* Top Chat Bar */}
      <div className="px-5 py-3 border-b border-slate-800 bg-slate-900/60 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Bot className="w-4 h-4 text-brand-400" />
          <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider">MAX Intelligence Stream</h3>
        </div>
        <div className="flex items-center gap-2">
          {isSpeaking && (
            <button
              onClick={onStopSpeaking}
              className="flex items-center gap-1 px-2.5 py-1 rounded-lg bg-rose-500/20 text-rose-400 border border-rose-500/30 text-xs font-semibold animate-pulse"
            >
              <VolumeX className="w-3.5 h-3.5" />
              <span>Interrupt Speech</span>
            </button>
          )}
          <button
            onClick={() => setSpeechEnabled(!speechEnabled)}
            className={`p-1.5 rounded-lg border text-xs transition-colors ${
              speechEnabled ? 'bg-brand-500/10 border-brand-500/30 text-brand-400' : 'bg-slate-800 text-slate-400 border-slate-700'
            }`}
            title={speechEnabled ? "Mute Spoken Replies" : "Auto-Speak Replies"}
          >
            {speechEnabled ? <Volume2 className="w-3.5 h-3.5" /> : <VolumeX className="w-3.5 h-3.5" />}
          </button>
          <button
            onClick={onClearChat}
            className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-slate-200 border border-slate-700 text-xs transition-colors"
            title="Clear Chat History"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto p-5 space-y-4">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center p-6">
            <div className="w-12 h-12 rounded-2xl bg-brand-500/10 border border-brand-500/20 flex items-center justify-center mb-3">
              <Sparkles className="w-6 h-6 text-brand-400" />
            </div>
            <h4 className="text-base font-bold text-white">How can I assist you right now?</h4>
            <p className="text-xs text-slate-400 max-w-sm mt-1">
              Talk to MAX using voice or text. Try:
            </p>
            <div className="mt-4 flex flex-wrap justify-center gap-2 max-w-md">
              {[
                "Create my timetable for today",
                "What should I do right now?",
                "I completed my coding session",
                "Explain neural networks like I'm 10",
                "I need a 20-minute break"
              ].map((s) => (
                <button
                  key={s}
                  onClick={() => onSendMessage(s)}
                  className="px-3 py-1.5 rounded-xl bg-slate-800/80 hover:bg-slate-800 text-slate-300 hover:text-white border border-slate-700 text-xs transition-all"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((m, idx) => {
            const isBot = m.role === 'assistant';
            return (
              <div
                key={idx}
                className={`flex gap-3 ${isBot ? 'justify-start' : 'justify-end'}`}
              >
                {isBot && (
                  <div className="w-7 h-7 rounded-lg bg-gradient-to-tr from-brand-600 to-indigo-600 flex items-center justify-center text-white shrink-0 shadow-md">
                    <Bot className="w-4 h-4" />
                  </div>
                )}
                <div
                  className={`max-w-[80%] rounded-2xl p-4 text-xs leading-relaxed shadow-md ${
                    isBot
                      ? 'bg-slate-850 border border-slate-800 text-slate-200'
                      : 'bg-brand-600 text-white font-medium'
                  }`}
                >
                  <div className="whitespace-pre-wrap">{m.content}</div>

                  {/* Audio replay button for bot responses */}
                  {isBot && (
                    <div className="mt-2.5 pt-2 border-t border-slate-800/60 flex items-center justify-between text-[10px] text-slate-400">
                      <span>MAX Assistant</span>
                      <button
                        onClick={() => onSpeakText(m.content)}
                        className="hover:text-brand-400 flex items-center gap-1 transition-colors"
                        title="Speak this response"
                      >
                        <Volume2 className="w-3 h-3" />
                        <span>Speak</span>
                      </button>
                    </div>
                  )}
                </div>
                {!isBot && (
                  <div className="w-7 h-7 rounded-lg bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-300 shrink-0">
                    <User className="w-4 h-4" />
                  </div>
                )}
              </div>
            );
          })
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Bar */}
      <form onSubmit={handleSend} className="p-3 border-t border-slate-800 bg-slate-900/90 flex items-center gap-2">
        {/* Voice Microphone Toggle */}
        <button
          type="button"
          onClick={toggleMic}
          className={`p-2.5 rounded-xl transition-all shadow-md ${
            isListening
              ? 'bg-rose-600 text-white animate-pulse'
              : 'bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700'
          }`}
          title={isListening ? "Listening... click to stop" : "Speak to MAX"}
        >
          {isListening ? <Mic className="w-4 h-4" /> : <MicOff className="w-4 h-4" />}
        </button>

        <input
          type="text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder={isListening ? "Listening... speak now..." : "Type your command or question for MAX..."}
          className="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-brand-500 transition-colors"
        />

        <button
          type="submit"
          disabled={!inputText.trim()}
          className="p-2.5 rounded-xl bg-brand-600 hover:bg-brand-500 disabled:opacity-40 text-white transition-all shadow-md shadow-brand-500/20"
        >
          <Send className="w-4 h-4" />
        </button>
      </form>
    </div>
  );
};

