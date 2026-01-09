"use client";

import { FC, useCallback, useMemo } from "react";
import type { NextQuestionResponse } from "@/lib/types/quiz";
import { ConfigParser } from "@/lib/services/configParser";
import OptionTile from "./OptionTile";
import RichQuestionContent from "./RichQuestionContent";

interface QuestionCardProps {
  /** The question data from API */
  question: NextQuestionResponse;
  /** Config parser for UI decisions */
  configParser: ConfigParser;
  /** Callback when an option is selected */
  onOptionSelect: (optionId: string) => void;
  /** Currently selected option ID */
  selectedOptionId?: string | null;
  /** State of each option (for showing correct/incorrect) */
  optionStates?: Record<string, "default" | "selected" | "correct" | "incorrect" | "trapped">;
  /** Grade level for responsive sizing */
  gradeLevel?: 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10;
  /** Whether options are disabled (after submission) */
  isAnswered?: boolean;
  /** Show hints count */
  hintsAvailable?: number;
  /** Show misconception preview on hover */
  showMisconceptionPreview?: boolean;
}

/**
 * QuestionCard
 * 
 * Container component that displays a question with media and answer options.
 * Renders based on ConfigParser decisions (difficulty badge, media, options layout).
 * Responsive grid layout: 1 column mobile, 2 columns tablet+.
 * Works with all grade levels (3-10).
 * 
 * Layout:
 * - Difficulty badge (optional, ConfigParser controlled)
 * - Question text (always shown)
 * - Media (image/diagram, if present)
 * - Options grid (responsive columns)
 * - Hints available counter (if enabled)
 * 
 * @example
 * <QuestionCard 
 *   question={nextQuestion}
 *   configParser={parser}
 *   onOptionSelect={(id) => handleSelect(id)}
 *   selectedOptionId={selected}
 *   gradeLevel={6}
 * />
 */
