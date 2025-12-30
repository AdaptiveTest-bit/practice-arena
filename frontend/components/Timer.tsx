"use client";

import { FC, useMemo } from "react";

interface TimerProps {
  /**
   * Time remaining in seconds
   */
  timeRemaining: number;

  /**
   * Whether timer is in warning state (typically <= 30 seconds)
   * @default false
   */
  isWarning?: boolean;

  /**
   * Whether timer has expired
   * @default false
   */
  isExpired?: boolean;

  /**
   * Percentage of time remaining (0-100)
   * Used for circular progress indicator
   */
  percentage?: number;

  /**
   * Show circular progress ring instead of text only
   * @default false
   */
  showProgressRing?: boolean;

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

  /**
   * Custom label (e.g., "Time Left")
   * @default "Time"
   */
  label?: string;

  /**
   * Show seconds decimals (e.g., 1.5s)
   * @default false
   */
  showDecimals?: boolean;
}

/**
 * Timer Component
 *
 * Displays a countdown timer with warning and expiry states.
 * Supports all grade levels (3-10).
 *
 * Features:
 * - Clear MM:SS format display
 * - Color-coded states (normal/warning/expired)
 * - Optional circular progress ring
 * - Smooth animations
 * - Accessibility support
 * - Grade-level appropriate sizing
 *
 * @example
 * <Timer
 *   timeRemaining={240}
 *   isWarning={false}
 *   showProgressRing={true}
 *   gradeLevel={8}
 * />
 */
export const Timer: FC<TimerProps> = ({
  timeRemaining,
  isWarning = false,
  isExpired = false,
  percentage = 100,
  showProgressRing = false,
  reduceMotion = false,
  gradeLevel = 6,
  label = "Time",
  showDecimals = false,
}) => {
  // Format time to MM:SS
  const formattedTime = useMemo(() => {
    const minutes = Math.floor(timeRemaining / 60);
    const seconds = timeRemaining % 60;

    if (showDecimals && timeRemaining < 60) {
      const decimals = timeRemaining - Math.floor(timeRemaining);
      return `${minutes}:${seconds.toString().padStart(2, "0")}.${Math.round(decimals * 10)}`;
    }

    return `${minutes}:${seconds.toString().padStart(2, "0")}`;
  }, [timeRemaining, showDecimals]);

  // Determine color based on state
  const getTimerColor = (): string => {
    if (isExpired) return "text-red-600";
    if (isWarning) return "text-orange-600";
    return "text-blue-600";
  };

  const getBackgroundColor = (): string => {
    if (isExpired) return "bg-red-50";
    if (isWarning) return "bg-orange-50";
    return "bg-blue-50";
  };

  const getBorderColor = (): string => {
    if (isExpired) return "border-red-200";
    if (isWarning) return "border-orange-200";
    return "border-blue-200";
  };

  // Font size based on grade level
  const getFontSize = (): string => {
    if (gradeLevel <= 5) return "text-2xl";
    if (gradeLevel <= 8) return "text-xl";
    return "text-lg";
  };

  // Animation classes
  const pulseClass = isWarning && !reduceMotion ? "animate-pulse" : "";
  const transitionClass = reduceMotion ? "" : "transition-colors duration-300";

  // Calculate ring circumference and stroke-dashoffset for circular progress
  const radius = 45;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  return (
    <div className="flex flex-col items-center gap-2">
      {/* Label */}
      <span className="text-xs font-semibold text-gray-600 uppercase tracking-wide">
        {label}
      </span>

      {/* Timer Display Container */}
      <div
        className={`
          relative inline-flex items-center justify-center
          ${showProgressRing ? "w-24 h-24" : "px-4 py-2 rounded-lg border-2"}
          ${getBackgroundColor()} ${getBorderColor()} ${transitionClass}
        `}
        role="timer"
        aria-label={`${label}: ${formattedTime}`}
        aria-live="polite"
      >
        {/* Circular Progress Ring */}
        {showProgressRing && (
          <svg
            className="absolute inset-0"
            width="100%"
            height="100%"
            viewBox="0 0 100 100"
          >
            {/* Background circle */}
            <circle
              cx="50"
              cy="50"
              r={radius}
              fill="none"
              stroke={isExpired ? "#FEE2E2" : isWarning ? "#FFEDD5" : "#EFF6FF"}
              strokeWidth="3"
            />

            {/* Progress circle */}
            <circle
              cx="50"
              cy="50"
              r={radius}
              fill="none"
              stroke={isExpired ? "#DC2626" : isWarning ? "#F97316" : "#3B82F6"}
              strokeWidth="3"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              strokeLinecap="round"
              className={reduceMotion ? "" : "transition-all duration-300"}
              style={{ transform: "rotate(-90deg)", transformOrigin: "50% 50%" }}
            />
          </svg>
        )}

        {/* Time Text */}
        <span
          className={`
            font-bold font-mono
            ${getFontSize()}
            ${getTimerColor()}
            ${transitionClass}
            ${pulseClass}
            ${showProgressRing ? "relative z-10" : ""}
          `}
        >
          {formattedTime}
        </span>
      </div>

      {/* Status message for accessibility */}
      <div className="sr-only">
        {isExpired && "Time has expired"}
        {isWarning && "Less than 30 seconds remaining"}
        {!isExpired && !isWarning && "Time remaining"}
      </div>

      {/* Warning indicator (optional, for larger displays) */}
      {isWarning && (
        <span
          className="text-xs font-semibold text-orange-600 animate-pulse"
          role="alert"
        >
          ⚠️ Time running out!
        </span>
      )}

      {isExpired && (
        <span
          className="text-xs font-semibold text-red-600"
          role="alert"
        >
          ⏱️ Time expired
        </span>
      )}
    </div>
  );
};

export default Timer;
