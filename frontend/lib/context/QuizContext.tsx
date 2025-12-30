/**
 * Quiz Context Provider
 * 
 * Centralized state management for the entire quiz session
 * All components subscribe to state from here
 */

"use client";

import React, { createContext, useContext, useState, useCallback, ReactNode } from "react";
import {
  QuizSessionState,
  SessionStartResponse,
  NextQuestionResponse,
  SubmitAnswerResponse,
  HintResponse,
  QuizEvent,
} from "@/lib/types/quiz";

interface QuizContextType {
  // State
  state: QuizSessionState;

  // Session Management
  initializeSession: (config: SessionStartResponse) => void;
  setCurrentQuestion: (question: NextQuestionResponse) => void;

  // Answer Interaction
  selectAnswer: (answerId: string) => void;
  deselectAnswer: () => void;
  submitAnswer: (response: SubmitAnswerResponse) => void;

  // Hint Interaction
  requestHint: () => void;
  hintUsed: (response: HintResponse) => void;

  // Navigation
  continueToNextQuestion: () => void;
  resetQuestion: () => void;
  endSession: (finalScore: number) => void;

  // Utilities
  isAnswerSelected: boolean;
  canSubmit: boolean;
  getProgress: () => number; // 0-100
  getScore: () => number; // correct / attempted
  resetQuiz: () => void;
  
  // Event emission
  emitEvent: (event: QuizEvent) => void;
}

const QuizContext = createContext<QuizContextType | undefined>(undefined);

const initialState: QuizSessionState = {
  sessionId: "",
  mode: "PRACTICE",
  classLevel: "6-8",
  uiConfig: {
    theme: "light",
    animationIntensity: "medium",
    fontSize: "medium",
    enableHints: true,
    enableTimer: false,
    enableDifficultyBadge: true,
    enableMasteryDisplay: true,
    enableStreak: true,
    enableAccuracy: true,
    enableConfetti: true,
    enableSound: false,
    enableHapticFeedback: false,
    hintCount: 3,
    hintRevealMode: "progressive",
    showTimer: false,
    feedbackDepth: "moderate",
    questionCount: undefined,
    showQuestionCounter: true,
  },
  currentQuestion: null,
  selectedAnswerId: null,
  isSubmitted: false,
  student: {
    id: "",
    name: "",
    streak: 0,
    masteryScore: 0,
    recentAccuracy: 0,
    learningMomentum: "low",
    totalQuestionsAttempted: 0,
  },
  questionsAttempted: 0,
  correctCount: 0,
  incorrectCount: 0,
  showFeedback: false,
  showHintDrawer: false,
  usedHintCount: 0,
  isLoading: false,
  error: null,
};

