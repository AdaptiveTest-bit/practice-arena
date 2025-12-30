"use client";

import { FC, useCallback, useEffect, useMemo, useState } from "react";
import { ConfigParser } from "@/lib/services/configParser";

interface RewardToastProps {
  /** Whether the answer was correct */
  isCorrect: boolean;
  /** Current streak count */
  streak: number;
  /** Mastery score delta (percentage change) */
  masteryDelta: number;
  /** Config parser for UI decisions */
  configParser: ConfigParser;
  /** Grade level for text sizing */
  gradeLevel?: 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10;
  /** Whether to show the toast */
  isVisible?: boolean;
  /** Callback when toast should close */
  onClose?: () => void;
  /** Auto-dismiss time in milliseconds */
  autoDismissMs?: number;
}

interface ToastConfig {
  message: string;
  icon: string;
  backgroundColor: string;
  textColor: string;
  celebrationType: "subtle" | "moderate" | "explosive";
  shouldPlaySound: boolean;
  shouldShowConfetti: boolean;
}

/**
 * RewardToast
 *
 * Celebration notification that appears after correct answers.
 * Displays achievement milestones (streaks, mastery gains).
 * Supports three celebration levels: subtle, moderate, explosive.
 * Can trigger sound effects and confetti based on ConfigParser.
 *
 * Celebration Triggers:
 * - Correct answer: "Great job!" (subtle)
 * - Streak 5: "5 in a row! 🔥" (moderate)
 * - Streak 10: "10 in a row! 🚀" (explosive)
 * - Streak 25: "25 in a row!!! 🎉" (explosive)
 * - Streak 50: "50 in a row!!! 🏆" (explosive)
 * - Mastery gain +10%: "Mastery up! 📈" (moderate)
 * - Mastery gain +20%: "Big mastery jump! 📈" (explosive)
 *
 * Works with all grade levels (3-10).
 * Respects reduceMotion preferences.
 *
 * @example
 * <RewardToast
 *   isCorrect={true}
 *   streak={10}
 *   masteryDelta={15}
 *   configParser={parser}
 *   gradeLevel={6}
 *   isVisible={true}
 *   onClose={() => setShowToast(false)}
 * />
 */
