/**
 * BACKEND-DRIVEN ADAPTIVE QUIZ SYSTEM
 * Complete TypeScript interface definitions for all API contracts
 * between backend and frontend.
 * 
 * Philosophy: Backend controls ALL UI behavior through configuration.
 * Frontend is a dumb renderer that responds to these signals.
 */

// ============================================================================
// SESSION & CONFIGURATION
// ============================================================================

export interface SessionStartResponse {
  // Session Identity
  sessionId: string;
  
  // Mode
  mode: "PRACTICE" | "TEST";
  
  // Class Level (affects UI typography, complexity)
  classLevel: "3-5" | "6-8" | "9-10";
  
  // UI Configuration (controls all visual behavior)
  uiConfig: {
    // Theme & Visual
    theme: "light" | "dark" | "colorful" | "high-contrast";
    animationIntensity: "low" | "medium" | "high";
    fontSize: "small" | "medium" | "large";
    
    // Features (on/off)
    enableHints: boolean;
    enableTimer: boolean;
    enableDifficultyBadge: boolean;
    enableMasteryDisplay: boolean;
    enableStreak: boolean;
    enableAccuracy: boolean;
    enableConfetti: boolean;
    enableSound: boolean;
    enableHapticFeedback: boolean;
    
    // Hint Configuration
    hintCount: number;
    hintRevealMode: "progressive" | "all-at-once";
    
    // Time
    timeLimit?: number;
    showTimer: boolean;
    timerWarningThreshold?: number;
    
    // Feedback
    feedbackDepth: "minimal" | "moderate" | "detailed";
    
    // Session Length
    questionCount?: number;
    showQuestionCounter: boolean;
    
    // Feature Flags
    featureFlags?: {
      enableNewFeedbackUI?: boolean;
      enableAdaptiveHints?: boolean;
      enableMisconceptionExplanation?: boolean;
      [key: string]: boolean | undefined;
    };
  };
  
  // Student State
  student: {
    id: string;
    name: string;
    streak: number;
    masteryScore: number;
    recentAccuracy: number;
    learningMomentum: "low" | "building" | "high";
    totalQuestionsAttempted: number;
  };
  
  // Available chapters/topics
  chapters: Array<{
    id: string;
    name: string;
    topicCount: number;
    masteryLevel: number;
  }>;
}

// ============================================================================
// QUESTION RENDERING
// ============================================================================

export interface DataRepresentation {
  type: "image" | "diagram" | "table" | "video" | "interactive-model";
  url: string;
  alt: string;
  caption?: string;
  showCaption?: boolean;
}

export interface QuestionDataRepresentation {
  primary?: DataRepresentation;
  secondary?: DataRepresentation[];
}

export interface AnswerOption {
  id: string;
  label: string;
  displayType: "text" | "image" | "icon-text" | "equation" | "diagram";
  icon?: string;
  imageUrl?: string;
  
  misconceptionTarget?: {
    id: string;
    name: string;
    explanation?: string;
  };
  
  isTrap?: boolean;
  trapExplanation?: string;
  
  selectionFrequency?: number;
  commonMistake?: boolean;
}

export interface HintItem {
  id: string;
  order: number;
  type: "conceptual" | "visual" | "example" | "elimination" | "process";
  
  content: string;
  visualUrl?: string;
  
  showAfterAttempts?: number;
  showBeforeAttempts?: number;
  
  severity: "light" | "moderate" | "heavy";
  
  helpfulnessScore?: number;
}

export interface NextQuestionResponse {
  // Question Identity
  questionId: string;
  topic: string;
  subtopic?: string;
  chapterId: string;
  
  // Question Metadata
  difficulty: "easy" | "medium" | "hard";
  bloomLevel: "recall" | "understand" | "apply" | "analyze" | "evaluate" | "create";
  
  // Misconception & Trap Info
  misconceptionTag?: string;
  logicalTrapPresent: boolean;
  estimatedTime: number;
  
  // Question Content
  question: string;
  questionContext?: string;
  dataRepresentation?: QuestionDataRepresentation;
  
  // Answer Options
  options: AnswerOption[];
  
  // How to render options
  optionLayout: {
    type: 
      | "single-select" 
      | "multi-select" 
      | "drag-drop" 
      | "numeric-input" 
      | "equation-editor"
      | "matching";
    
    columns?: 1 | 2 | 3 | 4;
    shuffle: boolean;
    selectMultiple?: number;
    
    tileStyle: "button" | "card" | "pill" | "image-card";
    tileSize: "small" | "medium" | "large";
  };
  
  // Hint Strategy
  hintStrategy: {
    available: boolean;
    allowedCount: number;
    hints: HintItem[];
    showHintButton: boolean;
    hintButtonPlacement: "top" | "bottom" | "floating";
  };
  