export function QuizProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<QuizSessionState>(initialState);
  const [eventCallbacks, setEventCallbacks] = useState<((event: QuizEvent) => void)[]>([]);

  // Session Management
  const initializeSession = useCallback((config: SessionStartResponse) => {
    setState((prev) => ({
      ...prev,
      sessionId: config.sessionId,
      mode: config.mode,
      classLevel: config.classLevel,
      uiConfig: config.uiConfig,
      student: config.student,
    }));
    
    emitEvent({
      type: "SESSION_START",
      sessionId: config.sessionId,
      timestamp: Date.now(),
    });
  }, []);

  const setCurrentQuestion = useCallback((question: NextQuestionResponse) => {
    setState((prev) => ({
      ...prev,
      currentQuestion: question,
      selectedAnswerId: null,
      isSubmitted: false,
      showFeedback: false,
      usedHintCount: 0,
    }));

    emitEvent({
      type: "QUESTION_LOADED",
      sessionId: state.sessionId,
      timestamp: Date.now(),
      questionId: question.questionId,
    });
  }, [state.sessionId]);

  // Answer Interaction
  const selectAnswer = useCallback((answerId: string) => {
    setState((prev) => ({
      ...prev,
      selectedAnswerId: answerId,
    }));

    emitEvent({
      type: "ANSWER_SELECTED",
      sessionId: state.sessionId,
      timestamp: Date.now(),
      questionId: state.currentQuestion?.questionId,
    });
  }, [state.sessionId, state.currentQuestion?.questionId]);

  const deselectAnswer = useCallback(() => {
    setState((prev) => ({
      ...prev,
      selectedAnswerId: null,
    }));
  }, []);

  const submitAnswer = useCallback((response: SubmitAnswerResponse) => {
    setState((prev) => ({
      ...prev,
      isSubmitted: true,
      showFeedback: true,
      correctCount: response.isCorrect ? prev.correctCount + 1 : prev.correctCount,
      incorrectCount: !response.isCorrect ? prev.incorrectCount + 1 : prev.incorrectCount,
      questionsAttempted: prev.questionsAttempted + 1,
      student: {
        ...prev.student,
        streak: response.streakUpdate?.current ?? prev.student.streak,
        masteryScore: response.masteryScore.current,
      },
    }));

    emitEvent({
      type: "ANSWER_SUBMITTED",
      sessionId: state.sessionId,
      timestamp: Date.now(),
      questionId: state.currentQuestion?.questionId,
      data: {
        isCorrect: response.isCorrect,
        attemptNumber: response.attemptNumber,
        timeSpent: response.timeSpent,
      },
    });

    if (response.misconceptionDetected) {
      emitEvent({
        type: "MISCONCEPTION_DETECTED",
        sessionId: state.sessionId,
        timestamp: Date.now(),
        questionId: state.currentQuestion?.questionId,
        data: response.misconceptionDetected,
      });
    }

    if (response.logicalTrapTriggered) {
      emitEvent({
        type: "TRAP_TRIGGERED",
        sessionId: state.sessionId,
        timestamp: Date.now(),
        questionId: state.currentQuestion?.questionId,
      });
    }

    if (response.motivationTrigger) {
      emitEvent({
        type: "MILESTONE_REACHED",
        sessionId: state.sessionId,
        timestamp: Date.now(),
        data: response.motivationTrigger,
      });
    }
  }, [state.sessionId, state.currentQuestion?.questionId]);

  // Hint Interaction
  const requestHint = useCallback(() => {
    setState((prev) => ({
      ...prev,
      showHintDrawer: true,
    }));

    emitEvent({
      type: "HINT_REQUESTED",
      sessionId: state.sessionId,
      timestamp: Date.now(),
      questionId: state.currentQuestion?.questionId,
    });
  }, [state.sessionId, state.currentQuestion?.questionId]);

  const hintUsed = useCallback((response: HintResponse) => {
    setState((prev) => ({
      ...prev,
      usedHintCount: prev.usedHintCount + 1,
    }));

    emitEvent({
      type: "HINT_CONSUMED",
      sessionId: state.sessionId,
      timestamp: Date.now(),
      questionId: state.currentQuestion?.questionId,
      data: { hintType: response.hintType },
    });
  }, [state.sessionId, state.currentQuestion?.questionId]);

  // Navigation
  const continueToNextQuestion = useCallback(() => {
    setState((prev) => ({
      ...prev,
      selectedAnswerId: null,
      isSubmitted: false,
      showFeedback: false,
      showHintDrawer: false,
      currentQuestion: null,
    }));
  }, []);

  const resetQuestion = useCallback(() => {
    setState((prev) => ({
      ...prev,
      selectedAnswerId: null,
      isSubmitted: false,
      showFeedback: false,
      usedHintCount: 0,
    }));
  }, []);

  const endSession = useCallback((finalScore: number) => {
    emitEvent({
      type: "SESSION_END",
      sessionId: state.sessionId,
      timestamp: Date.now(),
      data: { finalScore },
    });

    setState((prev) => ({
      ...prev,
      currentQuestion: null,
      selectedAnswerId: null,
      isSubmitted: false,
    }));
  }, [state.sessionId]);

  // Utilities
  const isAnswerSelected = state.selectedAnswerId !== null;
  const canSubmit = isAnswerSelected && !state.isSubmitted;
  
  const getProgress = (): number => {
    if (state.questionsAttempted === 0) return 0;
    const config = state.uiConfig;
    const total = config.questionCount ?? 20; // default
    return Math.min((state.questionsAttempted / total) * 100, 100);
  };

  const getScore = (): number => {
    if (state.questionsAttempted === 0) return 0;
    return (state.correctCount / state.questionsAttempted) * 100;
  };

  const resetQuiz = useCallback(() => {
    setState(initialState);
  }, []);

  const emitEvent = useCallback((event: QuizEvent) => {
    eventCallbacks.forEach((cb) => cb(event));
  }, [eventCallbacks]);

  const value: QuizContextType = {
    state,
    initializeSession,
    setCurrentQuestion,
    selectAnswer,
    deselectAnswer,
    submitAnswer,
    requestHint,
    hintUsed,
    continueToNextQuestion,
    resetQuestion,
    endSession,
    isAnswerSelected,
    canSubmit,
    getProgress,
    getScore,
    resetQuiz,
    emitEvent,
  };

  return (
    <QuizContext.Provider value={value}>
      {children}
    </QuizContext.Provider>
  );
}

/**
 * Hook to use Quiz context
 */
export function useQuiz(): QuizContextType {
  const context = useContext(QuizContext);
  if (!context) {
    throw new Error("useQuiz must be used within QuizProvider");
  }
  return context;
}

/**
 * Hook to subscribe to quiz events
 */
export function useQuizEvents(callback: (event: QuizEvent) => void) {
  const { state } = useQuiz();

  React.useEffect(() => {
    // Register callback with context
    // Note: This is a simplified version; in production, you'd want
    // to register/unregister callbacks properly
  }, [callback]);
}
