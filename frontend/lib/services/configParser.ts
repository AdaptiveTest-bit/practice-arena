/**
 * Configuration Parser Service
 * 
 * Parses backend config to determine what to render
 * and how to render it. All UI logic flows through this.
 */

import { SessionStartResponse, NextQuestionResponse } from "@/lib/types/quiz";

export class ConfigParser {
  constructor(private config: SessionStartResponse["uiConfig"] | null) {}

  /**
   * Animation Timing
   */
  getAnimationDuration(baseMs: number): number {
    if (!this.config) return baseMs;
    const multiplier = {
      low: 0.5,
      medium: 1,
      high: 1.5,
    };
    return baseMs * multiplier[this.config.animationIntensity || "medium"];
  }

  /**
   * What to show in header
   */
  shouldShowTimer(): boolean {
    return !!(this.config?.showTimer && this.config?.timeLimit);
  }

  shouldShowDifficulty(): boolean {
    return this.config?.enableDifficultyBadge ?? true;
  }

  shouldShowMastery(): boolean {
    return this.config?.enableMasteryDisplay ?? true;
  }

  shouldShowStreak(): boolean {
    return this.config?.enableStreak ?? true;
  }

  shouldShowAccuracy(): boolean {
    return this.config?.enableAccuracy ?? true;
  }

  shouldShowQuestionCounter(): boolean {
    return this.config?.showQuestionCounter ?? true;
  }

  /**
   * Hint Configuration
   */
  areHintsEnabled(): boolean {
    return this.config?.enableHints ?? true;
  }

  getHintCount(): number {
    return this.config?.hintCount ?? 3;
  }

  isProgressiveHintReveal(): boolean {
    return (this.config?.hintRevealMode ?? "progressive") === "progressive";
  }

  /**
   * Feedback Configuration
   * 
   * For practice mode: Default to "detailed" to show misconceptions + traps
   * For assessment mode: Backend will override to "minimal"
   */
  getFeedbackDepth(): "minimal" | "moderate" | "detailed" {
    if (!this.config) return "detailed";
    return this.config.feedbackDepth ?? "detailed";
  }

  /**
   * Should show trap warning?
   */
  shouldShowTrapWarning(question: NextQuestionResponse): boolean {
    return !!(this.config?.enableDifficultyBadge && 
           question.logicalTrapPresent && 
           question.renderingHints.showTrapWarning);
  }

  /**
   * Should show misconception preview?
   */
  shouldShowMisconceptionPreview(): boolean {
    return this.config?.featureFlags?.enableMisconceptionExplanation ?? false;
  }

  /**
   * Confetti enabled?
   */
  shouldEnableConfetti(): boolean {
    return !!(this.config?.enableConfetti && this.config?.animationIntensity !== "low");
  }

  /**
   * Sound enabled?
   */
  shouldEnableSound(): boolean {
    return this.config?.enableSound ?? false;
  }

  /**
   * Haptic feedback enabled?
   */
  shouldEnableHapticFeedback(): boolean {
    return this.config?.enableHapticFeedback ?? false;
  }

  /**
   * Feature flag check
   */
  isFeatureEnabled(featureName: string): boolean {
    return this.config?.featureFlags?.[featureName] ?? false;
  }

  /**
   * Get timeout duration for timer
   */
  getTimeLimit(): number | null {
    return this.config?.timeLimit ?? null;
  }

  /**
   * Get warning threshold for timer (when to show warning)
   */
  getTimerWarningThreshold(): number {
    return this.config?.timerWarningThreshold ?? 30;
  }

  /**
   * Get theme
   */
  getTheme(): "light" | "dark" | "colorful" | "high-contrast" {
    return this.config?.theme ?? "light";
  }

  /**
   * Get font size scale
   */
  getFontSize(): "small" | "medium" | "large" {
    return this.config?.fontSize ?? "medium";
  }

  /**
   * Check if gamification is enabled
   */
  isGamificationEnabled(): boolean {
    return !!(this.config?.enableDifficultyBadge || 
           this.config?.enableStreak || 
           this.config?.enableMasteryDisplay);
  }
}

/**
 * Helper to get animation duration with syntax sugar
 */
export function getAnimDuration(
  parser: ConfigParser,
  baseMs: number
): string {
  return `${parser.getAnimationDuration(baseMs)}ms`;
}

/**
 * Helper to get CSS easing function
 */
export function getEasing(type: "ease-in-out" | "ease-out" | "ease-in" | "ease") {
  const easings = {
    "ease-in-out": "cubic-bezier(0.4, 0, 0.6, 1)",
    "ease-out": "cubic-bezier(0, 0, 0.2, 1)",
    "ease-in": "cubic-bezier(0.4, 0, 1, 1)",
    ease: "cubic-bezier(0.4, 0, 0.2, 1)",
  };
  return easings[type];
}
