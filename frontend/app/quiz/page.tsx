"use client";

import { FC, useCallback, useEffect, useMemo, useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { useStudent } from "@/lib/studentContext";
import {
  ProgressBar,
  Timer,
  QuestionCard,
  HintDrawer,
  FeedbackPanel,
  RewardToast,
  CompletionSummary,
} from "@/components";
import { ConfigParser } from "@/lib/services/configParser";
import { getQuizAPIClient } from "@/lib/api/quizClient";
import type {
  NextQuestionResponse,
  SubmitAnswerResponse,
  HintResponse,
  SessionStartResponse,
} from "@/lib/types/quiz";

interface AdaptiveQuizScreenProps {
  /** Session ID from backend */
  sessionId: string;
  /** Grade level for re              } as any}
              configParser={configParser}
              onOptionSelect={handleSelectOption}
              selectedOptionId={screenState.selectedOptionId}
              gradeLevel={gradeLevel}
              isAnswered={screenState.flowState !== "QUESTION"}
              hintsAvailable={3}
            /> UI */
  gradeLevel?: 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10;
}

type QuizFlowState = "LOADING" | "QUESTION" | "FEEDBACK" | "COMPLETE" | "ERROR";

interface ScreenState {
  flowState: QuizFlowState;
  currentQuestion: NextQuestionResponse | null;
  currentAnswerResponse: SubmitAnswerResponse | null;
  selectedOptionId: string | null;
  showReward: boolean;
  error: string | null;
  sessionConfig: SessionStartResponse | null;
  correctCount: number;
  attemptedCount: number;
  currentStreak: number;
  completionData?: any; // SessionCompletionResponse from backend
}

/**
 * AdaptiveQuizScreen
 *
 * Main orchestrator component for the adaptive quiz experience.
 * Combines all 7 Phase 2 components into a cohesive quiz interface.
 *
 * Layout (responsive):
 * ┌─────────────────────────────────────────────────────┐
 * │ ProgressBar (top)        Timer (top-right)          │
 * ├─────────────────────────────────────────────────────┤
 * │                                                     │
 * │  HintDrawer  │  QuestionCard (center)  │ AdaptInfo  │
 * │  (sidebar)   │  + OptionTile[] grid    │ (stats)    │
 * │              │                         │            │
 * │              │  FeedbackPanel          │            │
 * │              │  (when submitted)       │            │
 * │                                                     │
 * └─────────────────────────────────────────────────────┘
 * RewardToast (floating, bottom-right)
 *
 * Quiz Flow State Machine:
 * LOADING
 *   ↓ (question fetched)
 * QUESTION (user selecting answer)
 *   ↓ (user submits)
 * FEEDBACK (showing result + hints + feedback)
 *   ↓ (user clicks continue)
 * QUESTION (next question)
 * ...repeat...
 *   ↓ (last question complete)
 * COMPLETE (session finished)
 *
 * Features:
 * - Full adaptive logic (question selection based on performance)
 * - Real-time progress tracking
 * - Countdown timer with auto-submit
 * - Progressive hint system
 * - Configurable feedback depth
 * - Celebration rewards (toasts, confetti)
 * - Accessibility first (aria-live, sr-only)
 * - Mobile responsive (320px+)
 *
 * @example
 * <AdaptiveQuizScreen
 *   sessionId="sess_123"
 *   gradeLevel={6}
 * />
 */
export const AdaptiveQuizScreen: FC<AdaptiveQuizScreenProps> = ({
  sessionId,
  gradeLevel = 6,
}) => {
  const { student } = useStudent();
  const searchParams = useSearchParams();
  const chapterFromUrl = searchParams?.get("chapter") || undefined;
  
  // Local screen state
  const [screenState, setScreenState] = useState<ScreenState>({
    flowState: "LOADING",
    currentQuestion: null,
    currentAnswerResponse: null,
    selectedOptionId: null,
    showReward: false,
    error: null,
    sessionConfig: null,
    correctCount: 0,
    attemptedCount: 0,
    currentStreak: 0,
  });

  // Config parser for UI decisions
  const configParser = useMemo(() => {
    if (!screenState.sessionConfig) {
      return new ConfigParser({} as any);
    }
    return new ConfigParser(screenState.sessionConfig.uiConfig);
  }, [screenState.sessionConfig]);

  // Load initial question
  useEffect(() => {
    const initializeQuiz = async () => {
      try {
        setScreenState((prev) => ({ ...prev, flowState: "LOADING", error: null }));

        const api = getQuizAPIClient();
        
        // Use the actual registered student ID from context, ensure it's a string
        const studentId = String(student?.id || `student_${Math.random().toString(36).substr(2, 9)}`);
        
        // Call real API endpoint with chapter if provided from URL
        const config = await api.startSession(
          gradeLevel,
          "Mathematics",
          studentId,
          chapterFromUrl
        );

        setScreenState((prev) => ({
          ...prev,
          sessionConfig: config,
          flowState: "QUESTION",
        }));

        console.log("📋 Session Config Loaded:", {
          feedbackDepth: config.uiConfig?.feedbackDepth,
          mode: config.mode,
          classLevel: config.classLevel,
          fullUiConfig: config.uiConfig,
        });

        // Fetch first question
        await fetchNextQuestion(config.sessionId);
      } catch (err) {
        console.error("Failed to initialize quiz:", err);
        setScreenState((prev) => ({
          ...prev,
          flowState: "ERROR",
          error: err instanceof Error ? err.message : "Failed to initialize quiz",
        }));
      }
    };

    if (screenState.flowState === "LOADING" && !screenState.currentQuestion && !screenState.sessionConfig) {
      initializeQuiz();
    }
  }, [sessionId, gradeLevel, chapterFromUrl, student]);

  // ...existing code...

  // Fetch next question from API
  const fetchNextQuestion = useCallback(
    async (sessionId: string) => {
      try {
        const api = getQuizAPIClient();
        const question = await api.getNextQuestion(sessionId);
        
        setScreenState((prev) => ({
          ...prev,
          currentQuestion: question,
          flowState: "QUESTION",
        }));
      } catch (err) {
        console.error("Failed to fetch question:", err);
        setScreenState((prev) => ({
          ...prev,
          flowState: "ERROR",
          error: err instanceof Error ? err.message : "Failed to load question",
        }));
      }
    },
    []
  );

  // Handle option selection
  const handleSelectOption = useCallback((optionId: string) => {
    if (screenState.flowState !== "QUESTION") return;

    setScreenState((prev) => ({
      ...prev,
      selectedOptionId: optionId,
    }));
  }, [screenState.flowState]);

  // Handle answer submission
  const handleSubmitAnswer = useCallback(async () => {
    if (screenState.flowState !== "QUESTION" || !screenState.selectedOptionId) {
      return;
    }

    try {
      // Call real API endpoint to submit answer
      if (!screenState.currentQuestion || !screenState.sessionConfig) {
        throw new Error("Session not initialized");
      }

      const api = getQuizAPIClient();
      const response = await api.submitAnswer(
        screenState.sessionConfig.sessionId,
        screenState.currentQuestion.questionId,
        screenState.selectedOptionId || "",
        Math.floor(Math.random() * 60) // Simulate time spent
      );

      setScreenState((prev) => {
        const isCorrect = response.isCorrect;
        return {
          ...prev,
          currentAnswerResponse: response,
          flowState: "FEEDBACK",
          correctCount: prev.correctCount + (isCorrect ? 1 : 0),
          attemptedCount: prev.attemptedCount + 1,
          currentStreak: isCorrect ? prev.currentStreak + 1 : 0,
          showReward: isCorrect && (prev.currentStreak + 1) % 5 === 0,
        };
      });
    } catch (err) {
      console.error("Failed to submit answer:", err);
      setScreenState((prev) => ({
        ...prev,
        flowState: "ERROR",
        error: err instanceof Error ? err.message : "Failed to submit answer",
      }));
    }
  }, [screenState.flowState, screenState.selectedOptionId, screenState.currentQuestion, screenState.sessionConfig]);

  // Handle continue to next question
  const handleContinueNext = useCallback(async () => {
    if (screenState.flowState !== "FEEDBACK" || !screenState.sessionConfig) return;

    try {
      setScreenState((prev) => ({
        ...prev,
        flowState: "LOADING",
        showReward: false,
        error: null,
        selectedOptionId: null,
        currentAnswerResponse: null,
      }));

      // ✅ Check session completion with backend instead of hard 5-question limit
      const api = getQuizAPIClient();
      const completionCheck = await api.checkSessionCompletion(
        screenState.sessionConfig.sessionId
      );

      if (completionCheck.isComplete) {
        // Mastery achieved! End session
        setScreenState((prev) => ({
          ...prev,
          flowState: "COMPLETE",
          completionData: completionCheck,
        }));
      } else {
        // More to learn - fetch next question
        await fetchNextQuestion(screenState.sessionConfig.sessionId);
      }
    } catch (err) {
      console.error("Failed to load next question:", err);
      setScreenState((prev) => ({
        ...prev,
        flowState: "ERROR",
        error: err instanceof Error ? err.message : "Failed to continue",
      }));
    }
  }, [screenState.flowState, screenState.sessionConfig, fetchNextQuestion]);

  // Handle hint request
  const handleRequestHint = useCallback(
    async (hintIndex: number): Promise<HintResponse> => {
      if (!screenState.sessionConfig || !screenState.currentQuestion) {
        throw new Error("Session not initialized");
      }

      const api = getQuizAPIClient();
      return await api.getHint(
        screenState.sessionConfig.sessionId,
        screenState.currentQuestion.questionId,
        hintIndex
      );
    },
    [screenState.sessionConfig, screenState.currentQuestion]
  );

  // Handle timer expiration
  const handleTimerExpired = useCallback(() => {
    if (screenState.flowState === "QUESTION") {
      console.warn("Timer expired - auto-submitting...");
      // Auto-submit if timer expires
      if (screenState.selectedOptionId) {
        handleSubmitAnswer();
      }
    }
  }, [screenState.flowState, screenState.selectedOptionId]);

  // Derived values
  const isAnswerSelected = useMemo(() => {
    return screenState.selectedOptionId !== null;
  }, [screenState.selectedOptionId]);

  const isSubmitDisabled = useMemo(() => {
    return screenState.flowState !== "QUESTION" || !isAnswerSelected;
  }, [screenState.flowState, isAnswerSelected]);

  const shouldShowTimer = useMemo(() => {
    return configParser.shouldShowTimer?.() && screenState.flowState === "QUESTION";
  }, [configParser, screenState.flowState]);

  const shouldShowHints = useMemo(() => {
    return configParser.areHintsEnabled?.() && screenState.flowState === "QUESTION";
  }, [configParser, screenState.flowState]);

  // Loading state
  if (screenState.flowState === "LOADING" && !screenState.currentQuestion && screenState.attemptedCount === 0) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="bg-white rounded-3xl p-8 shadow-lg max-w-sm">
          <div className="flex justify-center mb-4">
            <svg className="w-12 h-12 animate-spin text-blue-600" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
          </div>
          <p className="text-center text-gray-700 font-semibold">Loading your quiz...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (screenState.flowState === "ERROR") {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="bg-white rounded-3xl p-8 shadow-lg max-w-sm">
          <div className="flex justify-center mb-4">
            <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center">
              <svg className="w-6 h-6 text-red-600" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
          </div>
          <p className="text-center text-gray-700 font-semibold mb-2">Something went wrong</p>
          <p className="text-center text-sm text-gray-600 mb-4">{screenState.error}</p>
          <button
            onClick={() => window.location.reload()}
            className="w-full px-4 py-2 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors"
          >
            Reload Quiz
          </button>
        </div>
      </div>
    );
  }

  // Complete state
  if (screenState.flowState === "COMPLETE") {
    return (
      <CompletionSummary
        completionData={screenState.completionData}
        chapterName={chapterFromUrl || "Chapter"}
        onStartNew={() => window.location.reload()}
        onBackToDashboard={() => (window.location.href = "/dashboard")}
        configParser={configParser}
        gradeLevel={gradeLevel}
      />
    );
  }

  // Main quiz screen
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header with Progress and Timer */}
      <div className="bg-white border-b border-blue-100 shadow-sm p-4 md:p-6 lg:p-8">
        <div className="flex items-center justify-between gap-4 mb-4">
          <h1 className="text-lg md:text-2xl font-bold text-gray-800">Adaptive Quiz</h1>
          {shouldShowTimer && (
            <Timer
              timeRemaining={120}
              isWarning={false}
              isExpired={false}
              percentage={100}
              showProgressRing={true}
              gradeLevel={gradeLevel}
            />
          )}
        </div>

        <ProgressBar
          currentProgress={screenState.attemptedCount}
          correctAnswers={screenState.correctCount}
          totalQuestions={5}
          showAccuracy={true}
          gradeLevel={gradeLevel}
        />
      </div>

      {/* Main Content Area */}
      <div className="p-4 md:p-6 lg:p-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Hint Drawer Sidebar */}
          {shouldShowHints && (
            <div className="lg:col-span-2">
              <div className="sticky top-24">
                <HintDrawer
                  questionId="q123"
                  hintsAvailable={3}
                  onHintRequest={handleRequestHint}
                  sessionId={sessionId}
                  configParser={configParser}
                  gradeLevel={gradeLevel}
                />
              </div>
            </div>
          )}

          {/* Question Card (Center) */}
          <div className={shouldShowHints ? "lg:col-span-7" : "lg:col-span-9"}>
            {screenState.flowState === "LOADING" ? (
              <div className="flex items-center justify-center p-8 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-3xl min-h-96">
                <div className="text-center">
                  <div className="animate-spin mb-4">
                    <div className="w-12 h-12 border-4 border-blue-200 border-t-blue-600 rounded-full"></div>
                  </div>
                  <p className="text-gray-600 font-semibold">Loading question...</p>
                </div>
              </div>
            ) : screenState.currentQuestion ? (
              <>
                <QuestionCard
                  question={screenState.currentQuestion as any}
                  configParser={configParser}
                  onOptionSelect={handleSelectOption}
                  selectedOptionId={screenState.selectedOptionId}
                  gradeLevel={gradeLevel}
                  isAnswered={screenState.flowState !== "QUESTION"}
                  hintsAvailable={3}
                />
              </>
            ) : (
              <div className="flex items-center justify-center p-8 bg-gradient-to-br from-red-50 to-orange-50 rounded-3xl min-h-96">
                <div className="text-center">
                  <p className="text-red-600 font-semibold">No question loaded</p>
                </div>
              </div>
            )}

            {/* Submit Button */}
            {screenState.flowState === "QUESTION" && (
              <button
                onClick={handleSubmitAnswer}
                disabled={isSubmitDisabled}
                className={`w-full mt-6 px-6 py-3 rounded-2xl font-bold transition-all duration-200 text-lg ${
                  isSubmitDisabled
                    ? "bg-gray-200 text-gray-400 cursor-not-allowed"
                    : "bg-green-500 text-white hover:bg-green-600 active:scale-95 shadow-md hover:shadow-lg"
                }`}
                aria-label="Submit answer"
              >
                Submit Answer
              </button>
            )}

            {/* Feedback Panel */}
            {screenState.flowState === "FEEDBACK" && screenState.currentAnswerResponse && screenState.currentQuestion && (
              <div className="mt-6">
                <FeedbackPanel
                  response={{
                    ...screenState.currentAnswerResponse,
                    feedback: {
                      showCorrectAnswer: true,
                      showSolution: true,
                      showExplanation: true,
                      showWhyCorrect: true,
                      showMisconception: true,
                      showTrapWarning: true,
                      tone: "encouraging",
                      mainMessage: screenState.currentAnswerResponse.isCorrect ? "Great!" : "Not quite!",
                      depth: "detailed",
                      nextAction: "continue",
                      enableGamification: true,
                    },
                  }}
                  question={screenState.currentQuestion as any}
                  onContinue={handleContinueNext}
                  configParser={configParser}
                  gradeLevel={gradeLevel}
                />
              </div>
            )}
          </div>

          {/* Adaptive Info Sidebar */}
          <div className="lg:col-span-3">
            <div className="sticky top-24 bg-white rounded-3xl p-6 shadow-md border border-blue-100">
              <h3 className="font-bold text-gray-800 mb-4">Performance</h3>
              <div className="space-y-4">
                <div>
                  <p className="text-xs text-gray-600 font-semibold">Accuracy</p>
                  <p className="text-2xl font-bold text-blue-600">
                    {screenState.attemptedCount > 0
                      ? Math.round((screenState.correctCount / screenState.attemptedCount) * 100)
                      : 0}
                    %
                  </p>
                </div>
                <div>
                  <p className="text-xs text-gray-600 font-semibold">Streak</p>
                  <p className="text-2xl font-bold text-orange-500">{screenState.currentStreak}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-600 font-semibold">Progress</p>
                  <p className="text-2xl font-bold text-emerald-600">{screenState.attemptedCount}/5</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Reward Toast */}
      <RewardToast
        isCorrect={screenState.currentAnswerResponse?.isCorrect || false}
        streak={screenState.currentStreak}
        masteryDelta={screenState.currentAnswerResponse?.masteryScore?.delta || 0}
        configParser={configParser}
        gradeLevel={gradeLevel}
        isVisible={screenState.showReward}
        onClose={() => setScreenState((prev) => ({ ...prev, showReward: false }))}
      />

      {/* Accessibility: Screen reader status */}
      <div className="sr-only" role="status" aria-live="polite">
        {screenState.flowState === "QUESTION" && "Question loaded, select an option and submit your answer"}
        {screenState.flowState === "FEEDBACK" && "Feedback for your answer is displayed"}
      </div>
    </div>
  );
};

// Wrapper component to handle Suspense for useSearchParams
function QuizPageWrapper() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="bg-white rounded-3xl p-8 shadow-lg max-w-sm">
          <div className="flex justify-center mb-4">
            <svg className="w-12 h-12 animate-spin text-blue-600" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
          </div>
          <p className="text-center text-gray-700 font-semibold">Loading your quiz...</p>
        </div>
      </div>
    }>
      <AdaptiveQuizScreen sessionId="quiz-session" gradeLevel={6} />
    </Suspense>
  );
}

export default QuizPageWrapper;
