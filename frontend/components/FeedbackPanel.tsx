"use client";

import { FC, useCallback, useMemo } from "react";
import type { SubmitAnswerResponse, NextQuestionResponse } from "@/lib/types/quiz";
import { ConfigParser } from "@/lib/services/configParser";

interface FeedbackPanelProps {
  /** Response from submitting an answer */
  response: SubmitAnswerResponse;
  /** Config parser for UI decisions */
  configParser: ConfigParser;
  /** The question that was answered (for context) */
  question: NextQuestionResponse;
  /** Callback when user clicks continue */
  onContinue: () => void;
  /** Grade level for responsive text sizing */
  gradeLevel?: 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10;
}

/**
 * FeedbackPanel
 *
 * Shows feedback after user submits an answer.
 * Displays correctness status, explanations, misconceptions, and trap warnings.
 * Feedback depth is configurable via ConfigParser (minimal, moderate, detailed).
 *
 * Depths:
 * - Minimal: Just ✅/❌ badge
 * - Moderate: Badge + explanation
 * - Detailed: Badge + explanation + misconception + trap warning + mastery update
 *
 * Layout (detailed):
 * ┌─────────────────────────┐
 * │ ✅ CORRECT!             │  ← Color-coded badge
 * ├─────────────────────────┤
 * │ Why this is right:      │  ← Explanation
 * │ [text from API]         │
 * ├─────────────────────────┤
 * │ 💡 Did you know?        │  ← Misconception warning
 * │ [misconception text]    │
 * ├─────────────────────────┤
 * │ ⚠️  Watch out for trap  │  ← Trap warning
 * │ [trap explanation]      │
 * ├─────────────────────────┤
 * │ Mastery: 45% → 58%      │  ← Mastery update
 * ├─────────────────────────┤
 * │ [Continue Button]       │  ← Next
 * └─────────────────────────┘
 *
 * @example
 * <FeedbackPanel
 *   response={submitResponse}
 *   configParser={parser}
 *   question={currentQuestion}
 *   onContinue={() => loadNextQuestion()}
 *   gradeLevel={6}
 * />
 */
