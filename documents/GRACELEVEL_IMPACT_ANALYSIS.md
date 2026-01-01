# Grade Level Impact Analysis: `gradeLevel = 6` Hardcoding

## Current State: Where the Value Comes From

```
Frontend: quiz/page.tsx
├── Line 104: gradeLevel = 6 (DEFAULT PARAMETER in AdaptiveQuizScreen component)
├── Line 141: const api = getQuizAPIClient();
├── Line 143-148: api.startSession(
│   ├── gradeLevel,           ← 6 (hardcoded default)
│   ├── "Mathematics",
│   ├── studentId,
│   └── chapterFromUrl
└── Sends to Backend as: class_level: 6

Backend: routes/practice_routes.py
├── Line 96: sm.start_session(
│   ├── student_id
│   ├── chapter_id
│   ├── class_level=request.class_level  ← receives 6
│   └── subject
├── Services: SessionManager.start_session()
├── Stores in DB: PracticeSession(class_level=6)
└── Used downstream...
```

---

## Data Flow: How `class_level=6` Affects Backend

### 1. **Database Storage (backend/database.py)**
```python
class PracticeSession(Base):
    __tablename__ = "analytics.practice_sessions"
    
    class_level = Column(Integer, nullable=False, default=5)
    # ↑ Stores the grade level (6) for this session
```

**Effect:** Each practice session record in the database has `class_level=6` hardcoded.

---

### 2. **Bloom Level Progression (backend/services/question_service.py)**
```python
def generate_next_question_for_practice(self, practice_session_id: int):
    session = self.session_manager._get_session(practice_session_id)
    
    bloom_level = "remember"  # Default
    if self.bloom_enforcer:
        current = self.bloom_enforcer.get_current_level(practice_session_id)
        if current:
            bloom_level = current
    
    # ↓ Get difficulty based on Bloom level
    difficulty = float(self.adaptive_selector.get_question_difficulty(
        chapter_id,
        bloom_level  # ← Depends on Bloom progression
    ))
```

**Effect:** The Bloom level enforcement affects which difficulty tier questions are selected.

---

### 3. **Question Difficulty Scaling (backend/services/adaptive_question_selector.py)**
```python
def get_question_difficulty(self, chapter_id: int, bloom_level: str) -> float:
    """
    Maps Bloom level to difficulty:
    - remember     → 1.0 (easy)
    - understand   → 1.5 
    - apply        → 2.0 
    - analyze      → 2.5 
    - evaluate     → 3.0 (hard)
    - create       → 3.5 (very hard)
    """
    # Currently NOT using class_level in difficulty calculation
    # ↑ This is a potential enhancement point
```

**Current Effect:** `class_level=6` is **STORED but NOT USED** in question difficulty.

---

### 4. **Learning Gap Analysis**
```python
def analyze_learning_gaps(self, session_id: int, chapter_id: int) -> dict:
    """
    Analyzes student performance to determine:
    - next_focus: Which concept to focus on next
    - difficulty_adjustment: Should we increase/decrease difficulty?
    """
    # Currently doesn't differentiate by class_level
    # ↑ Could be enhanced to adjust for age group
```

**Current Effect:** `class_level=6` is **NOT USED** in gap analysis.

---

## Where `class_level` SHOULD Be Used (But Isn't Currently)

### ❌ Missing: Grade-Based Question Selection
```python
# MISSING IMPLEMENTATION:
def should_include_concept(self, concept: str, class_level: int) -> bool:
    """
    Grade 3: Basic arithmetic (add, subtract)
    Grade 4: Factors, multiples, rounding
    Grade 5: Fractions, decimals, area
    Grade 6: Ratios, percentages, algebra basics
    Grade 7: Integers, exponents, equations
    """
    concepts_by_grade = {
        3: ["addition", "subtraction", "skip_counting"],
        4: ["factors", "multiples", "place_value"],
        5: ["fractions", "decimals", "area", "perimeter"],
        6: ["ratios", "percentages", "averages", "graphing"],
        7: ["integers", "equations", "exponents"],
    }
    return concept in concepts_by_grade.get(class_level, [])
```

---

### ❌ Missing: Difficulty Multiplier Based on Grade
```python
# MISSING IMPLEMENTATION:
def get_difficulty_for_grade(self, base_difficulty: float, class_level: int) -> float:
    """
    Adjust base difficulty by grade level
    """
    grade_multipliers = {
        3: 0.7,    # Make questions easier for younger students
        4: 0.8,
        5: 0.9,
        6: 1.0,    # Neutral (default)
        7: 1.1,
        8: 1.2,
        9: 1.3,
        10: 1.4,   # Harder for older students
    }
    return base_difficulty * grade_multipliers.get(class_level, 1.0)
```

---

### ❌ Missing: Bloom Level Starting Point by Grade
```python
# MISSING IMPLEMENTATION:
def get_initial_bloom_level(self, class_level: int) -> str:
    """
    Younger grades start easier, older grades can start higher
    """
    initial_levels = {
        3: "remember",
        4: "remember",
        5: "understand",
        6: "understand",   # Current hardcoding = class 6
        7: "apply",
        8: "apply",
        9: "analyze",
        10: "evaluate",
    }
    return initial_levels.get(class_level, "remember")
```

