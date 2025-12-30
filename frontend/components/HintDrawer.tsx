"use client";

import { FC, useCallback, useMemo, useState } from "react";
import type { HintResponse } from "@/lib/types/quiz";
import { ConfigParser } from "@/lib/services/configParser";

interface HintDrawerProps {
  /** Question ID to request hints for */
  questionId: string;
  /** Number of hints available */
  hintsAvailable: number;
  /** Callback to request hint from API */
  onHintRequest: (hintIndex: number) => Promise<HintResponse>;
  /** Session ID for analytics */
  sessionId: string;
  /** Config parser for UI decisions */
  configParser: ConfigParser;
  /** Grade level for responsive text sizing */
  gradeLevel?: 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10;
}

interface DisplayedHint {
  id: number;
  text: string;
  type: "conceptual" | "visual" | "example" | "elimination" | "process";
  index: number;
  severity: "light" | "moderate" | "heavy";
}

/**
 * HintDrawer
 *
 * Progressive hint reveal system for quiz questions.
 * Shows a button that reveals hints one at a time.
 * Tracks remaining hint count and disables when exhausted.
 * Supports three hint types with different icons.
 * Works with all grade levels (3-10).
 *
 * Flow:
 * User clicks "Get Hint (X left)"
 *   ↓
 * API call to get next hint
 *   ↓
 * Hint animates in (fade, 300ms)
 *   ↓
 * Count decrements, button updates
 *   ↓
 * Repeats until no hints left (button disabled)
 *
 * @example
 * <HintDrawer
 *   questionId="q123"
 *   hintsAvailable={3}
 *   onHintRequest={async (idx) => await api.getHint(sessionId, questionId, idx)}
 *   sessionId="s456"
 *   configParser={parser}
 *   gradeLevel={6}
 * />
 */
