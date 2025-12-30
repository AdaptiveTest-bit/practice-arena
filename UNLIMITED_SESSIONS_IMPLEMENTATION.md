# QUICK START: Enable Unlimited Practice Sessions

## The 4-Step Implementation (7 hours total)

### STEP 1: Backend - Add Completion Detection (1 hour)

**File:** `backend/services/session_manager.py`

Add this method to the `SessionManager` class:

```python
def check_session_completion(self, session_id: int) -> Dict[str, Any]:
    """
    Check if student has achieved mastery across all dimensions.
    
    Criteria (ALL must be met):
    1. Difficulty 1-5: ALL ≥80% accuracy
    2. Bloom's Remember-Apply: ALL ≥80% accuracy  
    3. All concepts: ≥80% accuracy each
    4. No problematic misconceptions (2+ errors in same type)
    """
    session = get_practice_session(session_id)
    if not session:
        return {
            "success": False,
            "error": "Session not found",
            "is_complete": False
        }
    
    # ===== CHECK 1: DIFFICULTY MASTERY (1-5) =====
    difficulty_mastery = {}
    all_difficulties_mastered = True
    
    for difficulty in range(1, 6):
        difficulty_stats = session.difficulty_mastery.get(str(difficulty), {
            "attempts": 0,
            "correct": 0,
            "accuracy": 0.0
        })
        accuracy = difficulty_stats.get("accuracy", 0.0)
        attempts = difficulty_stats.get("attempts", 0)
        
        difficulty_mastery[difficulty] = {
            "accuracy": accuracy,
            "attempts": attempts,
            "mastered": accuracy >= 0.80 and attempts >= 3,
            "status": "✅ Mastered" if (accuracy >= 0.80 and attempts >= 3) 
                      else ("⚠️ In Progress" if accuracy >= 0.70 
                      else "❌ Weak")
        }
        
        if not (accuracy >= 0.80 and attempts >= 3):
            all_difficulties_mastered = False
    
    # ===== CHECK 2: BLOOM'S LEVEL MASTERY =====
    bloom_mastery = {}
    all_bloom_levels_mastered = True
    required_bloom_levels = ["remember", "understand", "apply", "analyze"]
    
    for level in required_bloom_levels:
        level_stats = session.bloom_levels_completed.get(level, {
            "attempts": 0,
            "correct": 0,
            "accuracy": 0.0
        })
        accuracy = level_stats.get("accuracy", 0.0)
        attempts = level_stats.get("attempts", 0)
        
        bloom_mastery[level] = {
            "accuracy": accuracy,
            "attempts": attempts,
            "mastered": accuracy >= 0.80 and attempts >= 2,
            "status": "✅ Mastered" if (accuracy >= 0.80 and attempts >= 2)
                      else ("⚠️ In Progress" if accuracy >= 0.70
                      else "❌ Weak")
        }
        
        if not (accuracy >= 0.80 and attempts >= 2):
            all_bloom_levels_mastered = False
    
    # ===== CHECK 3: CONCEPT MASTERY =====
    concept_mastery = {}
    all_concepts_mastered = True
    
    accuracy_by_concept = session.accuracy_by_concept or {}
    for concept, stats in accuracy_by_concept.items():
        accuracy = stats.get("accuracy", 0.0)
        attempts = stats.get("total", 0)
        
        concept_mastery[concept] = {
            "accuracy": accuracy,
            "attempts": attempts,
            "mastered": accuracy >= 0.80,
            "status": "✅ Mastered" if accuracy >= 0.80
                      else ("⚠️ In Progress" if accuracy >= 0.70
                      else "❌ Weak")
        }
        
        if not (accuracy >= 0.80):
            all_concepts_mastered = False
    
    # ===== CHECK 4: MISCONCEPTIONS =====
    problem_misconceptions = session.get_problem_misconceptions()
    has_problems = len(problem_misconceptions) > 0
    
    # ===== DETERMINE COMPLETION =====
    is_complete = (
        all_difficulties_mastered and
        all_bloom_levels_mastered and
        all_concepts_mastered and
        not has_problems
    )
    
    return {
        "success": True,
        "is_complete": is_complete,
        "completion_analysis": {
            "difficulty_mastery": difficulty_mastery,
            "bloom_mastery": bloom_mastery,
            "concept_mastery": concept_mastery,
            "problem_misconceptions": [
                {
                    "type": m.value,
                    "count": session.misconceptions[m.value]["encounter_count"]
                }
                for m in problem_misconceptions
            ]
        },
        "session_summary": {
            "questions_answered": session.questions_answered,
            "accuracy_overall": round(
                session.accuracy_by_concept.get("overall", {}).get("accuracy", 0) * 100, 1
            ),
            "concepts_mastered": session.concepts_mastered or [],
            "concepts_in_progress": [
                c for c in session.concepts_covered 
                if c not in (session.concepts_mastered or [])
            ],
            "time_spent_minutes": (
                (datetime.now() - session.created_at).total_seconds() / 60
                if session.created_at else 0
            )
        },
        "next_recommendation": (
            "COMPLETE" if is_complete
            else (self._get_next_recommendation(session))
        )
    }

def _get_next_recommendation(self, session) -> str:
    """Get recommendation for what student should work on next."""
    progress_svc = session.adaptive_engine  # Reuse existing logic
    recommendation = progress_svc.get_next_recommendation(session.student_progress)
    return recommendation.action.upper()  # "REMEDIATE", "RETREAT", "ADVANCE", "REINFORCE"
```

