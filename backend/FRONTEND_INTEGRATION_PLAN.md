# Frontend-Backend Integration Plan: Adaptive Sequencing

## Goal
Wire the new `domain/adaptation/` (ConceptGraph, MasteryTracker, Sequencer) into the existing quiz API so students experience **adaptive question selection**.

---

## Architecture Changes

### Current Flow (Random/Static)
```
Frontend → /api/quiz/{session}/question → SessionAdapter → QuestionBankService → Random question from YAML
```

### New Flow (Adaptive)
```
Frontend → /api/quiz/{session}/question → SessionAdapter → AdaptiveQuestionSelector
                                                            ↓
                                        ┌───────────────────┼───────────────────┐
                                        ↓                   ↓                   ↓
                                   ConceptGraph      MasteryTracker        Sequencer
                                   (prerequisites)   (student state)    (next target)
                                        ↓                   ↓                   ↓
                                        └───────────────────┼───────────────────┘
                                                            ↓
                                              FactorsMultiplesGenerator.generate_targeted()
```

---

## Implementation Steps

### Step 1: Create AdaptiveQuestionSelector service
**File**: `backend/domain/adaptation/selector.py`

This service:
- Takes a `student_id` and `chapter_key`
- Uses `Sequencer.get_next_target()` to get optimal concept + difficulty
- Calls the appropriate generator with those parameters
- Returns a fully formed question

### Step 2: Integrate into SessionAdapter
**File**: `backend/domain/session_management/service.py`

Modify `get_next_question()` to:
1. Load student's mastery state from DB
2. Call `AdaptiveQuestionSelector.select_question()`
3. Record the served question event

### Step 3: Track mastery on answer submission
**File**: `backend/domain/session_management/service.py`

Modify `submit_answer()` to:
1. Update `MasteryTracker` with attempt result
2. Persist mastery state to DB
3. Return enriched feedback with mastery info

### Step 4: Add mastery endpoints for frontend
**File**: `backend/app_main.py`

New endpoints:
- `GET /api/student/{id}/mastery` - Get concept mastery levels
- `GET /api/quiz/{session}/progress` - Get session progress with mastery

### Step 5: Frontend integration
**Files**: `frontend/components/`, `frontend/lib/`

- Display mastery progress bar per concept
- Show "concept unlocked" notifications
- Show targeted misconception feedback

---

## Files to Create/Modify

| File | Action | Purpose |
|------|--------|---------|
| `domain/adaptation/selector.py` | CREATE | Orchestrates adaptive selection |
| `domain/session_management/service.py` | MODIFY | Wire in adaptive selector |
| `app_main.py` | MODIFY | Add mastery endpoints |
| `db/models/mastery.py` | CREATE | Persist mastery state |
| `alembic/versions/xxx_add_mastery.py` | CREATE | DB migration |

---

## Execution Order

1. ✅ Create `selector.py` with AdaptiveQuestionSelector
2. ✅ Wire into SessionAdapter.get_next_question()
3. ✅ Wire into SessionAdapter.submit_answer()
4. ✅ Add mastery endpoints to app_main.py
5. ✅ Test full flow (2026-01-03)
6. ⏳ Frontend integration (separate task)
7. ⏳ DB persistence for mastery (currently in-memory)

---

## Test Results (2026-01-03)

### End-to-End Flow Verified ✅

```bash
# 1. Start session with factors_multiples chapter
POST /api/quiz/session/start
{"student_id": "demo-001", "chapter": "factors_multiples", ...}
→ Session created

# 2. Get adaptive question
GET /api/quiz/{session}/question
→ Returns question with adaptive metadata:
   - questionId: "adaptive_xxx_0"
   - topic: "Number Sense - Finding Factors"
   - adaptive.conceptId, adaptive.mastery, adaptive.progress

# 3. Submit answer (correct)
POST /api/quiz/{session}/answer
{"question_id": "adaptive_xxx_0", "selected_index": 0}
→ Updates mastery: word_problem → PRACTICED

# 4. Check mastery
GET /api/student/demo-001/mastery/factors_multiples
→ Returns:
   - overall_accuracy: 1.0
   - concepts[word_problem]: {level: "practiced", attempts: 2, correct: 2}
   - recommendations: ["Focus on: Divisibility"]
```

### 69 Tests Passing ✅

```
tests/adaptation/test_adaptation.py: 24 passed
tests/contracts/test_question_contract.py: 20 passed  
tests/generators/test_factors_multiples_contract.py: 25 passed
```
