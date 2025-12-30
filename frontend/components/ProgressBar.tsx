"use client";

import { FC, useMemo } from "react";

interface ProgressBarProps {
  /**
   * Number of questions attempted so far
   */
  currentProgress: number;

  /**
   * Number of correct answers
   */
  correctAnswers: number;

  /**
   * Total number of questions in quiz
   * If not provided, progress is undefined
   */
  totalQuestions?: number;

  /**
   * Show accuracy percentage badge
   * @default true
   */
  showAccuracy?: boolean;

  /**
   * Label text (e.g., "Question 5 of 10")
   * If not provided, uses default calculation
   */
  label?: string;

  /**
   * Disable animations for accessibility
   * @default false
   */
  reduceMotion?: boolean;

  /**
   * Grade level for styling adaptation
   * @default 6
   */
  gradeLevel?: number;
}

/**
 * ProgressBar Component
 *
 * Displays quiz progress as a visual bar with accuracy indicator.
 * Supports all grade levels (3-10).
 *
 * Features:
 * - Smooth animated progress bar
 * - Color gradient based on accuracy
 * - Responsive design
 * - Accessibility support
 * - Grade-level appropriate sizing
 *
 * @example
 * <ProgressBar
 *   currentProgress={5}
 *   correctAnswers={4}
 *   totalQuestions={10}
 *   showAccuracy={true}
 *   gradeLevel={8}
 * />
 */
export const ProgressBar: FC<ProgressBarProps> = ({
  currentProgress,
  correctAnswers,
  totalQuestions,
  showAccuracy = true,
  label,
  reduceMotion = false,
  gradeLevel = 6,
}) => {
  // Calculate progress percentage
  const progressPercentage = useMemo(() => {
    if (!totalQuestions || totalQuestions === 0) return 0;
    return Math.min((currentProgress / totalQuestions) * 100, 100);
  }, [currentProgress, totalQuestions]);

  // Calculate accuracy percentage
  const accuracyPercentage = useMemo(() => {
    if (currentProgress === 0) return 0;
    return Math.round((correctAnswers / currentProgress) * 100);
  }, [correctAnswers, currentProgress]);

  // Determine progress bar color based on accuracy
  const getProgressColor = (): string => {
    if (accuracyPercentage >= 80) return "bg-gradient-to-r from-green-400 to-green-500";
    if (accuracyPercentage >= 60) return "bg-gradient-to-r from-blue-400 to-blue-500";
    if (accuracyPercentage >= 40) return "bg-gradient-to-r from-orange-400 to-orange-500";
    return "bg-gradient-to-r from-red-400 to-red-500";
  };

  // Determine text color for accuracy badge
  const getAccuracyTextColor = (): string => {
    if (accuracyPercentage >= 80) return "text-green-600";
    if (accuracyPercentage >= 60) return "text-blue-600";
    if (accuracyPercentage >= 40) return "text-orange-600";
    return "text-red-600";
  };

  // Font size based on grade level
  const getFontSize = (): string => {
    if (gradeLevel <= 5) return "text-sm";
    if (gradeLevel <= 8) return "text-xs";
    return "text-xs";
  };

  // Default label if not provided
  const displayLabel = label || `${currentProgress}${totalQuestions ? ` of ${totalQuestions}` : ""}`;

  // Animation class
  const animationClass = reduceMotion ? "" : "transition-all duration-300 ease-out";

  return (
    <div className="w-full space-y-2">
      {/* Header with label and accuracy */}
      <div className="flex items-center justify-between">
        <span
          className={`font-semibold text-gray-700 ${getFontSize()}`}
          role="status"
          aria-label={`Progress: ${displayLabel}`}
        >
          {displayLabel}
        </span>

        {showAccuracy && currentProgress > 0 && (
          <span
            className={`font-bold ${getFontSize()} ${getAccuracyTextColor()}`}
            role="status"
            aria-label={`Accuracy: ${accuracyPercentage}%`}
          >
            {accuracyPercentage}% ✓
          </span>
        )}
      </div>

      {/* Progress bar container */}
      <div
        className="w-full h-2 bg-gray-200 rounded-full overflow-hidden shadow-sm"
        role="progressbar"
        aria-valuenow={Math.round(progressPercentage)}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label={`Quiz progress: ${Math.round(progressPercentage)}%`}
      >
        {/* Progress bar fill */}
        <div
          className={`h-full ${getProgressColor()} ${animationClass}`}
          style={{
            width: `${progressPercentage}%`,
          }}
        />
      </div>

      {/* Optional progress text for accessibility */}
      <div className="sr-only">
        Progress: {Math.round(progressPercentage)}% complete.
        {currentProgress > 0 && ` Accuracy: ${accuracyPercentage}%.`}
      </div>
    </div>
  );
};

export default ProgressBar;
