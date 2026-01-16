"use client";

import { FC, useMemo } from "react";

/**
 * Mastery data for a single concept
 */
export interface ConceptMastery {
  concept_id: string;
  concept_name: string;
  level: "not_started" | "learning" | "practiced" | "mastered";
  accuracy: number;
  total_attempts: number;
  correct_attempts: number;
}

/**
 * Full mastery response from API
 */
export interface StudentMasteryData {
  success: boolean;
  student_id: string;
  chapter_id: string;
  overall_accuracy: number;
  concepts: ConceptMastery[];
  recommendations: string[];
}

/**
 * Adaptive metadata from question response
 */
export interface AdaptiveQuestionMetadata {
  conceptId: string;
  reason: string;
  mastery: {
    current_level: string;
    attempts: number;
    accuracy: number;
  };
  progress: {
    total_concepts: number;
    mastered_count: number;
    learning_count: number;
    not_started_count: number;
    completion_percentage: number;
    concepts_mastered: string[];
    concepts_learning: string[];
    concepts_not_started: string[];
  };
}

interface MasteryProgressPanelProps {
  /**
   * Adaptive metadata from current question (real-time)
   */
  adaptiveData?: AdaptiveQuestionMetadata;
  
  /**
   * Full mastery data from API (detailed view)
   */
  masteryData?: StudentMasteryData;
  
  /**
   * Whether panel is collapsed
   */
  collapsed?: boolean;
  
  /**
   * Callback when panel is toggled
   */
  onToggle?: () => void;
  
  /**
   * Grade level for styling
   */
  gradeLevel?: number;
}

/**
 * Get color classes for mastery level
 */
const getMasteryColor = (level: string): string => {
  switch (level.toLowerCase()) {
    case "mastered":
      return "bg-green-500 text-white";
    case "practiced":
      return "bg-blue-500 text-white";
    case "learning":
      return "bg-yellow-500 text-white";
    case "not_started":
    default:
      return "bg-gray-300 text-gray-600";
  }
};

/**
 * Get icon for mastery level
 */
const getMasteryIcon = (level: string): string => {
  switch (level.toLowerCase()) {
    case "mastered":
      return "⭐";
    case "practiced":
      return "📚";
    case "learning":
      return "🌱";
    case "not_started":
    default:
      return "○";
  }
};

/**
 * MasteryProgressPanel
 * 
 * Displays concept-level mastery progress during a quiz session.
 * Shows which concepts the student has mastered, is learning, or hasn't started.
 * 
 * Features:
 * - Visual progress ring showing overall completion
 * - Concept pills with mastery status
 * - Current concept highlight
 * - Recommendations from adaptive system
 * 
 * @example
 * <MasteryProgressPanel 
 *   adaptiveData={question.adaptive}
 *   collapsed={false}
 * />
 */
