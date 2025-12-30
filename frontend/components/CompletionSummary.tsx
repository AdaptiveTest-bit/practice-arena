"use client";

import { FC } from "react";
import { ConfigParser } from "@/lib/services/configParser";

export interface SessionCompletionResponse {
  success: boolean;
  isComplete: boolean;
  completionAnalysis: {
    difficulty_mastery: Record<number, { accuracy: number; attempts: number; mastered: boolean; status: string }>;
    bloom_mastery: Record<string, { accuracy: number; attempts: number; mastered: boolean; status: string }>;
    concept_mastery: Record<string, { accuracy: number; attempts: number; mastered: boolean; status: string }>;
    problem_misconceptions: Array<{ type: string; count: number }>;
  };
  sessionSummary: {
    questions_answered: number;
    accuracy_overall: number;
    concepts_mastered: string[];
    concepts_in_progress: string[];
    time_spent_minutes: number;
  };
  nextRecommendation: string;
}

interface CompletionSummaryProps {
  completionData: SessionCompletionResponse;
  chapterName?: string;
  onStartNew?: () => void;
  onBackToDashboard?: () => void;
  configParser?: ConfigParser;
  gradeLevel?: number;
}

/**
 * CompletionSummary Component
 *
 * Displays comprehensive mastery achievement summary with:
 * - Celebratory header
 * - Performance metrics (questions, accuracy, time)
 * - Mastery breakdown (difficulty levels, Bloom levels, concepts)
 * - Problem misconceptions to review
 * - Navigation buttons to continue or go back
 *
 * Used when student achieves mastery across all dimensions:
 * ✅ All difficulties (1-5) ≥80% accuracy
 * ✅ All Bloom levels ≥80% accuracy
 * ✅ All concepts ≥80% accuracy
 * ✅ No problematic misconceptions
 *
 * @example
 * <CompletionSummary
 *   completionData={completionCheck}
 *   chapterName="Large Numbers"
 *   onStartNew={() => startNewSession()}
 *   configParser={configParser}
 *   gradeLevel={5}
 * />
 */