  // Rendering Hints
  renderingHints: {
    emphasizeQuestion: boolean;
    showVisualSteps: boolean;
    useGamification: boolean;
    highlightDifficulty: boolean;
    showTimeEstimate: boolean;
    showTrapWarning: boolean;
  };
  
  // Rich Content from Hybrid Neuro-Symbolic Pipeline
  richHtmlContent?: string;
  richNarrative?: string;
  visualHints?: string[];
  
  // Correct answer
  correctAnswerId: string;
  
  // Adaptive context
  attemptNumber: number;
  previousAttempt?: {
    selectedAnswerId: string;
    timeSpent: number;
    misconceptionDetected?: string;
  };
}

// ============================================================================
// ANSWER SUBMISSION & FEEDBACK
// ============================================================================

export interface MisconceptionInfo {
  id?: string;
  name?: string;
  type?: string;
  category?: string;
  explanation: string;
  correctionExample?: string;
  learnMoreUrl?: string;
  count?: number;
}

export interface LogicalTrapInfo {
  id?: string;
  type?: "distractor" | "common-mistake" | "similar-operation" | "order-of-operations" | string;
  explanation: string;
  preventionStrategy?: string;
  difficulty?: string;
}

export interface SolutionStep {
  order: number;
  description: string;
  visual?: DataRepresentation;
  reasoning?: string;
  commonMistake?: string;
}

export interface MotivationTrigger {
  type: 
    | "streak-milestone" 
    | "mastery-jump" 
    | "concept-mastery" 
    | "improvement"
    | "first-correct"
    | "consistency";
  
  message: string;
  emoji?: string;
  celebrationLevel: "subtle" | "moderate" | "explosive";
}

export interface FeedbackConfig {
  // What to show
  showCorrectAnswer: boolean;
  showSolution: boolean;
  showExplanation: boolean;
  showWhyCorrect: boolean;
  showMisconception: boolean;
  showTrapWarning: boolean;
  
  // Text Customization
  tone: "encouraging" | "neutral" | "corrective" | "celebratory";
  mainMessage: string;
  secondaryMessage?: string;
  
  // Depth of Feedback
  depth: "minimal" | "moderate" | "detailed";
  
  // Next Action Suggestion
  nextAction: 
    | "continue" 
    | "repeat" 
    | "request-hint" 
    | "concept-review" 
    | "similar-problem";
  
  // Gamification
  enableGamification: boolean;
}

export interface SubmitAnswerResponse {
  // Core Result
  isCorrect: boolean;
  correctAnswerId: string;
  correctAnswerLabel: string;
  
  // Student's Attempt
  selectedAnswerId: string | string[];
  selectedAnswerLabel: string | string[];
  attemptNumber: number;
  timeSpent: number;
  
  // Adaptive Insights
  misconceptionDetected?: MisconceptionInfo;
  logicalTrapTriggered: boolean;
  trapDetails?: LogicalTrapInfo;
  
  // Solution
  solution?: {
    steps: SolutionStep[];
    summary: string;
    keyInsight?: string;
  };
  
  // Mastery Update
  masteryScore: {
    previous: number;
    current: number;
    delta: number;
    method?: string;
  };
  
  // Streak Update
  streakUpdate?: {
    current: number;
    previous: number;
    milestone?: number;
  };
  
  // Performance Metrics
  metrics?: {
    averageTimePerQuestion?: number;
    accuracy?: number;
    mastery?: number;
    confidence?: "high" | "medium" | "low";
  };
  
  // Feedback Configuration
  feedback: FeedbackConfig;
  
  // Motivational Signal
  motivationTrigger?: MotivationTrigger;
  
  // Adaptive Sequencing Hint
  nextQuestionHints?: {
    difficulty: "same" | "easier" | "harder";
    topic: string;
    reason: string;
    estimatedSuccessProbability?: number;
  };
  
  // Learning Analytics
  learningOpportunity?: {
    concept: string;
    difficulty: string;
    nextRecommendedTopic?: string;
  };
}

// ============================================================================
// HINT REQUEST
// ============================================================================

export interface HintResponse {
  // Content
  hintContent: string;
  hintType: "conceptual" | "visual" | "example" | "elimination" | "process";
  
  // State
  hintIndex: number;
  remainingHints: number;
  maxHints: number;
  
  // Severity
  severity: "light" | "moderate" | "heavy";
  
  // UI Configuration
  displayFormat: "text" | "image" | "video" | "interactive";
  shouldDisableSubmit?: boolean;
}

// ============================================================================
// QUIZ EVENTS (ANALYTICS)
// ============================================================================

