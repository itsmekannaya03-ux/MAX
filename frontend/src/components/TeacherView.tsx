import React, { useState } from 'react';
import { 
  GraduationCap, Sparkles, BookOpen, CheckCircle2, 
  HelpCircle, ArrowRight, Award, RotateCcw, Lightbulb
} from 'lucide-react';
import { LessonExplainResponse, QuizResponse, QuizResultResponse } from '../types';
import { api } from '../api/client';

export const TeacherView: React.FC = () => {
  const [topic, setTopic] = useState('');
  const [level, setLevel] = useState('beginner');
  const [isLoading, setIsLoading] = useState(false);
  const [lesson, setLesson] = useState<LessonExplainResponse | null>(null);

  // Quiz state
  const [quiz, setQuiz] = useState<QuizResponse | null>(null);
  const [selectedAnswers, setSelectedAnswers] = useState<number[]>([]);
  const [quizResult, setQuizResult] = useState<QuizResultResponse | null>(null);
  const [quizLoading, setQuizLoading] = useState(false);

  const handleExplain = async (customTopic?: string) => {
    const targetTopic = customTopic || topic;
    if (!targetTopic.trim()) return;
    setIsLoading(true);
    setQuiz(null);
    setQuizResult(null);
    try {
      const res = await api.explainTopic(targetTopic.trim(), level);
      setLesson(res);
      setTopic(targetTopic);
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  const handleStartQuiz = async () => {
    if (!lesson) return;
    setQuizLoading(true);
    setQuizResult(null);
    try {
      const res = await api.generateQuiz(lesson.topic, 3, level);
      setQuiz(res);
      setSelectedAnswers(new Array(res.questions.length).fill(-1));
    } catch (e) {
      console.error(e);
    } finally {
      setQuizLoading(false);
    }
  };

  const handleSelectOption = (questionIdx: number, optionIdx: number) => {
    const updated = [...selectedAnswers];
    updated[questionIdx] = optionIdx;
    setSelectedAnswers(updated);
  };

  const handleSubmitQuiz = async () => {
    if (!quiz) return;
    try {
      const res = await api.submitQuiz(quiz.session_id, selectedAnswers);
      setQuizResult(res);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto pb-12">
      {/* Header */}
      <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 shadow-xl">
        <div className="flex items-center gap-2">
          <GraduationCap className="w-5 h-5 text-brand-400" />
          <h2 className="text-xl font-bold text-white tracking-tight">MAX AI Personal Teacher</h2>
        </div>
        <p className="text-xs text-slate-400 mt-1">
          Patient, step-by-step concept explanations powered by real-world everyday analogies and interactive quizzes.
        </p>

        {/* Input Bar */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleExplain();
          }}
          className="mt-4 flex flex-col sm:flex-row gap-2"
        >
          <input
            type="text"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="Ask MAX to teach any topic: 'Python OOP', 'Binary Search', 'Photosynthesis'..."
            className="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-brand-500 font-medium transition-colors"
          />
          <select
            value={level}
            onChange={(e) => setLevel(e.target.value)}
            className="bg-slate-950 border border-slate-800 rounded-xl px-3 py-2.5 text-xs text-slate-300 focus:outline-none focus:border-brand-500"
          >
            <option value="beginner">Beginner</option>
            <option value="intermediate">Intermediate</option>
            <option value="advanced">Advanced</option>
          </select>
          <button
            type="submit"
            disabled={isLoading || !topic.trim()}
            className="px-5 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-500 disabled:opacity-40 text-white text-xs font-semibold shadow-md shadow-brand-500/20 transition-all shrink-0"
          >
            {isLoading ? 'Teaching...' : 'Explain Topic'}
          </button>
        </form>

        {/* Quick Suggestion Chips */}
        <div className="mt-3 flex flex-wrap items-center gap-2">
          <span className="text-[11px] text-slate-500">Try asking:</span>
          {['Binary Search', 'Python Decorators', 'Neural Networks', 'Newton Laws of Motion'].map((chip) => (
            <button
              key={chip}
              onClick={() => handleExplain(chip)}
              className="text-[11px] px-2.5 py-1 rounded-lg bg-slate-800/80 hover:bg-slate-800 text-slate-300 hover:text-white border border-slate-700 transition-colors"
            >
              {chip}
            </button>
          ))}
        </div>
      </div>

      {/* Lesson Viewer */}
      {lesson && (
        <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 shadow-xl space-y-5 animate-in fade-in duration-300">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <div>
              <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-brand-500/10 text-brand-400 border border-brand-500/20">
                {lesson.level} LEVEL
              </span>
              <h3 className="text-2xl font-bold text-white mt-1">{lesson.topic}</h3>
            </div>
            <button
              onClick={handleStartQuiz}
              disabled={quizLoading}
              className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-md shadow-indigo-500/20 transition-all"
            >
              <HelpCircle className="w-3.5 h-3.5" />
              <span>{quizLoading ? 'Generating...' : 'Take Quiz'}</span>
            </button>
          </div>

          {/* Everyday Analogy */}
          <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-200">
            <div className="flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-amber-400 mb-1">
              <Lightbulb className="w-4 h-4 text-amber-400" />
              <span>Everyday Real-World Analogy</span>
            </div>
            <p className="text-xs leading-relaxed text-amber-100">{lesson.everyday_analogy}</p>
          </div>

          {/* Concept Summary */}
          <div>
            <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-1">The Core Idea</h4>
            <p className="text-xs text-slate-300 leading-relaxed">{lesson.concept_summary}</p>
          </div>

          {/* Step-by-Step Breakdown */}
          <div>
            <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">Step-by-Step Breakdown</h4>
            <div className="space-y-2">
              {lesson.breakdown_steps.map((step, idx) => (
                <div key={idx} className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-200 flex items-start gap-2.5">
                  <span className="w-5 h-5 rounded-md bg-brand-500/20 text-brand-400 flex items-center justify-center font-bold text-[10px] shrink-0">
                    {idx + 1}
                  </span>
                  <span>{step}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Practical Code or Example */}
          <div>
            <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">Practical Example / Code</h4>
            <pre className="p-4 rounded-xl bg-slate-950 border border-slate-800 text-xs font-mono text-emerald-400 overflow-x-auto whitespace-pre-wrap">
              {lesson.practical_code_or_example}
            </pre>
          </div>

          {/* Quick Check Question */}
          <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 text-xs text-slate-300">
            <span className="font-bold text-brand-400">Comprehension Check:</span> {lesson.comprehension_check}
          </div>
        </div>
      )}

      {/* Interactive Quiz Runner */}
      {quiz && (
        <div className="p-6 rounded-2xl bg-slate-900 border border-indigo-500/30 shadow-2xl space-y-6">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <div className="flex items-center gap-2">
              <Award className="w-5 h-5 text-indigo-400" />
              <h3 className="text-lg font-bold text-white">Quiz: {quiz.topic}</h3>
            </div>
            {quizResult && (
              <span className="px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-bold text-xs">
                Score: {quizResult.score} / {quizResult.total} ({quizResult.percentage}%)
              </span>
            )}
          </div>

          {quizResult && (
            <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-200 text-xs">
              <span className="font-bold text-emerald-400">Feedback:</span> {quizResult.feedback}
            </div>
          )}

          <div className="space-y-5">
            {quiz.questions.map((q, qIdx) => (
              <div key={q.id} className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-3">
                <p className="text-xs font-semibold text-slate-100">
                  <span className="text-brand-400 font-bold mr-1">Q{qIdx + 1}.</span> {q.question}
                </p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {q.options.map((opt, optIdx) => {
                    const isSelected = selectedAnswers[qIdx] === optIdx;
                    return (
                      <button
                        key={optIdx}
                        disabled={!!quizResult}
                        onClick={() => handleSelectOption(qIdx, optIdx)}
                        className={`text-left p-2.5 rounded-lg text-xs font-medium border transition-all ${
                          isSelected
                            ? 'bg-brand-600 text-white border-brand-500 shadow-sm'
                            : 'bg-slate-900/60 hover:bg-slate-850 text-slate-300 border-slate-800'
                        }`}
                      >
                        <span className="font-bold mr-1.5 opacity-60">
                          {String.fromCharCode(65 + optIdx)}.
                        </span>
                        {opt}
                      </button>
                    );
                  })}
                </div>

                {/* Show explanation after grading */}
                {quizResult && quizResult.detailed_answers[qIdx] && (
                  <div className="mt-2 pt-2 border-t border-slate-800 text-[11px]">
                    <span className={quizResult.detailed_answers[qIdx].is_correct ? 'text-emerald-400 font-bold' : 'text-rose-400 font-bold'}>
                      {quizResult.detailed_answers[qIdx].is_correct ? '✓ Correct! ' : '✗ Incorrect. '}
                    </span>
                    <span className="text-slate-400">{quizResult.detailed_answers[qIdx].explanation}</span>
                  </div>
                )}
              </div>
            ))}
          </div>

          {!quizResult && (
            <div className="flex justify-end pt-2">
              <button
                onClick={handleSubmitQuiz}
                disabled={selectedAnswers.includes(-1)}
                className="px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 disabled:opacity-40 text-white text-xs font-bold shadow-md shadow-emerald-500/20 transition-all"
              >
                Submit Answers
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

