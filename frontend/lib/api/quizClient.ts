/**
 * Quiz API Client
 * 
 * Type-safe API client for all quiz operations
 * Handles: session management, questions, answers, hints
 */

import axios, { AxiosInstance, AxiosError } from "axios";
import {
  SessionStartResponse,
  NextQuestionResponse,
  SubmitAnswerResponse,
  HintResponse,
  ApiError,
  ApiResponse,
} from "@/lib/types/quiz";

/**
 * Session Completion Response Types
 */
export interface DifficultyMasteryStatus {
  accuracy: number;
  attempts: number;
  mastered: boolean;
  status: string;
}

export interface BloomMasteryStatus {
  accuracy: number;
  attempts: number;
  mastered: boolean;
  status: string;
}

export interface ConceptMasteryStatus {
  accuracy: number;
  attempts: number;
  mastered: boolean;
  status: string;
}

export interface MisconceptionInfo {
  type: string;
  count: number;
}

export interface CompletionAnalysis {
  difficulty_mastery: Record<number, DifficultyMasteryStatus>;
  bloom_mastery: Record<string, BloomMasteryStatus>;
  concept_mastery: Record<string, ConceptMasteryStatus>;
  problem_misconceptions: MisconceptionInfo[];
}

export interface SessionSummary {
  questions_answered: number;
  accuracy_overall: number;
  concepts_mastered: string[];
  concepts_in_progress: string[];
  time_spent_minutes: number;
}

export interface SessionCompletionResponse {
  success: boolean;
  isComplete: boolean;
  completionAnalysis: CompletionAnalysis;
  sessionSummary: SessionSummary;
  nextRecommendation: "COMPLETE" | "CONTINUE";
}

/**
 * Base error handler for API operations
 */
class QuizApiError extends Error {
  constructor(
    public statusCode: number,
    public endpoint: string,
    message: string,
    public originalError?: unknown
  ) {
    super(message);
    this.name = "QuizApiError";
  }
}

/**
 * Main Quiz API Client
 * Centralizes all communication with backend
 */
export class QuizAPIClient {
  private client: AxiosInstance;
  private baseURL: string;
  private defaultTimeout: number = 30000; // 30 seconds

  constructor(baseURL: string = process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:5002/api") {
    this.baseURL = baseURL;

    this.client = axios.create({
      baseURL: this.baseURL,
      timeout: this.defaultTimeout,
      headers: {
        "Content-Type": "application/json",
      },
    });

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      this.handleError.bind(this)
    );