export type QuizEventType =
  | "SESSION_START"
  | "QUESTION_LOADED"
  | "QUESTION_VIEWED"
  | "ANSWER_SELECTED"
  | "ANSWER_SUBMITTED"
  | "HINT_REQUESTED"
  | "HINT_CONSUMED"
  | "FEEDBACK_VIEWED"
  | "MISCONCEPTION_DETECTED"
  | "TRAP_TRIGGERED"
  | "MILESTONE_REACHED"
  | "SESSION_END"
  | "ERROR_OCCURRED";

export interface QuizEvent {
  type: QuizEventType;
  sessionId: string;
  timestamp: number;
  
  questionId?: string;
  attemptNumber?: number;
  
  data?: {
    [key: string]: any;
  };
}

// ============================================================================
// COMPONENT PROPS (FRONTEND)
// ============================================================================

export interface QuestionCardProps {
  question: NextQuestionResponse;
  config: SessionStartResponse["uiConfig"];
  onQuestionLoaded?: () => void;
  className?: string;
}

export interface OptionTileProps {
  option: AnswerOption;
  optionNumber: number;
  isSelected: boolean;
  isSubmitted: boolean;
  isCorrect?: boolean;
  showMisconceptionPreview: boolean;
  onSelect: (optionId: string) => void;
  config: SessionStartResponse["uiConfig"];
  className?: string;
}

export interface FeedbackPanelProps {
  response: SubmitAnswerResponse;
  config: SessionStartResponse["uiConfig"];
  classLevel: "3-5" | "6-8" | "9-10";
  onContinue: () => void;
  onRequestHint?: () => void;
  className?: string;
}

export interface HintDrawerProps {
  hintStrategy: NextQuestionResponse["hintStrategy"];
  usedHintCount: number;
  onHintRequested: () => Promise<HintResponse>;
  config: SessionStartResponse["uiConfig"];
  className?: string;
}

export interface ProgressBarProps {
  student: SessionStartResponse["student"];
  questionNumber: number;
  totalQuestions?: number;
  config: SessionStartResponse["uiConfig"];
  className?: string;
}

export interface RewardToastProps {
  trigger?: MotivationTrigger;
  config: SessionStartResponse["uiConfig"];
  onDismiss?: () => void;
  className?: string;
}

export interface AdaptiveQuizScreenProps {
  sessionId: string;
  mode: "PRACTICE" | "TEST";
  classLevel: "3-5" | "6-8" | "9-10";
  
  onFetchSessionConfig: () => Promise<SessionStartResponse>;
  onFetchNextQuestion: (sessionId: string) => Promise<NextQuestionResponse>;
  onSubmitAnswer: (sessionId: string, answerId: string | string[]) => Promise<SubmitAnswerResponse>;
  onRequestHint: (sessionId: string, questionId: string) => Promise<HintResponse>;
  
  onEvent?: (event: QuizEvent) => void;
  onSessionEnd?: (finalScore: number) => void;
  
  className?: string;
}

// ============================================================================
// STATE MANAGEMENT
// ============================================================================

export interface QuizSessionState {
  // Session
  sessionId: string;
  mode: "PRACTICE" | "TEST";
  classLevel: "3-5" | "6-8" | "9-10";
  
  // Configuration
  uiConfig: SessionStartResponse["uiConfig"];
  
  // Current Question
  currentQuestion: NextQuestionResponse | null;
  selectedAnswerId: string | null;
  isSubmitted: boolean;
  
  // Student State
  student: SessionStartResponse["student"];
  
  // Session Progress
  questionsAttempted: number;
  correctCount: number;
  incorrectCount: number;
  
  // UI State
  showFeedback: boolean;
  showHintDrawer: boolean;
  usedHintCount: number;
  rewardToast?: MotivationTrigger;
  
  // Loading
  isLoading: boolean;
  error: ApiError | null;
}

// ============================================================================
// ERROR HANDLING
// ============================================================================

export interface ApiError {
  code: string;
  message: string;
  details?: {
    field?: string;
    reason?: string;
  };
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: ApiError;
  timestamp: number;
}

// ============================================================================
// FEATURE FLAGS
// ============================================================================

export interface FeatureFlagConfig {
  [featureName: string]: {
    enabled: boolean;
    variant?: "A" | "B" | "C";
    config?: Record<string, any>;
  };
}

// ============================================================================
// SESSION COMPLETION
// ============================================================================

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

export interface CompletionAnalysis {
  difficulty_mastery: Record<number, DifficultyMasteryStatus>;
  bloom_mastery: Record<string, BloomMasteryStatus>;
  concept_mastery: Record<string, ConceptMasteryStatus>;
  problem_misconceptions: Array<{ type: string; count: number }>;
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
  is_complete: boolean;
  completion_analysis: CompletionAnalysis;
  session_summary: SessionSummary;
  next_recommendation: "COMPLETE" | "CONTINUE";
}

export type SessionCompletionData = SessionCompletionResponse;