export const QuestionCard: FC<QuestionCardProps> = ({
  question,
  configParser,
  onOptionSelect,
  selectedOptionId,
  optionStates = {},
  gradeLevel = 6,
  isAnswered = false,
  hintsAvailable = 0,
  showMisconceptionPreview = false,
}) => {
  // Determine text size based on grade level
  const textSizeClasses = useMemo(() => {
    if (gradeLevel >= 3 && gradeLevel <= 5) {
      return {
        question: "text-xl font-bold",
        difficulty: "text-sm font-semibold",
        subtext: "text-base",
      };
    }
    if (gradeLevel >= 6 && gradeLevel <= 8) {
      return {
        question: "text-lg font-semibold",
        difficulty: "text-xs font-medium",
        subtext: "text-base",
      };
    }
    return {
      question: "text-base font-semibold",
      difficulty: "text-xs font-medium",
      subtext: "text-sm",
    };
  }, [gradeLevel]);

  // Get difficulty color based on level
  const difficultyStyles = useMemo(() => {
    const baseClasses =
      "inline-block px-3 py-1 rounded-full font-semibold text-white mb-4";

    // Convert numeric difficulty (1-5) to string level
    let difficultyLevel = "medium";
    if (typeof question.difficulty === "number") {
      if (question.difficulty <= 2) difficultyLevel = "easy";
      else if (question.difficulty >= 4) difficultyLevel = "hard";
      else difficultyLevel = "medium";
    } else if (typeof question.difficulty === "string") {
      difficultyLevel = question.difficulty.toLowerCase();
    }

    switch (difficultyLevel) {
      case "easy":
        return baseClasses + " bg-green-500";
      case "medium":
        return baseClasses + " bg-blue-500";
      case "hard":
        return baseClasses + " bg-red-500";
      default:
        return baseClasses + " bg-gray-500";
    }
  }, [question.difficulty]);

  // Determine grid columns based on grade level and option count
  const gridClasses = useMemo(() => {
    const optionCount = question.options?.length || 0;

    // Mobile: always 1 column
    // Tablet (md): 2 columns if 4 options, 1 if 2
    // Desktop (lg): 2 columns if 4 options, 1 if 2

    if (optionCount <= 2) {
      return "grid-cols-1";
    }

    return "grid-cols-1 md:grid-cols-2";
  }, [question.options?.length]);

  // Get option state for each option
  const getOptionState = useCallback(
    (optionId: string): "default" | "selected" | "correct" | "incorrect" | "trapped" => {
      // If explicitly provided, use that
      if (optionStates[optionId]) {
        return optionStates[optionId];
      }

      // If selected and not answered, show selected state
      if (optionId === selectedOptionId && !isAnswered) {
        return "selected";
      }

      // Otherwise default
      return "default";
    },
    [optionStates, selectedOptionId, isAnswered]
  );

  // Handle option click
  const handleOptionClick = useCallback(
    (optionId: string) => {
      if (!isAnswered) {
        onOptionSelect(optionId);
      }
    },
    [onOptionSelect, isAnswered]
  );

  // Check if should show difficulty badge
  const shouldShowDifficulty = useMemo(
    () => configParser.shouldShowDifficulty() && question.difficulty,
    [configParser, question.difficulty]
  );

  // Get difficulty display label
  const difficultyLabel = useMemo(() => {
    if (typeof question.difficulty === "number") {
      if (question.difficulty <= 2) return "Easy";
      else if (question.difficulty >= 4) return "Hard";
      else return "Medium";
    } else if (typeof question.difficulty === "string") {
      return question.difficulty.charAt(0).toUpperCase() + question.difficulty.slice(1).toLowerCase();
    }
    return "Medium";
  }, [question.difficulty]);

  return (
    <div className="w-full bg-white rounded-3xl shadow-lg p-8 space-y-6">
      {/* Difficulty Badge */}
      {shouldShowDifficulty && (
        <div className="flex items-center gap-2">
          <span className={difficultyStyles}>
            {difficultyLabel}
          </span>
          <span className={`text-gray-600 ${textSizeClasses.difficulty}`}>
            {question.bloomLevel && `Level: ${question.bloomLevel}`}
          </span>
        </div>
      )}

      {/* Rich Content - K.C. Nag Narrative, Diagrams, and Visual Hints */}
      {/* Note: Visual representations are hidden until after submission (pedagogical strategy) */}
      {(question.richNarrative || question.richHtmlContent || question.visualHints) && (
        <RichQuestionContent
          richNarrative={question.richNarrative}
          richHtmlContent={question.richHtmlContent}
          visualHints={question.visualHints}
          chapter={question.chapterId}
          showNarrative={true}
          isAnswered={isAnswered}
        />
      )}

      {/* Question Text */}
      <div className="space-y-2">
        <h2 className={`${textSizeClasses.question} text-gray-900 leading-relaxed`}>
          {question.question}
        </h2>

        {/* Optional: Question context */}
        {question.questionContext && (
          <p className={`${textSizeClasses.subtext} text-gray-600 italic`}>
            {question.questionContext}
          </p>
        )}
      </div>

      {/* Options Grid */}
      <div>
        <div className={`grid ${gridClasses} gap-4`}>
          {question.options && question.options.length > 0 ? (
            question.options.map((option) => (
              <OptionTile
                key={option.id}
                option={option}
                isSelected={selectedOptionId === option.id}
                isDisabled={isAnswered}
                state={getOptionState(option.id)}
                onClick={() => handleOptionClick(option.id)}
                gradeLevel={gradeLevel}
                showMisconceptionPreview={showMisconceptionPreview}
              />
            ))
          ) : (
            <div className="col-span-full text-center text-gray-500 py-4">
              No options available for this question.
            </div>
          )}
        </div>
      </div>

      {/* Hints Available Counter */}
      {configParser.areHintsEnabled() && hintsAvailable > 0 && (
        <div className="flex items-center gap-2 text-blue-600 bg-blue-50 rounded-lg p-3 text-sm">
          <svg
            className="w-5 h-5 flex-shrink-0"
            fill="currentColor"
            viewBox="0 0 20 20"
            aria-hidden="true"
          >
            <path
              fillRule="evenodd"
              d="M18 5v8a2 2 0 01-2 2h-5l4 4v-4h3a2 2 0 002-2V5a2 2 0 00-2-2H4a2 2 0 00-2 2v8a2 2 0 002 2h1v3l4-3h5a2 2 0 002-2v-8a2 2 0 00-2-2H4a2 2 0 00-2 2v3h2V5h12z"
              clipRule="evenodd"
            />
          </svg>
          <span className="font-semibold">
            {hintsAvailable} {hintsAvailable === 1 ? "hint" : "hints"} available
          </span>
        </div>
      )}

      {/* Question Metadata (for debugging/accessibility) */}
      {question.bloomLevel && (
        <div className="sr-only">
          Question type: {question.topic}. Cognitive level: {question.bloomLevel}.
        </div>
      )}
    </div>
  );
};

export default QuestionCard;