    // Log the configured base URL in development
    if (process.env.NODE_ENV === "development") {
      console.log("[QuizAPIClient] Configured with baseURL:", this.baseURL);
    }
  }

  /**
   * Central error handler
   */
  private handleError(error: AxiosError<ApiError>) {
    const statusCode = error.response?.status || 500;
    let message =
      error.response?.data?.message || error.message || "An unknown error occurred";
    const endpoint = error.config?.url || "unknown";

    // Provide more helpful network error messages
    if (!error.response && error.request) {
      message = `Network Error: Cannot connect to ${this.baseURL}. Is the backend server running?`;
    }

    console.error(`[QuizAPIError] ${statusCode} ${endpoint}: ${message}`);

    throw new QuizApiError(statusCode, endpoint, message, error);
  }

  /**
   * Log API calls (useful for debugging)
   */
  private logCall(method: string, endpoint: string, data?: unknown) {
    if (process.env.NODE_ENV === "development") {
      console.log(`[API] ${method} ${endpoint}`, data);
    }
  }

  /**
   * Chapter name to ID mapping - Maps strategy names to backend chapter IDs
   */
  private getChapterId(chapterName?: string): number {
    const chapterMapping: Record<string, number> = {
      // Chapter 1
      "large_numbers": 1,
      // Chapter 2 - Shapes & Angles (Part 1)
      "clock_angles": 2,
      // Chapter 3 - Shapes & Angles (Part 2)
      "symmetry": 3,
      // Chapter 4 - Shapes & Angles (Part 3)
      "rotation": 4,
      // Chapter 5 - How Many Squares
      "fraction_area": 5,
      // Chapter 6 - Parts & Wholes
      "fractions_decimals": 6,
      // Chapter 7 - Does it Look the Same (Part 1)
      "dice_logic": 7,
      // Chapter 8 - Does it Look the Same (Part 2)
      "nets": 8,
      // Chapter 9 - Be My Multiple
      "factors_multiples": 9,
      // Chapter 10 - Can You See Pattern
      "data_patterns": 10,
      // Chapter 11 - Mapping Your Way
      "mapping": 11,
      // Chapter 12 - Boxes & Sketches (Part 1)
      "cube_counting": 12,
      // Chapter 13 - Area & Measurement
      "geometry_measurement": 13,
      // Chapter 14 - Smart Charts
      "data_handling": 14,
      // Chapter 15 - Ways to Multiply/Divide
      "multiplication_division": 15,
      // Chapter 16 - How Big/Heavy
      "measurement": 16,
    };
    
    if (!chapterName) return 1; // Default to chapter 1
    const normalized = chapterName.toLowerCase().replace(/\s+/g, "_");
    return chapterMapping[normalized] || 1;
  }

  /**
   * Initialize a quiz session
   * 
   * @param gradeLevel - Student grade level (3-10)
   * @param subject - Subject (e.g., "math", "science")
   * @param studentId - Student identifier
   * @param chapterName - Chapter name (optional, defaults to chapter 1)
   * @returns Session configuration with UI settings
   */
  async startSession(
    gradeLevel: number,
    subject: string,
    studentId: string,
    chapterName?: string
  ): Promise<SessionStartResponse> {
    try {
      const chapterId = this.getChapterId(chapterName);
      
      // Backend expects: student_id (int), chapter_id (int), class_level (int), subject (str)
      const payload = {
        student_id: parseInt(studentId.replace(/\D/g, "") || "1"),
        chapter_id: chapterId,
        class_level: gradeLevel,
        subject,
      };
      
      this.logCall("POST", "/practice/session/start", payload);

      const response = await this.client.post(
        "/practice/session/start",
        payload
      );

      // Backend returns snake_case, transform to camelCase for frontend
      const data = response.data as any;
      console.log("[API] Session start response:", data);
      
      if (!data.session_id) {
        throw new Error(`Invalid session response: missing session_id. Received: ${JSON.stringify(data)}`);
      }

      return {
        sessionId: String(data.session_id),
        mode: "PRACTICE",
        classLevel: "3-5",
        uiConfig: {
          theme: "light",
          animationIntensity: "medium",
          fontSize: "medium",
          enableHints: true,
          enableTimer: true,
          enableDifficultyBadge: true,
          enableMasteryDisplay: true,
          enableStreak: true,
          enableAccuracy: true,
          enableConfetti: true,
          enableSound: false,
          enableHapticFeedback: false,
          hintCount: 3,
          hintRevealMode: "progressive",
          showTimer: true,
          feedbackDepth: "moderate",
          showQuestionCounter: true,
        } as any,
        student: {
          id: studentId,
          name: "Student",
          streak: 0,
          masteryScore: 0,
          recentAccuracy: 0,
          learningMomentum: "low" as const,
          totalQuestionsAttempted: 0,
        },
        chapters: [],
      } as SessionStartResponse;
    } catch (error) {
      console.error("[API] Failed to start session:", error);
      throw error;
    }
  }

  /**
   * Get next question for the session
   * 
   * @param sessionId - Current session ID
   * @returns Question with rendering hints and options
   */
  async getNextQuestion(sessionId: string): Promise<NextQuestionResponse> {
    try {
      this.logCall("POST", `/practice/session/${sessionId}/next-question`);

      // Backend requires POST (not GET) for next-question endpoint
      const response = await this.client.post<any>(
        `/practice/session/${sessionId}/next-question`
      );

      const data = response.data;
      
      // Transform backend's string array options into AnswerOption objects
      if (data.options && Array.isArray(data.options)) {
        data.options = data.options.map((optionText: string, index: number) => ({
          id: `option_${index}`,
          label: optionText,
          displayType: "text" as const,
          commonMistake: false,
        }));
      }

      // Transform snake_case fields to camelCase for rich content
      const transformed = {
        questionId: data.question_id,
        topic: data.concept,
        chapterId: String(data.chapter_id),
        difficulty: this.mapDifficulty(data.difficulty),
        bloomLevel: this.mapBloomLevel(data.bloom_level),
        logicalTrapPresent: !!data.logical_trap,
        estimatedTime: 120,
        question: data.question_text,
        options: data.options,
        optionLayout: {
          type: "single-select" as const,
          columns: 1,
          shuffle: false,
          tileStyle: "button" as const,
          tileSize: "medium" as const,
        },
        hintStrategy: {
          available: true,
          allowedCount: 3,
          hints: [],
          showHintButton: true,
          hintButtonPlacement: "bottom" as const,
        },
        renderingHints: {
          emphasizeQuestion: false,
          showVisualSteps: !!data.rich_html_content,
          useGamification: false,
          highlightDifficulty: false,
          showTimeEstimate: false,
          showTrapWarning: !!data.logical_trap,
        },
        richHtmlContent: data.rich_html_content,
        richNarrative: data.rich_narrative,
        visualHints: data.visual_hints,
        correctAnswerId: "option_0", // Will be set by backend if available
        attemptNumber: 1,
      } as NextQuestionResponse;

      return transformed;
    } catch (error) {
      throw error;
    }
  }

  /**
   * Helper to map difficulty float to enum
   */
  private mapDifficulty(difficulty: number): "easy" | "medium" | "hard" {
    if (difficulty < 1.5) return "easy";
    if (difficulty < 2.5) return "medium";
    return "hard";
  }

  /**
   * Helper to map bloom level string to enum
   */
  private mapBloomLevel(
    bloomLevel: string
  ): "recall" | "understand" | "apply" | "analyze" | "evaluate" | "create" {
    const mapping: Record<string, "recall" | "understand" | "apply" | "analyze" | "evaluate" | "create"> = {
      remember: "recall",
      understand: "understand",
      apply: "apply",
      analyze: "analyze",
      evaluate: "evaluate",
      create: "create",
    };
    return mapping[bloomLevel.toLowerCase()] || "recall";
  }

  /**
   * Submit answer for current question
   * 
   * @param sessionId - Current session ID
   * @param questionId - Question ID being answered
   * @param answerId - Selected answer ID (format: "option_0", "option_1", etc.)
   * @param timeSpent - Time spent on question in seconds
   * @returns Feedback, correctness, and mastery update
   */
  async submitAnswer(
    sessionId: string,
    questionId: string,
    answerId: string | string[],
    timeSpent: number = 0
  ): Promise<SubmitAnswerResponse> {
    try {
      // Extract index from option ID (e.g., "option_0" -> 0)
      let selectedIndex = 0;
      if (typeof answerId === 'string') {
        if (answerId.startsWith('option_')) {
          selectedIndex = parseInt(answerId.replace('option_', ''));
        } else {
          selectedIndex = parseInt(answerId);
        }
      } else if (Array.isArray(answerId) && answerId.length > 0) {
        const firstAnswerId = answerId[0];
        if (firstAnswerId.startsWith('option_')) {
          selectedIndex = parseInt(firstAnswerId.replace('option_', ''));
        } else {
          selectedIndex = parseInt(firstAnswerId);
        }
      }

      // Backend expects: question_id (str), selected_index (int), time_taken_seconds (optional int)
      const payload = {
        question_id: questionId,
        selected_index: selectedIndex,
        time_taken_seconds: timeSpent,
      };
      
      const endpoint = `/practice/session/${sessionId}/submit-answer`;
      this.logCall("POST", endpoint, payload);
      
      if (process.env.NODE_ENV === "development") {
        console.log(`[API] Full URL: ${this.baseURL}${endpoint}`);
      }

      const response = await this.client.post<any>(
        endpoint,
        payload
      );

      const data = response.data;
      
      // Transform backend response to frontend format
      const transformed: SubmitAnswerResponse = {
        // Core Result
        isCorrect: data.is_correct || false,
        correctAnswerId: `option_${data.correct_index ?? 0}`,
        correctAnswerLabel: data.answer || "",
        
        // Student's Attempt
        selectedAnswerId: `option_${selectedIndex}`,
        selectedAnswerLabel: "", // Will be filled from question data if available
        attemptNumber: 1,
        timeSpent: timeSpent || 0,
        
        // Adaptive Insights
        misconceptionDetected: undefined,
        logicalTrapTriggered: false,
        trapDetails: undefined,
        
        // Solution
        solution: data.solution_steps ? {
          steps: (data.solution_steps || []).map((step: string, index: number) => ({
            order: index + 1,
            description: step,
            reasoning: "",
          })),
          summary: data.answer || "",
          keyInsight: `Concept: ${data.concept}`,
        } : undefined,
        
        // Mastery Update - Use accuracy as proxy for mastery score
        masteryScore: {
          previous: 0,
          current: Math.round((data.concept_accuracy || 0) * 100),
          delta: Math.round((data.concept_accuracy || 0) * 100),
          method: "adaptive-assessment",
        },
        
        // Streak Update
        streakUpdate: undefined,
        
        // Performance Metrics
        metrics: {
          accuracy: data.overall_accuracy || 0,
          mastery: data.concept_accuracy || 0,
          confidence: (data.concept_accuracy || 0) > 0.7 ? "high" : (data.concept_accuracy || 0) > 0.4 ? "medium" : "low",
        },
        
        // Feedback Configuration
        feedback: {
          showCorrectAnswer: true,
          showSolution: true,
          showExplanation: true,
          showWhyCorrect: true,
          showMisconception: false,
          showTrapWarning: false,
          tone: data.is_correct ? "celebratory" : "corrective" as const,
          mainMessage: data.is_correct ? "Correct!" : "Incorrect",
          depth: "moderate" as const,
          nextAction: data.is_correct ? "continue" : "repeat" as const,
          enableGamification: true,
        },
        
        // Motivational Signal
        motivationTrigger: data.is_correct ? {
          type: "first-correct" as const,
          message: "Great job! Keep it up!",
          celebrationLevel: "moderate" as const,
        } : {
          type: "improvement" as const,
          message: "Let's try another one!",
          celebrationLevel: "subtle" as const,
        },
        
        // Adaptive Sequencing Hint
        nextQuestionHints: {
          difficulty: data.is_correct ? "harder" : "same",
          topic: data.concept || "unknown",
          reason: data.is_correct ? "You got this right, let's increase difficulty" : "Let's reinforce this concept",
          estimatedSuccessProbability: 0.7,
        },
      };

      return transformed;
    } catch (error) {
      console.error("[API] Error submitting answer:", error);
      throw error;
    }
  }

  /**
   * Request a hint for current question
   * 
   * @param sessionId - Current session ID
   * @param questionId - Question ID to get hint for
   * @param hintIndex - Which hint level (0 = first, 1 = second, etc.)
   * @returns Hint content and remaining hint count
   */
  async getHint(
    sessionId: string,
    questionId: string,
    hintIndex: number = 0
  ): Promise<HintResponse> {
    try {
      this.logCall("GET", `/quiz/${sessionId}/hint`, {
        questionId,
        hintIndex,
      });

      const response = await this.client.get<HintResponse>(
        `/quiz/${sessionId}/hint`,
        {
          params: {
            question_id: questionId,
            hint_index: hintIndex,
          },
        }
      );

      return response.data as HintResponse;
    } catch (error) {
      throw error;
    }
  }

  /**
   * Get current session state (for resuming)
   * 
   * @param sessionId - Session ID to resume
   * @returns Full session state including current progress
   */
  async getSessionState(sessionId: string): Promise<SessionStartResponse> {
    try {
      this.logCall("GET", `/quiz/${sessionId}/state`);

      const response = await this.client.get<SessionStartResponse>(
        `/quiz/${sessionId}/state`
      );

      return response.data as SessionStartResponse;
    } catch (error) {
      throw error;
    }
  }

  /**
   * End session and get final results
   * 
   * @param sessionId - Session ID to end
   * @returns Final statistics and recommendations
   */
  async endSession(sessionId: string): Promise<{
    finalScore: number;
    totalQuestions: number;
    correctAnswers: number;
    accuracy: number;
    recommendations: string[];
    masteryGains: Record<string, number>;
  }> {
    try {
      this.logCall("POST", `/quiz/${sessionId}/end`);

      const response = await this.client.post<{
        final_score: number;
        total_questions: number;
        correct_answers: number;
        accuracy: number;
        recommendations: string[];
        mastery_gains: Record<string, number>;
      }>(`/quiz/${sessionId}/end`);

      const data = response.data as {
        final_score: number;
        total_questions: number;
        correct_answers: number;
        accuracy: number;
        recommendations: string[];
        mastery_gains: Record<string, number>;
      };
      return {
        finalScore: data.final_score,
        totalQuestions: data.total_questions,
        correctAnswers: data.correct_answers,
        accuracy: data.accuracy,
        recommendations: data.recommendations,
        masteryGains: data.mastery_gains,
      };
    } catch (error) {
      throw error;
    }
  }

  /**
   * Skip current question (only in practice mode)
   * 
   * @param sessionId - Current session ID
   * @param questionId - Question ID to skip
   * @returns Next question
   */
  async skipQuestion(sessionId: string, questionId: string): Promise<NextQuestionResponse> {
    try {
      this.logCall("POST", `/quiz/${sessionId}/skip`, { questionId });

      const response = await this.client.post<NextQuestionResponse>(
        `/quiz/${sessionId}/skip`,
        {
          question_id: questionId,
        }
      );

      return response.data as NextQuestionResponse;
    } catch (error) {
      throw error;
    }
  }

  /**
   * Flag question for review (in assessment mode)
   * 
   * @param sessionId - Current session ID
   * @param questionId - Question ID to flag
   * @returns Updated session state
   */
  async flagQuestion(sessionId: string, questionId: string): Promise<void> {
    try {
      this.logCall("POST", `/quiz/${sessionId}/flag`, { questionId });

      await this.client.post(`/quiz/${sessionId}/flag`, {
        question_id: questionId,
      });
    } catch (error) {
      throw error;
    }
  }

  /**
   * Get performance analytics for student
   * 
   * @param studentId - Student ID
   * @param gradeLevel - Grade level to get analytics for
   * @returns Analytics including strengths, weaknesses, trends
   */
  async getAnalytics(studentId: string, gradeLevel: number): Promise<{
    totalQuestionsAttempted: number;
    averageAccuracy: number;
    strengths: string[];
    weaknesses: string[];
    progressTrend: number;
  }> {
    try {
      this.logCall("GET", `/analytics/${studentId}/${gradeLevel}`);

      const response = await this.client.get<{
        total_questions_attempted: number;
        average_accuracy: number;
        strengths: string[];
        weaknesses: string[];
        progress_trend: number;
      }>(`/analytics/${studentId}/${gradeLevel}`);

      const data = response.data as {
        total_questions_attempted: number;
        average_accuracy: number;
        strengths: string[];
        weaknesses: string[];
        progress_trend: number;
      };
      return {
        totalQuestionsAttempted: data.total_questions_attempted,
        averageAccuracy: data.average_accuracy,
        strengths: data.strengths,
        weaknesses: data.weaknesses,
        progressTrend: data.progress_trend,
      };
    } catch (error) {
      throw error;
    }
  }

  /**
   * Health check - verify API is accessible
   */
  async healthCheck(): Promise<boolean> {
    try {
      this.logCall("GET", "/health");
      const response = await this.client.get("/health");
      return response.status === 200;
    } catch (error) {
      console.warn("Health check failed:", error);
      return false;
    }
  }

  /**
   * Check if session completion criteria are met
   * 
   * 4-Dimensional Mastery Check:
   * 1. Difficulty levels 1-5: ALL ≥80% accuracy + 3 attempts
   * 2. Bloom cognitive levels: ALL ≥80% accuracy + 2 attempts
   * 3. All concepts: ≥80% accuracy each
   * 4. No problematic misconceptions (2+ same type = problem)
   * 
   * @param sessionId - Current session ID
   * @returns Completion status with detailed analysis
   */
  async checkSessionCompletion(sessionId: string): Promise<SessionCompletionResponse> {
    try {
      this.logCall("GET", `/practice/session/${sessionId}/check-completion`);

      const response = await this.client.get<any>(
        `/practice/session/${sessionId}/check-completion`
      );

      const data = response.data;
      
      // Transform backend's snake_case response to camelCase
      // Backend returns: is_complete, completion_analysis, session_summary, next_recommendation
      return {
        success: data.success || false,
        isComplete: data.is_complete || data.isComplete || false,
        completionAnalysis: {
          difficulty_mastery: data.completion_analysis?.difficulty_mastery || {},
          bloom_mastery: data.completion_analysis?.bloom_mastery || {},
          concept_mastery: data.completion_analysis?.concept_mastery || {},
          problem_misconceptions: data.completion_analysis?.problem_misconceptions || [],
        },
        sessionSummary: {
          questions_answered: data.session_summary?.questions_answered || 0,
          accuracy_overall: data.session_summary?.accuracy_overall || 0,
          concepts_mastered: data.session_summary?.concepts_mastered || [],
          concepts_in_progress: data.session_summary?.concepts_in_progress || [],
          time_spent_minutes: data.session_summary?.time_spent_minutes || 0,
        },
        nextRecommendation: (data.next_recommendation || data.nextRecommendation || "CONTINUE") as "COMPLETE" | "CONTINUE",
      } as SessionCompletionResponse;
    } catch (error) {
      console.error("[API] Error checking session completion:", error);
      throw error;
    }
  }

  /**
   * Set custom timeout for slow connections
   */
  setTimeout(ms: number) {
    this.defaultTimeout = ms;
    this.client.defaults.timeout = ms;
  }

  /**
   * Set authentication token (if needed)
   */
  setAuthToken(token: string) {
    this.client.defaults.headers.common["Authorization"] = `Bearer ${token}`;
  }

  /**
   * Clear authentication token
   */
  clearAuthToken() {
    delete this.client.defaults.headers.common["Authorization"];
  }
}

/**
 * Singleton instance - can be used throughout app
 */
let apiClientInstance: QuizAPIClient | null = null;

export function getQuizAPIClient(): QuizAPIClient {
  if (!apiClientInstance) {
    apiClientInstance = new QuizAPIClient();
  }
  return apiClientInstance;
}

/**
 * Reset instance (useful for testing)
 */
export function resetQuizAPIClient() {
  apiClientInstance = null;
}
