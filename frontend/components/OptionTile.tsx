"use client";

import { FC, useCallback, useMemo } from "react";
import type { AnswerOption } from "@/lib/types/quiz";

interface OptionTileProps {
  /** The answer option data */
  option: AnswerOption;
  /** Whether this option is currently selected */
  isSelected: boolean;
  /** Whether this option is disabled (after submit) */
  isDisabled: boolean;
  /** Current state of the option */
  state: "default" | "selected" | "correct" | "incorrect" | "trapped";
  /** Callback when option is clicked */
  onClick: () => void;
  /** Grade level for responsive text sizing */
  gradeLevel?: 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10;
  /** Show misconception preview on hover */
  showMisconceptionPreview?: boolean;
}

/**
 * OptionTile
 * 
 * Individual answer option button for quiz questions.
 * Displays with state-based styling (default, selected, correct, incorrect, trapped).
 * Smooth color transitions and hover effects with full keyboard accessibility.
 * Works with all grade levels (3-10).
 * 
 * States:
 * - Default: White background, border
 * - Selected: Blue background, white text
 * - Correct: Green background, checkmark icon
 * - Incorrect: Red background, X icon
 * - Trapped: Orange background (logical trap triggered)
 * 
 * @example
 * <OptionTile 
 *   option={{ id: "opt1", text: "Option A", distractor_type: null }}
 *   isSelected={false}
 *   isDisabled={false}
 *   state="default"
 *   onClick={() => handleSelect("opt1")}
 *   gradeLevel={6}
 * />
 */
export const OptionTile: FC<OptionTileProps> = ({
  option,
  isSelected,
  isDisabled,
  state,
  onClick,
  gradeLevel = 6,
  showMisconceptionPreview = false,
}) => {
  // Determine text size based on grade level
  const textSizeClass = useMemo(() => {
    if (gradeLevel >= 3 && gradeLevel <= 5) return "text-lg font-bold";
    if (gradeLevel >= 6 && gradeLevel <= 8) return "text-base font-semibold";
    return "text-sm font-medium"; // Grade 9-10
  }, [gradeLevel]);

  // Determine styling based on state
  const styleClasses = useMemo(() => {
    let baseClasses =
      "relative w-full px-6 py-4 rounded-2xl border-2 transition-all duration-150 cursor-pointer ";
    baseClasses += "flex items-center gap-3 min-h-[56px] ";
    baseClasses += "hover:scale-105 active:scale-95 ";
    baseClasses += "focus:outline-none focus:ring-2 focus:ring-offset-2 ";

    switch (state) {
      case "correct":
        return (
          baseClasses +
          "bg-green-500 border-green-600 text-white focus:ring-green-400"
        );

      case "incorrect":
        return (
          baseClasses +
          "bg-red-500 border-red-600 text-white focus:ring-red-400"
        );

      case "trapped":
        return (
          baseClasses +
          "bg-orange-500 border-orange-600 text-white focus:ring-orange-400"
        );

      case "selected":
        return (
          baseClasses +
          "bg-blue-500 border-blue-600 text-white focus:ring-blue-400"
        );

      case "default":
      default:
        return (
          baseClasses +
          "bg-white border-gray-300 text-gray-700 hover:border-blue-300 hover:bg-blue-50 " +
          "focus:ring-blue-400 " +
          (isDisabled ? "opacity-60 cursor-not-allowed" : "")
        );
    }
  }, [state, isDisabled]);

  // Render appropriate icon based on state
  const renderIcon = useCallback(() => {
    switch (state) {
      case "correct":
        return (
          <svg
            className="w-6 h-6 flex-shrink-0"
            fill="currentColor"
            viewBox="0 0 20 20"
            aria-hidden="true"
          >
            <path
              fillRule="evenodd"
              d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
              clipRule="evenodd"
            />
          </svg>
        );

      case "incorrect":
        return (
          <svg
            className="w-6 h-6 flex-shrink-0"
            fill="currentColor"
            viewBox="0 0 20 20"
            aria-hidden="true"
          >
            <path
              fillRule="evenodd"
              d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
              clipRule="evenodd"
            />
          </svg>
        );

      case "trapped":
        return (
          <svg
            className="w-6 h-6 flex-shrink-0"
            fill="currentColor"
            viewBox="0 0 20 20"
            aria-hidden="true"
          >
            <path
              fillRule="evenodd"
              d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
              clipRule="evenodd"
            />
          </svg>
        );

      default:
        return null;
    }
  }, [state]);

  // Handle click with disabled check
  const handleClick = useCallback(() => {
    if (!isDisabled && state !== "correct" && state !== "incorrect") {
      onClick();
    }
  }, [onClick, isDisabled, state]);

  // Build ARIA label
  const ariaLabel = useMemo(() => {
    const stateText = {
      correct: "Correct answer",
      incorrect: "Incorrect answer",
      trapped: "This is a logical trap",
      selected: "Selected",
      default: "",
    };

    return `Option: ${option.label}${stateText[state] ? `, ${stateText[state]}` : ""}`;
  }, [option.label, state]);

  return (
    <div className="group relative">
      <button
        onClick={handleClick}
        disabled={isDisabled || state === "correct" || state === "incorrect"}
        className={styleClasses}
        role="option"
        aria-selected={isSelected}
        aria-label={ariaLabel}
        tabIndex={isDisabled ? -1 : 0}
      >
        {/* Option text */}
        <span className={`flex-1 text-left break-words ${textSizeClass}`}>
          {option.label}
        </span>

        {/* State icon */}
        {state !== "default" && state !== "selected" && renderIcon()}

        {/* Ripple effect on click */}
        {state === "selected" && (
          <svg
            className="absolute inset-0 w-6 h-6 top-1/2 right-6 -translate-y-1/2 flex-shrink-0"
            fill="currentColor"
            viewBox="0 0 20 20"
            aria-hidden="true"
          >
            <circle cx="10" cy="10" r="4" opacity="0.3" />
          </svg>
        )}
      </button>

      {/* Misconception indicator tooltip (from misconceptionTarget) */}
      {showMisconceptionPreview && option.misconceptionTarget && state === "default" && (
        <div
          className="absolute z-50 left-0 right-0 bottom-full mb-2 px-3 py-2 bg-orange-100 border border-orange-300 rounded-lg text-orange-900 text-sm opacity-0 group-hover:opacity-100 transition-opacity duration-150 pointer-events-none whitespace-normal"
          role="tooltip"
        >
          <span className="font-semibold block mb-1">💡 Common Misconception:</span>
          {option.misconceptionTarget.explanation || option.misconceptionTarget.name}
        </div>
      )}

      {/* Trap indicator for screen readers */}
      {option.isTrap && (
        <div className="sr-only">
          This is a logical trap. {option.trapExplanation}
        </div>
      )}
    </div>
  );
};

export default OptionTile;