export const FeedbackPanel: FC<FeedbackPanelProps> = ({
  response,
  configParser,
  question,
  onContinue,
  gradeLevel = 6,
}) => {
  // Determine text sizes based on grade level
  const textSizeClasses = useMemo(() => {
    if (gradeLevel >= 3 && gradeLevel <= 5) {
      return {
        header: "text-2xl font-bold",
        section: "text-base font-semibold",
        body: "text-base",
        small: "text-sm",
      };
    }
    if (gradeLevel >= 6 && gradeLevel <= 8) {
      return {
        header: "text-xl font-bold",
        section: "text-base font-semibold",
        body: "text-sm",
        small: "text-xs",
      };
    }
    return {
      header: "text-lg font-bold",
      section: "text-sm font-semibold",
      body: "text-sm",
      small: "text-xs",
    };
  }, [gradeLevel]);

  // Get feedback depth
  const feedbackDepth = useMemo(
    () => configParser.getFeedbackDepth(),
    [configParser]
  );

  // DEBUG: Log what we're receiving
  useMemo(() => {
    console.log("FeedbackPanel DEBUG:", {
      feedbackDepth,
      configParserConfig: configParser.constructor.name,
      isCorrect: response.isCorrect,
      hasMisconception: !!response.misconceptionDetected,
      misconceptionData: response.misconceptionDetected,
      logicalTrapTriggered: response.logicalTrapTriggered,
      trapDetails: response.trapDetails,
      fullResponse: response,
    });
  }, [feedbackDepth, response, configParser]);

  // Color scheme based on correctness
  const colorScheme = useMemo(() => {
    if (response.isCorrect) {
      return {
        badge: "bg-green-500 text-white",
        badgeBg: "bg-green-50 border-green-200",
        section: "bg-green-50 border-green-200",
        icon: "✅",
        accent: "text-green-600",
        accentBg: "bg-green-100",
      };
    } else {
      return {
        badge: "bg-red-500 text-white",
        badgeBg: "bg-red-50 border-red-200",
        section: "bg-red-50 border-red-200",
        icon: "❌",
        accent: "text-red-600",
        accentBg: "bg-red-100",
      };
    }
  }, [response.isCorrect]);

  // Calculate mastery delta
  const masteryDelta = useMemo(() => {
    return response.masteryScore.delta;
  }, [response.masteryScore.delta]);

  // Format percentage change
  const masteryChangeDisplay = useMemo(() => {
    if (masteryDelta === 0) return "No change";
    const sign = masteryDelta > 0 ? "+" : "";
    return `${sign}${masteryDelta}%`;
  }, [masteryDelta]);

  return (
    <div className="w-full bg-white rounded-3xl shadow-lg p-8 space-y-4 animate-fadeIn">
      {/* Header Badge */}
      <div className={`px-6 py-4 rounded-2xl border-2 ${colorScheme.badgeBg}`}>
        <div className="flex items-center gap-3">
          <span className="text-4xl">{colorScheme.icon}</span>
          <div>
            <p className={`${textSizeClasses.header} ${colorScheme.accent}`}>
              {response.isCorrect ? "Excellent!" : "Not quite!"}
            </p>
            {response.isCorrect && response.streakUpdate && (
              <p className="text-sm text-green-600 font-semibold mt-1">
                🔥 Streak: {response.streakUpdate.current}
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Main Explanation (shown for moderate and detailed) */}
      {feedbackDepth !== "minimal" && response.solution && (
        <div className={`px-6 py-4 rounded-2xl border-2 ${colorScheme.section}`}>
          <p className={`${textSizeClasses.section} ${colorScheme.accent} mb-2`}>
            Why {response.isCorrect ? "this is correct" : "this isn't quite right"}:
          </p>
          <p className={`${textSizeClasses.body} ${colorScheme.accent}`}>
            {response.solution.summary}
          </p>
        </div>
      )}

      {/* Misconception Warning (shown for detailed) */}
      {feedbackDepth === "detailed" && response.misconceptionDetected && (
        <div className="px-6 py-4 rounded-2xl border-2 border-amber-200 bg-amber-50">
          <p className="text-2xl flex items-center gap-2 mb-2">
            <span>💡</span>
            <span className={`${textSizeClasses.section} text-amber-900`}>
              Common Misconception: {response.misconceptionDetected.name}
            </span>
          </p>
          {response.misconceptionDetected.whyWrong && (
            <p className={`${textSizeClasses.body} text-amber-900 mb-2`}>
              <strong>Why this is wrong:</strong> {response.misconceptionDetected.whyWrong}
            </p>
          )}
          {response.misconceptionDetected.teachingPoint && (
            <p className={`${textSizeClasses.body} text-amber-800 bg-amber-100 rounded-lg p-3`}>
              <strong>💡 Remember:</strong> {response.misconceptionDetected.teachingPoint}
            </p>
          )}
        </div>
      )}

      {/* Trap Warning (shown for detailed) */}
      {feedbackDepth === "detailed" && response.logicalTrapTriggered && response.trapDetails && (
        <div className="px-6 py-4 rounded-2xl border-2 border-orange-200 bg-orange-50">
          <p className="text-2xl flex items-center gap-2 mb-2">
            <span>⚠️</span>
            <span className={`${textSizeClasses.section} text-orange-900`}>
              Logical Trap Detected
            </span>
          </p>
          <p className={`${textSizeClasses.body} text-orange-900`}>
            {response.trapDetails.explanation}
          </p>
        </div>
      )}

      {/* Mastery Update (shown for detailed) */}
      {feedbackDepth === "detailed" && (
        <div className={`px-6 py-4 rounded-2xl border-2 border-blue-200 bg-blue-50`}>
          <p className={`${textSizeClasses.section} text-blue-900 mb-2`}>
            📈 Mastery Progress
          </p>
          <div className="flex items-center gap-4">
            <div>
              <p className={`${textSizeClasses.small} text-blue-700 mb-1`}>Before</p>
              <p className={`${textSizeClasses.body} font-bold text-blue-900`}>
                {response.masteryScore.previous}%
              </p>
            </div>
            <div className="text-blue-600">→</div>
            <div>
              <p className={`${textSizeClasses.small} text-blue-700 mb-1`}>After</p>
              <p className={`${textSizeClasses.body} font-bold text-blue-900`}>
                {response.masteryScore.current}%
              </p>
            </div>
            {masteryDelta !== 0 && (
              <div className={`ml-auto ${masteryDelta > 0 ? "text-green-600" : "text-red-600"}`}>
                <p className={`${textSizeClasses.small} font-semibold`}>
                  {masteryChangeDisplay}
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Continue Button */}
      <button
        onClick={onContinue}
        className={`w-full px-6 py-3 rounded-2xl font-semibold transition-all duration-150 mt-6 ${textSizeClasses.section} ${
          response.isCorrect
            ? "bg-green-500 hover:bg-green-600 text-white active:scale-95"
            : "bg-blue-500 hover:bg-blue-600 text-white active:scale-95"
        } focus:outline-none focus:ring-2 focus:ring-offset-2 ${
          response.isCorrect ? "focus:ring-green-400" : "focus:ring-blue-400"
        }`}
        aria-label={response.isCorrect ? "Continue to next question" : "Try again or continue"}
      >
        {response.isCorrect ? "Next Question" : "Try Again"}
      </button>

      {/* Accessibility: Announce feedback to screen readers */}
      <div className="sr-only" role="status" aria-live="assertive">
        {response.isCorrect ? "Correct!" : "Incorrect."}
        {response.solution && ` ${response.solution.summary}`}
        {response.misconceptionDetected && ` Common misconception: ${response.misconceptionDetected.explanation || response.misconceptionDetected.name}`}
        {response.logicalTrapTriggered && response.trapDetails && ` Watch out for: ${response.trapDetails.explanation}`}
        Mastery score changed from {response.masteryScore.previous}% to {response.masteryScore.current}%
      </div>

      {/* CSS for animation */}
      <style>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(8px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        
        .animate-fadeIn {
          animation: fadeIn 0.3s ease-out forwards;
        }
      `}</style>
    </div>
  );
};

export default FeedbackPanel;