export const MasteryProgressPanel: FC<MasteryProgressPanelProps> = ({
  adaptiveData,
  masteryData,
  collapsed = false,
  onToggle,
  gradeLevel = 5,
}) => {
  // Calculate progress percentage
  const progressPercent = useMemo(() => {
    if (adaptiveData?.progress) {
      return adaptiveData.progress.completion_percentage;
    }
    if (masteryData?.concepts) {
      const mastered = masteryData.concepts.filter(c => c.level === "mastered").length;
      const total = masteryData.concepts.length;
      return total > 0 ? Math.round((mastered / total) * 100) : 0;
    }
    return 0;
  }, [adaptiveData, masteryData]);

  // Get current concept being practiced
  const currentConcept = useMemo(() => {
    if (adaptiveData?.conceptId) {
      // Extract short name from full ID (e.g., "math.class5.factors_multiples.gcd" -> "gcd")
      const parts = adaptiveData.conceptId.split(".");
      return parts[parts.length - 1];
    }
    return null;
  }, [adaptiveData]);

  // Get concept list with status
  const conceptList = useMemo(() => {
    if (masteryData?.concepts) {
      return masteryData.concepts;
    }
    
    if (adaptiveData?.progress) {
      // Phase 1: Concept lists are now optional in question payloads
      // Use empty arrays as fallback when lists are not provided
      const concepts_mastered = adaptiveData.progress.concepts_mastered || [];
      const concepts_learning = adaptiveData.progress.concepts_learning || [];
      const concepts_not_started = adaptiveData.progress.concepts_not_started || [];
      
      const all: ConceptMastery[] = [
        ...concepts_mastered.map(id => ({
          concept_id: id,
          concept_name: id.split(".").pop()?.replace(/_/g, " ") || id,
          level: "mastered" as const,
          accuracy: 1,
          total_attempts: 0,
          correct_attempts: 0,
        })),
        ...concepts_learning.map(id => ({
          concept_id: id,
          concept_name: id.split(".").pop()?.replace(/_/g, " ") || id,
          level: "learning" as const,
          accuracy: 0.5,
          total_attempts: 0,
          correct_attempts: 0,
        })),
        ...concepts_not_started.map(id => ({
          concept_id: id,
          concept_name: id.split(".").pop()?.replace(/_/g, " ") || id,
          level: "not_started" as const,
          accuracy: 0,
          total_attempts: 0,
          correct_attempts: 0,
        })),
      ];
      
      return all;
    }
    
    return [];
  }, [adaptiveData, masteryData]);

  // Collapsed view - just show progress ring
  if (collapsed) {
    return (
      <button
        onClick={onToggle}
        className="flex items-center gap-2 px-3 py-2 bg-white rounded-full shadow-md hover:shadow-lg transition-shadow"
        aria-label="Show mastery progress"
      >
        <div className="relative w-8 h-8">
          <svg className="w-8 h-8 transform -rotate-90">
            <circle
              cx="16"
              cy="16"
              r="14"
              stroke="#e5e7eb"
              strokeWidth="3"
              fill="none"
            />
            <circle
              cx="16"
              cy="16"
              r="14"
              stroke="#10b981"
              strokeWidth="3"
              fill="none"
              strokeDasharray={`${progressPercent * 0.88} 88`}
              strokeLinecap="round"
            />
          </svg>
          <span className="absolute inset-0 flex items-center justify-center text-xs font-bold">
            {progressPercent}%
          </span>
        </div>
        <span className="text-sm font-medium text-gray-700">Mastery</span>
      </button>
    );
  }

  // Get total concepts - prefer adaptiveData.progress.total_concepts
  const totalConcepts = useMemo(() => {
    if (adaptiveData?.progress?.total_concepts) {
      return adaptiveData.progress.total_concepts;
    }
    if (conceptList.length > 0) {
      return conceptList.length;
    }
    return 0;
  }, [adaptiveData, conceptList]);

  // Get mastered count
  const masteredCount = useMemo(() => {
    if (adaptiveData?.progress?.mastered_count !== undefined) {
      return adaptiveData.progress.mastered_count;
    }
    return conceptList.filter(c => c.level === "mastered").length;
  }, [adaptiveData, conceptList]);

  // Check if we have data to display
  const hasData = adaptiveData?.progress || masteryData?.concepts || conceptList.length > 0;

  // Expanded view
  return (
    <div className="bg-white rounded-2xl shadow-lg p-4 w-full max-w-sm">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold text-gray-800">📊 Your Progress</h3>
        {onToggle && (
          <button
            onClick={onToggle}
            className="text-gray-400 hover:text-gray-600"
            aria-label="Collapse panel"
          >
            ✕
          </button>
        )}
      </div>

      {/* Progress Ring */}
      <div className="flex items-center gap-4 mb-4">
        <div className="relative w-16 h-16">
          <svg className="w-16 h-16 transform -rotate-90">
            <circle
              cx="32"
              cy="32"
              r="28"
              stroke="#e5e7eb"
              strokeWidth="6"
              fill="none"
            />
            <circle
              cx="32"
              cy="32"
              r="28"
              stroke="#10b981"
              strokeWidth="6"
              fill="none"
              strokeDasharray={`${progressPercent * 1.76} 176`}
              strokeLinecap="round"
              className="transition-all duration-500"
            />
          </svg>
          <span className="absolute inset-0 flex items-center justify-center text-lg font-bold text-gray-800">
            {progressPercent}%
          </span>
        </div>
        <div>
          <p className="text-sm text-gray-600">Chapter Mastery</p>
          {hasData ? (
            <p className="text-xs text-gray-400">
              {masteredCount} of {totalConcepts} concepts mastered
            </p>
          ) : (
            <p className="text-xs text-gray-400">Loading progress...</p>
          )}
        </div>
      </div>

      {/* Current Concept Highlight */}
      {currentConcept && adaptiveData?.reason && (
        <div className="bg-blue-50 rounded-lg p-3 mb-4 border-l-4 border-blue-500">
          <p className="text-sm font-medium text-blue-800">
            🎯 Now practicing: <span className="capitalize">{currentConcept.replace(/_/g, " ")}</span>
          </p>
          <p className="text-xs text-blue-600 mt-1">{adaptiveData.reason}</p>
        </div>
      )}

      {/* Concept Pills */}
      <div className="mb-4">
        <p className="text-xs text-gray-500 uppercase tracking-wide mb-2">Concepts</p>
        <div className="flex flex-wrap gap-2">
          {conceptList.length > 0 ? (
            <>
              {conceptList.slice(0, 8).map((concept) => {
                const shortName = concept.concept_name || concept.concept_id.split(".").pop() || "";
                const isCurrent = currentConcept && concept.concept_id.includes(currentConcept);
                
                return (
                  <span
                    key={concept.concept_id}
                    className={`
                      inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium
                      ${getMasteryColor(concept.level)}
                      ${isCurrent ? "ring-2 ring-blue-400 ring-offset-1" : ""}
                      transition-all duration-200
                    `}
                    title={`${shortName}: ${Math.round(concept.accuracy * 100)}% accuracy`}
                  >
                    <span>{getMasteryIcon(concept.level)}</span>
                    <span className="capitalize truncate max-w-[80px]">
                      {shortName.replace(/_/g, " ")}
                    </span>
                  </span>
                );
              })}
              {conceptList.length > 8 && (
                <span className="text-xs text-gray-400">
                  +{conceptList.length - 8} more
                </span>
              )}
            </>
          ) : hasData ? (
            <span className="text-xs text-gray-400 italic">
              {totalConcepts} concepts to master
            </span>
          ) : (
            <span className="text-xs text-gray-400 italic">
              Loading concepts...
            </span>
          )}
        </div>
      </div>

      {/* Legend */}
      <div className="flex flex-wrap gap-3 text-xs text-gray-500 border-t pt-3">
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 rounded-full bg-green-500"></span> Mastered
        </span>
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 rounded-full bg-blue-500"></span> Practiced
        </span>
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 rounded-full bg-yellow-500"></span> Learning
        </span>
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 rounded-full bg-gray-300"></span> Not Started
        </span>
      </div>

      {/* Recommendations */}
      {masteryData?.recommendations && masteryData.recommendations.length > 0 && (
        <div className="mt-4 pt-3 border-t">
          <p className="text-xs text-gray-500 uppercase tracking-wide mb-2">💡 Tips</p>
          {masteryData.recommendations.slice(0, 2).map((rec, i) => (
            <p key={i} className="text-sm text-gray-600 mb-1">
              • {rec}
            </p>
          ))}
        </div>
      )}
    </div>
  );
};

export default MasteryProgressPanel;