export const CompletionSummary: FC<CompletionSummaryProps> = ({
  completionData,
  chapterName = "Chapter",
  onStartNew = () => window.location.reload(),
  onBackToDashboard = () => (window.location.href = "/dashboard"),
  configParser,
  gradeLevel = 5,
}) => {
  const { completionAnalysis, sessionSummary } = completionData;

  // Celebration animation
  const confetti = () => {
    if (typeof window !== "undefined" && "confetti" in window) {
      (window as any).confetti();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-blue-50 to-purple-50 p-4 sm:p-6 lg:p-8">
      <div className="max-w-4xl mx-auto">
        {/* Celebration Header */}
        <div className="text-center mb-12 animate-bounce">
          <div className="text-6xl mb-4">🎉</div>
          <h1 className="text-4xl sm:text-5xl font-bold bg-gradient-to-r from-green-600 to-blue-600 bg-clip-text text-transparent mb-2">
            Chapter Mastered!
          </h1>
          <p className="text-gray-600 text-xl">{chapterName}</p>
          <p className="text-gray-500 text-sm mt-2">You've achieved excellence across all dimensions</p>
        </div>

        {/* Performance Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          {/* Questions */}
          <div className="bg-white rounded-2xl shadow-lg p-6 border-2 border-blue-200 hover:shadow-xl transition-shadow">
            <div className="text-3xl mb-2">📋</div>
            <p className="text-gray-600 text-sm font-semibold">Questions Answered</p>
            <p className="text-3xl font-bold text-blue-600">{sessionSummary.questions_answered}</p>
          </div>

          {/* Accuracy */}
          <div className="bg-white rounded-2xl shadow-lg p-6 border-2 border-green-200 hover:shadow-xl transition-shadow">
            <div className="text-3xl mb-2">🎯</div>
            <p className="text-gray-600 text-sm font-semibold">Overall Accuracy</p>
            <p className="text-3xl font-bold text-green-600">
              {Math.round(sessionSummary.accuracy_overall)}%
            </p>
          </div>

          {/* Time */}
          <div className="bg-white rounded-2xl shadow-lg p-6 border-2 border-purple-200 hover:shadow-xl transition-shadow">
            <div className="text-3xl mb-2">⏱️</div>
            <p className="text-gray-600 text-sm font-semibold">Time Spent</p>
            <p className="text-3xl font-bold text-purple-600">
              {sessionSummary.time_spent_minutes} min
            </p>
          </div>
        </div>

        {/* Mastery Breakdown */}
        <div className="bg-white rounded-3xl shadow-2xl p-8 mb-8 border border-gray-200">
          <h2 className="text-2xl font-bold text-gray-900 mb-8 flex items-center">
            <span className="text-2xl mr-3">📊</span>
            Mastery Breakdown
          </h2>

          {/* Difficulty Levels */}
          <div className="mb-10">
            <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
              <span className="text-xl mr-2">🏔️</span>
              Difficulty Levels
            </h3>
            <div className="grid grid-cols-5 gap-2">
              {Object.entries(completionAnalysis.difficulty_mastery).map(([level, data]: [string, any]) => (
                <div
                  key={`difficulty_${level}`}
                  className="bg-gradient-to-br from-blue-100 to-blue-50 rounded-xl p-4 text-center border-2 border-blue-300 hover:shadow-lg transition-shadow"
                >
                  <p className="text-gray-700 font-bold text-2xl mb-1">{level}</p>
                  <p className="text-xs text-gray-600 font-semibold">{Math.round(data.accuracy * 100)}%</p>
                  <p className="text-sm mt-2">{data.mastered ? "✅" : "⚠️"}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Bloom Levels */}
          <div className="mb-10">
            <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
              <span className="text-xl mr-2">🧠</span>
              Bloom's Cognitive Levels
            </h3>
            <div className="space-y-3">
              {Object.entries(completionAnalysis.bloom_mastery).map(([level, data]: [string, any]) => (
                <div
                  key={`bloom_${level}`}
                  className="flex items-center justify-between bg-gradient-to-r from-purple-50 to-pink-50 p-4 rounded-xl border border-purple-200 hover:shadow-md transition-shadow"
                >
                  <div className="flex-1">
                    <p className="font-semibold text-gray-800 capitalize">{level}</p>
                    <div className="w-full bg-gray-300 rounded-full h-2 mt-2">
                      <div
                        className="bg-gradient-to-r from-purple-500 to-pink-500 h-2 rounded-full transition-all"
                        style={{ width: `${data.accuracy * 100}%` }}
                      />
                    </div>
                  </div>
                  <div className="ml-4 text-right">
                    <p className="font-bold text-gray-800">{Math.round(data.accuracy * 100)}%</p>
                    <p className="text-xs text-gray-600">{data.status}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Concepts Mastered */}
          {sessionSummary.concepts_mastered.length > 0 && (
            <div className="mb-10">
              <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
                <span className="text-xl mr-2">🎓</span>
                Concepts Mastered
              </h3>
              <div className="flex flex-wrap gap-2">
                {sessionSummary.concepts_mastered.map((concept) => (
                  <div
                    key={`concept_${concept}`}
                    className="bg-gradient-to-r from-green-400 to-green-500 text-white px-4 py-2 rounded-full font-semibold text-sm shadow-lg hover:shadow-xl transition-shadow"
                  >
                    ✅ {concept}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Problem Misconceptions */}
          {completionAnalysis.problem_misconceptions.length > 0 && (
            <div className="mb-10">
              <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
                <span className="text-xl mr-2">⚠️</span>
                Areas to Review
              </h3>
              <div className="space-y-2">
                {completionAnalysis.problem_misconceptions.map((misc, idx) => (
                  <div key={idx} className="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded flex items-start">
                    <span className="text-lg mr-3">📍</span>
                    <div>
                      <p className="font-semibold text-gray-800 capitalize">{misc.type}</p>
                      <p className="text-sm text-gray-600">
                        Encountered {misc.count} time{misc.count !== 1 ? "s" : ""}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Action Buttons */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-8">
          <button
            onClick={() => {
              confetti();
              onStartNew();
            }}
            className="bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 text-white font-bold py-4 px-6 rounded-2xl shadow-lg hover:shadow-xl transition-all transform hover:scale-105 active:scale-95 flex items-center justify-center gap-2"
          >
            <span className="text-xl">🔄</span>
            Practice Again
          </button>

          <button
            onClick={onBackToDashboard}
            className="bg-gradient-to-r from-gray-700 to-gray-800 hover:from-gray-800 hover:to-gray-900 text-white font-bold py-4 px-6 rounded-2xl shadow-lg hover:shadow-xl transition-all transform hover:scale-105 active:scale-95 flex items-center justify-center gap-2"
          >
            <span className="text-xl">📚</span>
            Back to Dashboard
          </button>
        </div>

        {/* Motivational Message */}
        <div className="text-center p-6 bg-gradient-to-r from-yellow-100 to-pink-100 rounded-2xl border-2 border-yellow-300">
          <p className="text-gray-800 font-semibold text-lg">
            🌟 Fantastic work! You've demonstrated mastery of this chapter.
          </p>
          <p className="text-gray-700 mt-2">
            Ready for the next challenge? Head back to the dashboard to explore more chapters!
          </p>
        </div>
      </div>
    </div>
  );
};