export const HintDrawer: FC<HintDrawerProps> = ({
  questionId,
  hintsAvailable,
  onHintRequest,
  sessionId,
  configParser,
  gradeLevel = 6,
}) => {
  // State
  const [displayedHints, setDisplayedHints] = useState<DisplayedHint[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Derived values
  const textSizeClass = useMemo(() => {
    if (gradeLevel >= 3 && gradeLevel <= 5) return "text-base font-semibold";
    if (gradeLevel >= 6 && gradeLevel <= 8) return "text-sm font-semibold";
    return "text-xs font-medium";
  }, [gradeLevel]);

  const remainingHints = useMemo(() => {
    return hintsAvailable - displayedHints.length;
  }, [hintsAvailable, displayedHints.length]);

  const isHintAvailable = useMemo(() => {
    return remainingHints > 0 && configParser.areHintsEnabled();
  }, [remainingHints, configParser]);

  // Get icon for hint type
  const getHintIcon = useCallback((type: string): string => {
    switch (type) {
      case "visual":
        return "🎨"; // Art for visual hints
      case "example":
        return "�"; // Example hints
      case "elimination":
        return "❌"; // Elimination hints
      case "process":
        return "�"; // Process/procedural hints
      case "conceptual":
      default:
        return "💡"; // Lightbulb for concept hints
    }
  }, []);

  // Request hint from API
  const handleRequestHint = useCallback(async () => {
    if (!isHintAvailable || isLoading) return;

    setError(null);
    setIsLoading(true);

    try {
      // Request next hint (based on number already displayed)
      const hintResponse = await onHintRequest(displayedHints.length);

      // Add hint to displayed list
      setDisplayedHints((prev) => [
        ...prev,
        {
          id: hintResponse.hintIndex,
          text: hintResponse.hintContent,
          type: hintResponse.hintType,
          index: hintResponse.hintIndex,
          severity: hintResponse.severity,
        },
      ]);

      // Log hint usage for analytics
      if (typeof window !== "undefined") {
        // Could send to analytics service here
        console.debug("Hint requested", {
          questionId,
          sessionId,
          hintType: hintResponse.hintType,
          index: hintResponse.hintIndex,
          timestamp: new Date().toISOString(),
        });
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load hint");
      console.error("Error requesting hint:", err);
    } finally {
      setIsLoading(false);
    }
  }, [displayedHints.length, isHintAvailable, isLoading, onHintRequest, questionId, sessionId]);

  // Don't render if hints not enabled
  if (!configParser.areHintsEnabled()) {
    return null;
  }

  return (
    <div className="space-y-3">
      {/* Hint Request Button */}
      <button
        onClick={handleRequestHint}
        disabled={!isHintAvailable || isLoading}
        className={`w-full px-4 py-3 rounded-2xl transition-all duration-150 font-semibold flex items-center justify-center gap-2 ${textSizeClass} ${
          isHintAvailable
            ? "bg-blue-50 border-2 border-blue-300 text-blue-600 hover:bg-blue-100 hover:border-blue-400 active:scale-95"
            : "bg-gray-50 border-2 border-gray-300 text-gray-400 cursor-not-allowed opacity-60"
        }`}
        aria-label={`Get hint ${displayedHints.length > 0 ? `${remainingHints} left` : `${remainingHints} available`}`}
        role="button"
        tabIndex={isHintAvailable ? 0 : -1}
      >
        <svg
          className="w-5 h-5 flex-shrink-0"
          fill="currentColor"
          viewBox="0 0 20 20"
          aria-hidden="true"
        >
          <path d="M18 5v8a2 2 0 01-2 2h-5l4 4v-4h3a2 2 0 002-2V5a2 2 0 00-2-2H4a2 2 0 00-2 2v8a2 2 0 002 2h1v3l4-3h5a2 2 0 002-2v-3h2a2 2 0 002-2V5z" />
        </svg>
        <span>
          Get Hint
          {remainingHints > 0 && <span className="ml-1">({remainingHints})</span>}
        </span>
        {isLoading && (
          <svg className="w-4 h-4 animate-spin ml-auto" fill="none" viewBox="0 0 24 24">
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
        )}
      </button>

      {/* Error Message */}
      {error && (
        <div
          className="px-4 py-3 rounded-2xl bg-red-50 border-2 border-red-200 text-red-700 text-sm"
          role="alert"
        >
          <p className="font-semibold flex items-center gap-2">
            <svg
              className="w-4 h-4 flex-shrink-0"
              fill="currentColor"
              viewBox="0 0 20 20"
              aria-hidden="true"
            >
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                clipRule="evenodd"
              />
            </svg>
            Hint Load Error
          </p>
          <p className="text-xs mt-1">{error}</p>
        </div>
      )}

      {/* Displayed Hints */}
      {displayedHints.length > 0 && (
        <div className="space-y-2 pt-2">
          {displayedHints.map((hint, index) => (
            <div
              key={hint.id}
              className="px-4 py-3 rounded-2xl bg-blue-50 border-2 border-blue-200 animate-fadeIn"
              style={{
                animation: `fadeIn 0.3s ease-in forwards`,
                animationDelay: `${index * 100}ms`,
              }}
            >
              {/* Hint Header */}
              <div className="flex items-start gap-2 mb-2">
                <span className="text-lg flex-shrink-0">{getHintIcon(hint.type)}</span>
                <div className="flex-1 min-w-0">
                  <p className={`font-semibold text-blue-900 ${textSizeClass}`}>
                    Hint {hint.index + 1}
                  </p>
                  <p className="text-xs text-blue-700 mt-0.5 capitalize">
                    {hint.type === "visual"
                      ? "Visual clue"
                      : hint.type === "example"
                        ? "Example"
                        : hint.type === "elimination"
                          ? "Elimination"
                          : hint.type === "process"
                            ? "Step-by-step"
                            : "Key concept"}
                  </p>
                </div>
              </div>

              {/* Hint Text */}
              <p className={`text-blue-900 leading-relaxed ${textSizeClass}`}>
                {hint.text}
              </p>
            </div>
          ))}
        </div>
      )}

      {/* No Hints Left Message */}
      {displayedHints.length > 0 && remainingHints === 0 && (
        <div
          className="px-4 py-2 rounded-lg bg-amber-50 border border-amber-200 text-amber-700 text-xs"
          role="status"
        >
          You've used all available hints. Give it your best shot!
        </div>
      )}

      {/* Accessibility: Screen reader status */}
      <div className="sr-only" role="status" aria-live="polite">
        {remainingHints > 0
          ? `${remainingHints} hints available`
          : `No hints remaining`}
      </div>

      {/* CSS for animation */}
      <style>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(-8px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
    </div>
  );
};

export default HintDrawer;