---

## What Currently Happens with `gradeLevel=6`

### Frontend Flow:
```
1. User clicks chapter
2. Quiz page loads with gradeLevel=6 (hardcoded default)
3. startSession(gradeLevel=6, ...) called
4. Backend receives class_level=6
```

### Backend Flow:
```
1. SessionManager.start_session() receives class_level=6
2. Creates PracticeSession with class_level=6 ✓ STORED
3. QuestionService.generate_next_question_for_practice()
   ├── Gets bloom_level from BloomEnforcer
   ├── Gets difficulty from AdaptiveQuestionSelector
   ├── BUT: Ignores class_level in both calculations ✗ NOT USED
   └── Returns question with fixed difficulty scaling
4. Question appears on frontend
```

### Database Record:
```sql
SELECT id, student_id, class_level, bloom_levels_completed, completion_percentage
FROM analytics.practice_sessions
WHERE student_id = 4;

-- Output:
-- id  | student_id | class_level | bloom_levels_completed          | completion_percentage
-- 129 | 4          | 6           | {"remember": [1, 0, 0, 0, 0]}   | 0
--                  ↑ Hardcoded to 6 (not from student data)
```

---

## The Problem: Hardcoded vs. Dynamic

### Current Implementation ❌
```typescript
// frontend/app/quiz/page.tsx
export const AdaptiveQuizScreen: FC<AdaptiveQuizScreenProps> = ({
  sessionId,
  gradeLevel = 6,  // ← HARDCODED DEFAULT
}) => {
  // gradeLevel is always 6 unless explicitly passed
  // Nobody passes it, so it's always 6
```

**Issues:**
1. ❌ All students get `class_level=6` regardless of age
2. ❌ No differentiation between Grade 3 and Grade 10 students
3. ❌ Difficulty scaling is uniform
4. ❌ Question selection doesn't account for grade appropriateness

### What It Should Be ✅
```typescript
// frontend/app/quiz/page.tsx
export const AdaptiveQuizScreen: FC<AdaptiveQuizScreenProps> = ({
  sessionId,
  gradeLevel = 6,
}) => {
  const { student } = useStudent();
  
  // Get grade level from student or chapter config
  const effectiveGradeLevel = student?.gradeLevel || gradeLevel;
  // ✓ Student could have: { id: "4", name: "Priya", gradeLevel: 5 }
```

---

## Impact Summary

| Aspect | Current | Ideal | Gap |
|--------|---------|-------|-----|
| **Storage** | ✓ Stored in DB | ✓ Stored | ✓ WORKING |
| **Question Difficulty** | ✗ Ignores grade | ✓ Adjusts by grade | ✗ NOT IMPLEMENTED |
| **Concept Selection** | ✗ Same for all ages | ✓ Grade-appropriate | ✗ NOT IMPLEMENTED |
| **Bloom Progression** | ✗ Fixed sequence | ✓ Age-based start | ✗ NOT IMPLEMENTED |
| **Feedback Depth** | ✗ Same for all ages | ✓ Adapts to maturity | ✗ NOT IMPLEMENTED |

---

## Recommendations

### Short Term (Fix Hardcoding):
1. Get `gradeLevel` from `student` context (not hardcoded to 6)
2. Store student's actual grade level in `Student` model
3. Pass actual grade to `startSession()`

### Medium Term (Use Grade Level):
1. Implement grade-based difficulty multipliers
2. Filter concepts by appropriateness for grade
3. Adjust Bloom level starting point by grade

### Long Term (Full Personalization):
1. Create grade-specific question templates
2. Implement age-appropriate language/examples
3. Customize feedback complexity by student age

---

## Code Changes Needed

### 1. Frontend: Use Student's Grade
```typescript
// BEFORE:
const { student } = useStudent();
const api = getQuizAPIClient();
const config = await api.startSession(
  gradeLevel,  // ← Always 6
  "Mathematics",
  studentId,
  chapterFromUrl
);

// AFTER:
const { student } = useStudent();
const effectiveGradeLevel = student?.gradeLevel || gradeLevel;
const api = getQuizAPIClient();
const config = await api.startSession(
  effectiveGradeLevel,  // ← From student data
  "Mathematics",
  studentId,
  chapterFromUrl
);
```

### 2. Backend: Use Grade in Question Selection
```python
# In QuestionService.generate_next_question_for_practice()
def generate_next_question_for_practice(self, practice_session_id: int):
    session = self.session_manager._get_session(practice_session_id)
    class_level = session.class_level  # ← Get from session
    
    # Apply grade-based filters
    if not self._is_concept_appropriate_for_grade(concept, class_level):
        concept = self._get_next_appropriate_concept(chapter_id, class_level)
    
    # Apply grade-based difficulty adjustment
    difficulty = self._adjust_difficulty_for_grade(
        base_difficulty,
        class_level
    )
```

---

## File References

- **Frontend Hardcoding:** `frontend/app/quiz/page.tsx` (line 104)
- **Student Model:** `frontend/lib/studentContext.tsx` (needs `gradeLevel` field)
- **Backend Storage:** `backend/database.py` (line 90)
- **Backend Usage:** `backend/services/question_service.py` (line 213)
- **Adaptive Selection:** `backend/services/adaptive_question_selector.py`