export const RewardToast: FC<RewardToastProps> = ({
  isCorrect,
  streak,
  masteryDelta,
  configParser,
  gradeLevel = 6,
  isVisible = true,
  onClose,
  autoDismissMs = 3000,
}) => {
  const [showConfetti, setShowConfetti] = useState(false);

  // Determine text size based on grade level
  const textSizeClass = useMemo(() => {
    if (gradeLevel >= 3 && gradeLevel <= 5) return "text-lg font-bold";
    if (gradeLevel >= 6 && gradeLevel <= 8) return "text-base font-bold";
    return "text-sm font-bold";
  }, [gradeLevel]);

  // Determine celebration based on achievement
  const toastConfig = useMemo((): ToastConfig => {
    if (!isCorrect) {
      return {
        message: "Not quite... try again!",
        icon: "💪",
        backgroundColor: "bg-blue-500",
        textColor: "text-white",
        celebrationType: "subtle",
        shouldPlaySound: false,
        shouldShowConfetti: false,
      };
    }

    // Streak milestones
    if (streak === 50) {
      return {
        message: "50 in a row!!! 🏆",
        icon: "🏆",
        backgroundColor: "bg-purple-500",
        textColor: "text-white",
        celebrationType: "explosive",
        shouldPlaySound: true,
        shouldShowConfetti: true,
      };
    }

    if (streak === 25) {
      return {
        message: "25 in a row!! 🚀",
        icon: "🚀",
        backgroundColor: "bg-red-500",
        textColor: "text-white",
        celebrationType: "explosive",
        shouldPlaySound: true,
        shouldShowConfetti: true,
      };
    }

    if (streak === 10) {
      return {
        message: "10 in a row! 🔥",
        icon: "🔥",
        backgroundColor: "bg-orange-500",
        textColor: "text-white",
        celebrationType: "explosive",
        shouldPlaySound: true,
        shouldShowConfetti: true,
      };
    }

    if (streak === 5) {
      return {
        message: "5 in a row! 👏",
        icon: "👏",
        backgroundColor: "bg-yellow-500",
        textColor: "text-white",
        celebrationType: "moderate",
        shouldPlaySound: true,
        shouldShowConfetti: false,
      };
    }

    // Mastery gains
    if (masteryDelta >= 20) {
      return {
        message: `Big mastery jump! 📈 +${masteryDelta}%`,
        icon: "📈",
        backgroundColor: "bg-green-500",
        textColor: "text-white",
        celebrationType: "explosive",
        shouldPlaySound: true,
        shouldShowConfetti: true,
      };
    }

    if (masteryDelta >= 10) {
      return {
        message: `Mastery up! 📈 +${masteryDelta}%`,
        icon: "📈",
        backgroundColor: "bg-emerald-500",
        textColor: "text-white",
        celebrationType: "moderate",
        shouldPlaySound: true,
        shouldShowConfetti: false,
      };
    }

    // Default: just correct answer
    return {
      message: "Great job! ✅",
      icon: "✅",
      backgroundColor: "bg-green-500",
      textColor: "text-white",
      celebrationType: "subtle",
      shouldPlaySound: false,
      shouldShowConfetti: false,
    };
  }, [isCorrect, streak, masteryDelta]);

  // Play sound effect
  const playSound = useCallback(() => {
    if (toastConfig.shouldPlaySound && configParser.shouldEnableSound?.()) {
      // Create a simple beep sound using Web Audio API
      try {
        const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();

        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);

        oscillator.frequency.value = 800; // Hz
        oscillator.type = "sine";

        gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.1);

        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.1);
      } catch (err) {
        // Web Audio API not available or blocked
        console.debug("Sound effect not available");
      }
    }
  }, [toastConfig.shouldPlaySound, configParser]);

  // Trigger confetti
  const triggerConfetti = useCallback(() => {
    if (toastConfig.shouldShowConfetti && configParser.shouldEnableConfetti?.()) {
      setShowConfetti(true);
      setTimeout(() => setShowConfetti(false), 1500);
    }
  }, [toastConfig.shouldShowConfetti, configParser]);

  // Initialize toast on mount
  useEffect(() => {
    if (isVisible) {
      playSound();
      triggerConfetti();

      // Auto-dismiss
      if (autoDismissMs > 0 && onClose) {
        const timer = setTimeout(onClose, autoDismissMs);
        return () => clearTimeout(timer);
      }
    }
  }, [isVisible, playSound, triggerConfetti, autoDismissMs, onClose]);

  if (!isVisible) {
    return null;
  }

  return (
    <div
      className={`fixed bottom-6 right-6 px-6 py-4 rounded-2xl shadow-2xl ${toastConfig.backgroundColor} ${toastConfig.textColor} ${textSizeClass} flex items-center gap-3 animate-slideIn z-50 max-w-xs`}
      role="status"
      aria-live="polite"
      aria-atomic="true"
    >
      {/* Icon */}
      <span className="text-2xl flex-shrink-0">{toastConfig.icon}</span>

      {/* Message */}
      <p className="flex-1">{toastConfig.message}</p>

      {/* Close button */}
      {onClose && (
        <button
          onClick={onClose}
          className="ml-2 p-1 hover:bg-white/20 rounded transition-colors"
          aria-label="Close notification"
        >
          <svg
            className="w-4 h-4"
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
        </button>
      )}

      {/* Confetti */}
      {showConfetti && <Confetti />}

      {/* CSS Animations */}
      <style>{`
        @keyframes slideIn {
          from {
            opacity: 0;
            transform: translateX(100%) translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateX(0) translateY(0);
          }
        }

        .animate-slideIn {
          animation: slideIn 0.3s ease-out forwards;
        }

        @keyframes confettiFall {
          to {
            transform: translateY(100px) rotate(360deg);
            opacity: 0;
          }
        }

        .confetti-piece {
          animation: confettiFall 1.5s ease-out forwards;
        }
      `}</style>
    </div>
  );
};

/**
 * Confetti Component
 * Renders falling confetti pieces
 */
const Confetti: FC = () => {
  const confettiPieces = useMemo(() => {
    return Array.from({ length: 30 }, (_, i) => ({
      id: i,
      left: Math.random() * 100,
      delay: Math.random() * 0.2,
      duration: 1.5 + Math.random() * 0.5,
      color: ["bg-yellow-400", "bg-pink-400", "bg-purple-400", "bg-blue-400", "bg-green-400"][
        Math.floor(Math.random() * 5)
      ],
    }));
  }, []);

  return (
    <>
      {confettiPieces.map((piece) => (
        <div
          key={piece.id}
          className={`confetti-piece absolute w-2 h-2 rounded-full pointer-events-none ${piece.color}`}
          style={{
            left: `${piece.left}%`,
            top: "50%",
            animation: `confettiFall ${piece.duration}s ease-out forwards`,
            animationDelay: `${piece.delay}s`,
          }}
        />
      ))}
    </>
  );
};

export default RewardToast;