### STEP 2: Backend - Add API Endpoint (30 mins)

**File:** `backend/routes/practice_routes.py`

Add this endpoint:

```python
from models.session_models import SessionCompletionResponse

@router.get(
    "/practice/session/{session_id}/check-completion",
    response_model=SessionCompletionResponse,
    summary="Check if student achieved mastery",
    tags=["Session Management"]
)
async def check_session_completion(
    session_id: int,
    sm: SessionManager = Depends(get_session_manager)
) -> SessionCompletionResponse:
    """
    Check if student has achieved mastery across all dimensions.
    
    Returns:
    - is_complete: True if mastery achieved
    - completion_analysis: Breakdown of each dimension
    - session_summary: Stats and progress
    - next_recommendation: What student should work on next
    """
    try:
        result = sm.check_session_completion(session_id)
        
        return SessionCompletionResponse(
            success=result["success"],
            isComplete=result["is_complete"],
            completionAnalysis=result["completion_analysis"],
            sessionSummary=result["session_summary"],
            nextRecommendation=result["next_recommendation"]
        )
    except Exception as e:
        logger.error(f"Error checking session completion: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

### STEP 3: Frontend - Remove 5-Question Hard Limit (1.5 hours)

**File:** `frontend/app/practice/page.tsx`

**Find (around line 155-165, in `handleLoadNext` function):**
```tsx
const handleLoadNext = async () => {
  if (!sessionId) return
  await loadNextQuestion(sessionId)
}
```

**Replace with:**
```tsx
const handleLoadNext = async () => {
  if (!sessionId) return

  try {
    // ✅ NEW: Check session completion with backend before loading next
    const completionCheck = await practiceAPI.checkSessionCompletion(sessionId)

    if (completionCheck.isComplete) {
      // Mastery achieved! End session and show completion screen
      setCurrentQuestion(null)
      setSessionId(null)
      toast.success('🎉 Chapter Mastered! Excellent work!')
      // Optionally navigate to chapters or show completion summary
      setTimeout(() => {
        window.location.href = '/chapters'
      }, 2000)
    } else {
      // More to learn - fetch next question
      await loadNextQuestion(sessionId)
    }
  } catch (err) {
    const msg = err instanceof Error ? err.message : 'Failed to check completion'
    setError(msg)
    toast.error('❌ ' + msg)
  }
}
```

### STEP 4: Frontend - Add API Method (30 mins)

**File:** `frontend/lib/api/client.ts` (or the practiceAPI client being used)

The `practiceAPI` object should have this method added:

```typescript
async checkSessionCompletion(sessionId: string): Promise<SessionCompletionResponse> {
  const response = await fetch(
    `/api/practice/session/${sessionId}/check-completion`,
    {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to check session completion: ${response.statusText}`);
  }

  return response.json();
}
```

Or if using axios (like in quizClient):
```typescript
async checkSessionCompletion(sessionId: string): Promise<SessionCompletionResponse> {
  try {
    const response = await this.client.get<SessionCompletionResponse>(
      `/practice/session/${sessionId}/check-completion`
    );
    return response.data;
  } catch (error) {
    throw error;
  }
}
```

### STEP 5: Frontend - Create Completion Summary Component (1.5 hours)

**File:** `frontend/app/practice/components/CompletionSummary.tsx` (NEW FILE)

```tsx
'use client'

import React from 'react'
import Link from 'next/link'
import { SessionCompletionResponse } from '@/lib/types'

interface CompletionSummaryProps {
  completionData: SessionCompletionResponse
  chapterName: string
  onNewSession: () => void
}

export const CompletionSummary: React.FC<CompletionSummaryProps> = ({
  completionData,
  chapterName,
  onNewSession,
}) => {
  const { sessionSummary, completionAnalysis } = completionData

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-blue-50 to-purple-50 py-12 px-4">
      <div className="max-w-4xl mx-auto space-y-8">
        {/* 🎉 CELEBRATION HEADER */}
        <div className="text-center space-y-4">
          <div className="text-8xl animate-bounce">🎉</div>
          <h1 className="text-5xl font-black bg-clip-text text-transparent bg-gradient-to-r from-green-600 via-blue-600 to-purple-600">
            Chapter Mastered!
          </h1>
          <p className="text-xl text-gray-600">
            You've achieved mastery of <span className="font-bold text-blue-600">{chapterName}</span>
          </p>
        </div>

        {/* 📊 STATISTICS */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-3xl p-8 shadow-lg border-2 border-blue-200 text-center">
            <div className="text-5xl font-black text-blue-600 mb-2">
              {sessionSummary.questions_answered}
            </div>
            <p className="text-gray-600 font-semibold">Questions Answered</p>
          </div>

          <div className="bg-white rounded-3xl p-8 shadow-lg border-2 border-green-200 text-center">
            <div className="text-5xl font-black text-green-600 mb-2">
              {Math.round(sessionSummary.accuracy_overall)}%
            </div>
            <p className="text-gray-600 font-semibold">Overall Accuracy</p>
          </div>

          <div className="bg-white rounded-3xl p-8 shadow-lg border-2 border-purple-200 text-center">
            <div className="text-5xl font-black text-purple-600 mb-2">
              {Math.round(sessionSummary.time_spent_minutes)}
            </div>
            <p className="text-gray-600 font-semibold">Minutes Spent</p>
          </div>
        </div>

        {/* 📈 MASTERY BREAKDOWN */}
        <div className="space-y-6">
          {/* DIFFICULTY MASTERY */}
          <div className="bg-white rounded-3xl p-8 shadow-lg border-l-4 border-blue-500">
            <h3 className="text-2xl font-bold text-gray-900 mb-6">📊 Difficulty Mastery</h3>
            <div className="space-y-3">
              {Object.entries(completionAnalysis.difficulty_mastery).map(
                ([difficulty, stats]: any) => (
                  <div key={difficulty} className="flex items-center gap-4">
                    <span className="font-bold text-gray-700 w-20">Level {difficulty}</span>
                    <div className="flex-1 h-3 bg-gray-200 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-blue-400 to-blue-600 rounded-full transition-all"
                        style={{ width: `${Math.min(stats.accuracy * 100, 100)}%` }}
                      ></div>
                    </div>
                    <span className="font-bold w-16 text-right">
                      {Math.round(stats.accuracy * 100)}%
                    </span>
                    <span className="text-2xl">{stats.status}</span>
                  </div>
                )
              )}
            </div>
          </div>

          {/* BLOOM'S MASTERY */}
          <div className="bg-white rounded-3xl p-8 shadow-lg border-l-4 border-purple-500">
            <h3 className="text-2xl font-bold text-gray-900 mb-6">🧠 Cognitive Levels</h3>
            <div className="space-y-3">
              {Object.entries(completionAnalysis.bloom_mastery).map(
                ([level, stats]: any) => (
                  <div key={level} className="flex items-center gap-4">
                    <span className="font-bold text-gray-700 w-24 capitalize">{level}</span>
                    <div className="flex-1 h-3 bg-gray-200 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-purple-400 to-purple-600 rounded-full transition-all"
                        style={{ width: `${Math.min(stats.accuracy * 100, 100)}%` }}
                      ></div>
                    </div>
                    <span className="font-bold w-16 text-right">
                      {Math.round(stats.accuracy * 100)}%
                    </span>
                    <span className="text-2xl">{stats.status}</span>
                  </div>
                )
              )}
            </div>
          </div>

          {/* CONCEPTS MASTERED */}
          {sessionSummary.concepts_mastered.length > 0 && (
            <div className="bg-white rounded-3xl p-8 shadow-lg border-l-4 border-green-500">
              <h3 className="text-2xl font-bold text-gray-900 mb-6">✅ Concepts Mastered</h3>
              <div className="flex flex-wrap gap-3">
                {sessionSummary.concepts_mastered.map((concept) => (
                  <span
                    key={concept}
                    className="bg-gradient-to-r from-green-400 to-green-600 text-white px-6 py-2 rounded-full font-bold shadow-md"
                  >
                    ✓ {concept.replace(/_/g, ' ')}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* 🎯 NEXT ACTIONS */}
        <div className="flex gap-4 justify-center flex-wrap">
          <button
            onClick={onNewSession}
            className="bg-gradient-to-r from-blue-500 to-blue-700 hover:from-blue-600 hover:to-blue-800 text-white font-bold py-4 px-8 rounded-2xl transition-all transform hover:scale-105 active:scale-95 shadow-lg text-lg"
          >
            🔄 Practice Again
          </button>
          <Link
            href="/chapters"
            className="bg-gradient-to-r from-gray-400 to-gray-600 hover:from-gray-500 hover:to-gray-700 text-white font-bold py-4 px-8 rounded-2xl transition-all transform hover:scale-105 active:scale-95 shadow-lg text-lg inline-block text-center"
          >
            ← Back to Chapters
          </Link>
        </div>
      </div>
    </div>
  )
}

export default CompletionSummary
```

### STEP 6: Wire Components Together (30 mins)

**File:** `frontend/app/practice/page.tsx`

Add import at the top:
```tsx
import { CompletionSummary } from './components/CompletionSummary'
```

Add state for completion data (in `PracticePageInner` function):
```tsx
const [completionData, setCompletionData] = useState<SessionCompletionResponse | null>(null)
```

Update the `handleLoadNext` function to handle completion:
```tsx
const handleLoadNext = async () => {
  if (!sessionId) return

  try {
    setIsLoading(true)
    // ✅ Check session completion with backend
    const completion = await practiceAPI.checkSessionCompletion(sessionId)

    if (completion.isComplete) {
      // Mastery achieved! Show completion summary
      setCompletionData(completion)
      setCurrentQuestion(null)
      toast.success('🎉 Chapter Mastered!')
    } else {
      // More to learn - fetch next question
      await loadNextQuestion(sessionId)
    }
  } catch (err) {
    const msg = err instanceof Error ? err.message : 'Failed to check completion'
    setError(msg)
    toast.error('❌ ' + msg)
  } finally {
    setIsLoading(false)
  }
}
```

Update the return JSX to show completion when done (replace the loading/error sections):
```tsx
// Show completion summary if mastery achieved
if (completionData) {
  return (
    <CompletionSummary
      completionData={completionData}
      chapterName={chapterName}
      onNewSession={startNewSession}
    />
  )
}

// ... rest of your existing UI
```

---

## Testing Checklist

- [ ] Backend: `check_session_completion()` returns correct mastery status
- [ ] Backend: API endpoint `/practice/session/{id}/check-completion` works
- [ ] Frontend: 5-question limit removed
- [ ] Frontend: API call to check completion happens
- [ ] Frontend: Session continues past 5 questions if not mastered
- [ ] Frontend: Session ends when mastery achieved
- [ ] Frontend: Completion summary displays correctly
- [ ] Frontend: Next chapter button works
- [ ] E2E: Student can practice unlimited until mastery

---

## Estimated Time

- Step 1 (Backend): 1 hour
- Step 2 (API): 30 mins
- Step 3 (Frontend remove limit): 1.5 hours
- Step 4 (API client): 30 mins
- Step 5 (Completion UI): 2 hours
- Step 6 (Wire together): 30 mins
- Testing: 1 hour

**Total: ~7 hours**

Start with Step 1 & 2 for the backend, then Step 3 & 4 for frontend basic support, then Step 5 & 6 for the nice UI.
