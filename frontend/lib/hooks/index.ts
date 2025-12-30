/**
 * Custom Hooks for Quiz Logic
 * 
 * These hooks encapsulate complex logic and state management
 * making components cleaner and more testable
 */

import { useState, useCallback, useEffect } from "react";
import { NextQuestionResponse, SubmitAnswerResponse, HintResponse, AnswerOption } from "@/lib/types/quiz";
import { ConfigParser } from "@/lib/services/configParser";

/**
 * Main quiz logic hook
 * Manages: answer selection, submission, feedback display
 */
export function useQuizLogic(
  question: NextQuestionResponse | null,
  configParser: ConfigParser
) {
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [submitResponse, setSubmitResponse] = useState<SubmitAnswerResponse | null>(null);
  const [usedHints, setUsedHints] = useState(0);
  const [isLoading, setIsLoading] = useState(false);

  // Reset when question changes
  useEffect(() => {
    setSelectedAnswer(null);
    setIsSubmitted(false);
    setSubmitResponse(null);
    setUsedHints(0);
  }, [question?.questionId]);

  const handleSelectOption = useCallback(
    (optionId: string) => {
      if (!isSubmitted && question) {
        setSelectedAnswer(optionId);
      }
    },
    [isSubmitted, question]
  );

  const handleSubmitAnswer = useCallback(
    async (
      onSubmit: (answerId: string | string[]) => Promise<SubmitAnswerResponse>
    ) => {
      if (!selectedAnswer) return;

      setIsLoading(true);
      try {
        const response = await onSubmit(selectedAnswer);
        setSubmitResponse(response);
        setIsSubmitted(true);
      } catch (error) {
        console.error("Error submitting answer:", error);
      } finally {
        setIsLoading(false);
      }
    },
    [selectedAnswer]
  );

  const handleRequestHint = useCallback(
    async (onHintRequest: () => Promise<HintResponse>) => {
      setIsLoading(true);
      try {
        const response = await onHintRequest();
        setUsedHints((prev) => prev + 1);
        return response;
      } catch (error) {
        console.error("Error requesting hint:", error);
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  const handleReset = useCallback(() => {
    setSelectedAnswer(null);
    setIsSubmitted(false);
    setSubmitResponse(null);
    setUsedHints(0);
  }, []);

  const canSubmit = selectedAnswer !== null && !isSubmitted;
  const isCorrect = submitResponse?.isCorrect ?? false;
  const showFeedback = isSubmitted && submitResponse !== null;

  return {
    // State
    selectedAnswer,
    isSubmitted,
    submitResponse,
    usedHints,
    isLoading,
    
    // Computed
    canSubmit,
    isCorrect,
    showFeedback,
    
    // Handlers
    handleSelectOption,
    handleSubmitAnswer,
    handleRequestHint,
    handleReset,
  };
}

/**
 * Timer logic hook
 * Manages: countdown, warning state, time-up event
 */
export function useQuizTimer(
  timeLimit: number | undefined,
  onTimeUp: () => void,
  isActive: boolean = true
) {
  const [timeRemaining, setTimeRemaining] = useState(timeLimit ?? 0);
  const [isWarning, setIsWarning] = useState(false);
  const [isExpired, setIsExpired] = useState(false);

  useEffect(() => {
    if (!timeLimit || !isActive) return;

    const timer = setInterval(() => {
      setTimeRemaining((prev) => {
        const newTime = prev - 1;

        if (newTime <= 0) {
          setIsExpired(true);
          onTimeUp();
          return 0;
        }

        // Show warning when <= 30 seconds
        setIsWarning(newTime <= 30);

        return newTime;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [timeLimit, onTimeUp, isActive]);

  const percentage = timeLimit ? (timeRemaining / timeLimit) * 100 : 100;
  const displayTime = {
    minutes: Math.floor(timeRemaining / 60),
    seconds: timeRemaining % 60,
  };

  const formatTime = (mins: number, secs: number) => {
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  return {
    timeRemaining,
    isWarning,
    isExpired,
    percentage,
    displayTime,
    formatTime: () => formatTime(displayTime.minutes, displayTime.seconds),
    reset: () => setTimeRemaining(timeLimit ?? 0),
  };
}

/**
 * Misconception preview hook
 * Manages: showing misconception hints before selection
 */
export function useMisconceptionPreview() {
  const [hoveredOptionId, setHoveredOptionId] = useState<string | null>(null);
  const [showPreview, setShowPreview] = useState(false);

  const handleHover = useCallback((optionId: string) => {
    setHoveredOptionId(optionId);
    setShowPreview(true);
  }, []);

  const handleLeave = useCallback(() => {
    setHoveredOptionId(null);
    setShowPreview(false);
  }, []);

  return {
    hoveredOptionId,
    showPreview,
    handleHover,
    handleLeave,
  };
}

/**
 * Feedback animation hook
 * Manages: animation states for feedback reveal
 */
export function useFeedbackAnimation(
  configParser: ConfigParser,
  shouldShow: boolean = true
) {
  const [isVisible, setIsVisible] = useState(false);
  const [isAnimating, setIsAnimating] = useState(false);

  useEffect(() => {
    if (shouldShow) {
      setIsAnimating(true);
      const timer = setTimeout(
        () => {
          setIsVisible(true);
          setIsAnimating(false);
        },
        configParser.getAnimationDuration(100)
      );
      return () => clearTimeout(timer);
    }
  }, [shouldShow, configParser]);

  const duration = configParser.getAnimationDuration(300);

  return {
    isVisible,
    isAnimating,
    duration,
    animationClass: isAnimating ? "animate-fadeIn" : "opacity-100",
  };
}

/**
 * Progress tracking hook
 * Manages: calculating and tracking progress through quiz
 */
export function useProgress(
  questionsAttempted: number,
  correctCount: number,
  totalQuestions?: number
) {
  const progress = totalQuestions ? (questionsAttempted / totalQuestions) * 100 : 0;
  const accuracy = questionsAttempted > 0 ? (correctCount / questionsAttempted) * 100 : 0;

  return {
    progress: Math.min(progress, 100),
    accuracy: Math.round(accuracy),
    questionsAttempted,
    correctCount,
  };
}

/**
 * Celebration trigger hook
 * Manages: showing celebrations based on performance
 */
export function useCelebration(
  isCorrect: boolean,
  streak: number,
  masteryDelta: number,
  configParser: ConfigParser
) {
  const [shouldCelebrate, setShouldCelebrate] = useState(false);
  const [celebrationType, setCelebrationType] = useState<"subtle" | "moderate" | "explosive">(
    "subtle"
  );

  useEffect(() => {
    if (!isCorrect) {
      setShouldCelebrate(false);
      return;
    }

    setShouldCelebrate(true);

    // Determine celebration intensity
    if (streak % 25 === 0) {
      // Major milestone
      setCelebrationType("explosive");
    } else if (streak % 10 === 0) {
      // Minor milestone
      setCelebrationType("moderate");
    } else if (masteryDelta > 10) {
      // Big mastery jump
      setCelebrationType("moderate");
    } else {
      // Regular correct
      setCelebrationType("subtle");
    }

    // Auto-hide celebration after delay
    const delay = {
      subtle: 2000,
      moderate: 3000,
      explosive: 5000,
    }[celebrationType];

    const timer = setTimeout(() => setShouldCelebrate(false), delay);
    return () => clearTimeout(timer);
  }, [isCorrect, streak, masteryDelta]);

  return {
    shouldCelebrate,
    celebrationType,
  };
}

/**
 * Animation frame hook
 * Useful for smooth animations and micro-interactions
 */
export function useAnimationFrame(callback: (deltaTime: number) => void, isActive: boolean = true) {
  useEffect(() => {
    if (!isActive) return;

    let lastTime = Date.now();
    let animationId: number;

    const animate = () => {
      const currentTime = Date.now();
      const deltaTime = currentTime - lastTime;
      lastTime = currentTime;

      callback(deltaTime);
      animationId = requestAnimationFrame(animate);
    };

    animationId = requestAnimationFrame(animate);

    return () => cancelAnimationFrame(animationId);
  }, [callback, isActive]);
}

/**
 * Audio feedback hook
 * Manages: playing sounds based on quiz events
 */
export function useAudioFeedback(enabled: boolean = false) {
  const playSound = useCallback(
    async (soundType: "correct" | "incorrect" | "select" | "celebration") => {
      if (!enabled) return;

      try {
        // Placeholder: In production, load actual sound files
        const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();

        // Generate different tones
        const frequency = {
          correct: 800,
          incorrect: 400,
          select: 600,
          celebration: 1000,
        }[soundType];

        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();

        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);

        oscillator.frequency.value = frequency;
        oscillator.type = "sine";

        gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.3);

        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.3);
      } catch (error) {
        console.error("Audio playback error:", error);
      }
    },
    [enabled]
  );

  return { playSound };
}
