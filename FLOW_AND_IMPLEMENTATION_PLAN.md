# 🎯 PRACTICE ENGINE - DATA FLOW & IMPLEMENTATION PLAN

**Date**: December 28, 2025  
**Status**: ✅ Flow Confirmed & Ready for Implementation  
**Scope**: Class 5 Mathematics MVP

---

## 📊 Confirmed Data Flow

```
┌─────────────────────────────────────┐
│   OTHER PROJECT (Entry Point)       │
├─────────────────────────────────────┤
│ 1. Student Login (handled there)    │
│ 2. Select Class: 5                  │
│ 3. Select Subject: Mathematics      │
│ 4. Select Chapter: e.g., "Ch5"      │
└────────────┬────────────────────────┘
             │
             ↓ Query database directly
    ┌────────────────────────────────────┐
    │ Check: Is practice_session         │
    │ completion >= 80% ?                │
    │ (Check analytics.practice_sessions)│
    └────────────┬──────────────┬────────┘
                 │              │
        No   ┌────┴─────┐  Yes   │
            ↓          ↓         │
    ┌──────────────┐  │         │
    │ Send to Our  │  │         │
    │ Practice     │  │         │
    │ Engine       │  │         │
    └──────┬───────┘  │         │
           │          │         │
           ↓          ↓         ↓
    ┌──────────────────────────────────────────┐
    │  OUR PRACTICE ENGINE (Port 5002)         │
    ├──────────────────────────────────────────┤
    │ 1. Start NEW or RESUME existing session  │
    │    (Check practice_sessions table)       │
    │                                          │
    │ 2. Show Bloom Level 1 (Remember)        │
    │    ├─ 3-5 questions per concept         │
    │    ├─ Track: accuracy, time, attempts   │
    │    ├─ Detect misconceptions             │
    │    └─ Move to next concept              │
    │                                          │
    │ 3. Show Bloom Level 2 (Understand)      │
    │    ├─ Student must have 80% acc in L1   │
    │    ├─ Track same analytics              │
    │    └─ Continue progression              │
    │                                          │
    │ 4. Continue through all Bloom levels    │
    │    └─ Based on chapter requirements     │
    │                                          │
    │ 5. Track Session:                       │
    │    ├─ session_start_time                │
    │    ├─ session_end_time                  │
    │    ├─ total_minutes_practiced           │
    │    ├─ concepts_covered                  │
    │    ├─ concepts_mastered                 │
    │    ├─ misconceptions_detected           │
    │    ├─ accuracy_by_bloom_level           │
    │    └─ final_completion_percentage       │
    └────────┬─────────────────────────────┬──┘
             │                             │
             │ Write to DB                 │ Return to Other Project
             ↓                             ↓
    ┌──────────────────────────────────────┐
    │  SHARED DATABASE (PostgreSQL)        │
    ├──────────────────────────────────────┤
    │ analytics.practice_sessions          │
    │ ├─ id                                │
    │ ├─ student_id (FK to users.students) │
    │ ├─ chapter_id                        │
    │ ├─ class_level: 5                    │
    │ ├─ subject: 'Mathematics'            │
    │ ├─ session_start_time                │
    │ ├─ session_end_time                  │
    │ ├─ total_duration_minutes            │
    │ ├─ completion_percentage             │
    │ ├─ concepts_covered: []              │
    │ ├─ concepts_mastered: []             │
    │ ├─ accuracy_by_concept: {}           │
    │ ├─ bloom_levels_completed: {}        │
    │ ├─ misconceptions_detected: {}       │
    │ ├─ weak_areas: []                    │
    │ ├─ strong_areas: []                  │
    │ ├─ status: 'in_progress'/'completed' │
    │ └─ created_at, updated_at            │
    └────────┬──────────────────────────┬──┘
             │ Read                      │
             │ (Other project)           │
             ↓                           │
    ┌──────────────────────────────┐     │
    │ Other Project Dashboard      │     │
    ├──────────────────────────────┤     │
    │ Shows:                       │     │
    │ ├─ Completion: 85% ✅        │     │
    │ ├─ Bloom levels: All 6 ✅    │     │
    │ ├─ Session time: 45 mins     │     │
    │ ├─ Misconceptions found: 3   │     │
    │ ├─ Weak areas: Place value   │     │
    │ └─ Next: Move to Ch6         │     │
    │                              │     │
    │ Or (if not 80%):             │     │
    │ ├─ Completion: 65% ⏳        │     │
    │ ├─ Weak area: Rounding       │     │
    │ └─ Next: Continue practicing │     │
    └──────────────────────────────┘     │
                                         │
                                    (Session ends
                                     when student
                                     leaves engine)
```

---

## 🗄️ Database Schema Changes Required

### New Table: `analytics.practice_sessions`

```sql
CREATE TABLE analytics.practice_sessions (
    id SERIAL PRIMARY KEY,
    
    -- Student & Course Info
    student_id INTEGER NOT NULL REFERENCES users.students(id) ON DELETE CASCADE,
    chapter_id INTEGER NOT NULL,
    class_level INTEGER NOT NULL DEFAULT 5,
    subject VARCHAR(50) NOT NULL DEFAULT 'Mathematics',
    
    -- Session Timing
    session_start_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    session_end_time TIMESTAMP NULL,
    total_duration_minutes INTEGER NULL,
    
    -- Progress Tracking
    completion_percentage FLOAT NOT NULL DEFAULT 0,
    
    -- JSON fields for flexibility
    concepts_covered JSON NOT NULL DEFAULT '[]',  -- ["concept1", "concept2"]
    concepts_mastered JSON NOT NULL DEFAULT '[]', -- ["concept1"]
    concepts_weak JSON NOT NULL DEFAULT '[]',     -- Areas needing remediation
    
    -- Analytics by Concept
    accuracy_by_concept JSON NOT NULL DEFAULT '{}', -- {"concept1": 0.85}
    
    -- Bloom's Level Progress
    bloom_levels_completed JSON NOT NULL DEFAULT '{}', 
    -- {
    --   "remember": {"status": "completed", "accuracy": 0.90},
    --   "understand": {"status": "completed", "accuracy": 0.85},
    --   "apply": {"status": "in_progress", "accuracy": 0.70},
    --   "analyze": {"status": "not_started"},
    --   "evaluate": {"status": "not_started"},
    --   "create": {"status": "not_started"}
    -- }
    
    -- Misconceptions
    misconceptions_detected JSON NOT NULL DEFAULT '{}',
    -- {
    --   "place_value_confusion": 3,
    --   "digit_place_error": 2,
    --   "rounding_logic_error": 1
    -- }
    
    -- Performance Summary
    total_questions_attempted INTEGER NOT NULL DEFAULT 0,
    total_questions_correct INTEGER NOT NULL DEFAULT 0,
    overall_accuracy FLOAT NOT NULL DEFAULT 0,
    
    -- Break points (for remediation)
    break_points JSON NOT NULL DEFAULT '[]',
    -- {
    --   "concept": "place_value",
    --   "bloom_level": "understand",
    --   "accuracy": 0.40,
    --   "timestamp": "2025-12-28T10:30:00"
    -- }
    
    -- Status
    status VARCHAR(20) NOT NULL DEFAULT 'in_progress',
    -- Values: 'in_progress', 'completed', 'paused'
    
    -- Metadata
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes for fast queries
    CONSTRAINT fk_student FOREIGN KEY (student_id) REFERENCES users.students(id),
    INDEX idx_student_id (student_id),
    INDEX idx_chapter_id (chapter_id),
    INDEX idx_session_date (created_at)
);
```

### Updated Table: `users.students` (Add Columns)

```sql
ALTER TABLE users.students ADD COLUMN (
    current_class_level INTEGER DEFAULT 5,
    current_subject VARCHAR(50) DEFAULT 'Mathematics',
    current_chapter_id INTEGER,
    last_active_session_id INTEGER REFERENCES analytics.practice_sessions(id),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

---

## 📋 API Endpoints Needed

### 1. Start/Resume Practice Session

```
POST /api/practice/session/start
Body: {
  "student_id": "123",
  "chapter_id": 5,
  "class_level": 5,
  "subject": "Mathematics"
}

Response: {
  "success": true,
  "session_id": "S_001",
  "chapter_name": "Large Numbers",
  "bloom_levels": ["remember", "understand", "apply", "analyze", "evaluate", "create"],
  "current_bloom_level": "remember",
  "concepts_to_cover": ["place_value", "rounding", "comparing", "operations"],
  "concepts_remaining": ["place_value", "rounding", "comparing", "operations"],
  "session_progress": {
    "completion_percentage": 0,
    "concepts_mastered": [],
    "bloom_levels_completed": {},
    "estimated_remaining_time": "45 minutes"
  }
}
```

### 2. Get Next Question (Existing, but with session tracking)

```
POST /api/practice/question
Body: {
  "student_id": "123",
  "session_id": "S_001",
  "bloom_level": "remember"
}

Response: {
  "question_id": "Q_001",
  "session_id": "S_001",
  "concept": "place_value",
  "bloom_level": "remember",
  "difficulty": 1.0,
  "question_text": "...",
  "options": [...],
  "hint": "...",
  "question_number": 1,
  "concept_question_number": 1,
  "bloom_level_progress": "1/5 questions for Remember level"
}
```

### 3. Submit Answer (Existing, but with session update)

```
POST /api/practice/answer/check
Body: {
  "student_id": "123",
  "session_id": "S_001",
  "question_id": "Q_001",
  "selected_index": 2,
  "time_taken_seconds": 15
}

Response: {
  "is_correct": true,
  "feedback": "Excellent! Place value...",
  "misconception_detected": null,
  "bloom_level_progress": {
    "level": "remember",
    "questions_completed": 2,
    "questions_needed": 5,
    "accuracy": 0.95,
    "status": "progressing"
  },
  "concept_progress": {
    "concept": "place_value",
    "mastered": false,
    "accuracy": 0.95,
    "questions_left": 1
  },
  "next_action": "continue_same_concept",
  "next_question_preview": {...}
}
```

### 4. Get Session Progress

```
GET /api/practice/session/{session_id}/progress
Response: {
  "session_id": "S_001",
  "student_id": "123",
  "chapter": "Large Numbers",
  "completion_percentage": 45,
  "session_duration_minutes": 22,
  "concepts": {
    "place_value": {
      "status": "mastered",
      "accuracy": 0.90,
      "questions": 5
    },
    "rounding": {
      "status": "in_progress",
      "accuracy": 0.70,
      "questions": 3
    },
    "comparing": {
      "status": "not_started"
    },
    "operations": {
      "status": "not_started"
    }
  },
  "bloom_levels": {
    "remember": {
      "status": "completed",
      "accuracy": 0.88,
      "concepts_covered": 2,
      "concepts_total": 4
    },
    "understand": {
      "status": "in_progress",
      "accuracy": 0.65,
      "concepts_covered": 1,
      "concepts_total": 4
    },
    ...
  },
  "misconceptions": {
    "place_value_confusion": 1,
    "rounding_logic_error": 2
  },
  "break_points": [
    {
      "concept": "rounding",
      "bloom_level": "understand",
      "accuracy": 0.40,
      "timestamp": "2025-12-28T10:45:00"
    }
  ]
}
```

### 5. End Session & Save Analytics

```
POST /api/practice/session/{session_id}/end
Body: {
  "student_id": "123"
}

Response: {
  "session_id": "S_001",
  "completion_percentage": 87,
  "status": "completed",
  "session_summary": {
    "total_duration": 45,
    "total_questions": 28,
    "total_correct": 24,
    "overall_accuracy": 0.86,
    "concepts_covered": 4,
    "concepts_mastered": 3,
    "concepts_weak": ["rounding"],
    "bloom_levels_completed": 3,
    "misconceptions_found": 3
  },
  "ready_for_next_chapter": true,
  "recommendations": [
    "Great job on place value! You mastered it.",
    "Work on rounding - we found some confusion there.",
    "Ready for the next chapter once you finish this one."
  ]
}
```

### 6. Query Session Status (For Other Project)

```
GET /api/practice/student/{student_id}/chapter/{chapter_id}/status
Response: {
  "student_id": "123",
  "chapter_id": 5,
  "has_active_session": true,
  "active_session_id": "S_001",
  "last_session": {
    "session_id": "S_001",
    "completion_percentage": 87,
    "status": "completed",
    "ended_at": "2025-12-28T11:15:00"
  },
  "completion_percentage": 87,
  "is_ready_for_next_chapter": true,
  "weak_concepts": ["rounding"],
  "misconceptions_detected": ["rounding_logic_error"]
}
```

---

## 🏗️ Implementation Components

### Component 1: Session Manager

**File**: `services/session_manager.py`

**Responsibilities**:
- Create new practice_session record
- Resume existing session
- Track session timing
- Update session progress
- Calculate completion percentage
- Store break points

```python
class SessionManager:
    def start_session(self, student_id, chapter_id, class_level=5, subject='Mathematics'):
        # Check if existing session exists
        # If yes, return resume data
        # If no, create new session
        # Return session_id and initial data
        
    def update_session_progress(self, session_id, updates):
        # Update concepts_covered
        # Update accuracy_by_concept
        # Update bloom_levels_completed
        # Detect break points
        # Calculate completion %
        
    def end_session(self, session_id):
        # Set session_end_time
        # Calculate total_duration_minutes
        # Finalize all analytics
        # Return completion summary
```

### Component 2: Bloom Level Progression Enforcer

**File**: `services/bloom_level_enforcer.py`

**Responsibilities**:
- Enforce sequential Bloom's level progression
- Calculate if student can advance to next level (80% accuracy required)
- Lock/unlock levels based on performance
- Track accuracy per level

```python
class BloomLevelEnforcer:
    def can_advance_to_next_level(self, session_id, current_level):
        # Get accuracy for current level
        # Check if >= 80%
        # If yes, return True
        # If no, return False with remaining requirement
        
    def get_next_level(self, current_level):
        # remember → understand → apply → analyze → evaluate → create
        
    def get_current_level_for_session(self, session_id):
        # Find highest unlocked level
```

### Component 3: Concept Mastery Tracker

**File**: `services/concept_mastery_tracker.py`

**Responsibilities**:
- Track accuracy per concept
- Determine if concept is mastered (80%+ accuracy)
- Identify weak concepts
- Calculate concept progression within Bloom's levels

```python
class ConceptMasteryTracker:
    def update_concept_accuracy(self, session_id, concept, is_correct):
        # Update accuracy_by_concept[concept]
        # Check if mastered (>= 0.8)
        # Mark in concepts_mastered if done
        
    def get_weak_concepts(self, session_id):
        # Return concepts with accuracy < 0.8
```

### Component 4: Misconception & Break Point Tracker

**File**: `services/break_point_tracker.py`

**Responsibilities**:
- Record break points (where student struggles)
- Track misconceptions per session
- Provide remediation data to other project

```python
class BreakPointTracker:
    def record_break_point(self, session_id, concept, bloom_level, accuracy):
        # If accuracy < threshold, record break point
        # Include: concept, bloom_level, accuracy, timestamp
        
    def update_misconceptions(self, session_id, misconception_type, count):
        # Increment misconception counter
```

---

## 🎯 Chapter Configuration (Hardcoded for MVP)

```python
# In app_refactored.py or config.py

CLASS_5_MATHS_CHAPTERS = {
    1: {
        "name": "The Fish Tale",
        "concepts": ["numbers", "operations", "word_problems"],
        "max_bloom_level": "Apply",  # Students only go up to Apply
        "difficulty_curve": [0.5, 0.8, 1.0, 1.2, 1.4]
    },
    2: {
        "name": "Shapes and Angles",
        "concepts": ["geometry", "angles", "measurement"],
        "max_bloom_level": "Apply",
        "difficulty_curve": [0.6, 0.9, 1.1, 1.3, 1.5]
    },
    3: {
        "name": "How Many Squares?",
        "concepts": ["patterns", "spatial_reasoning", "counting"],
        "max_bloom_level": "Analyze",  # This chapter goes deeper
        "difficulty_curve": [0.7, 1.0, 1.2, 1.4, 1.6]
    },
    4: {
        "name": "Parts and Wholes",
        "concepts": ["fractions", "decimals", "ratios"],
        "max_bloom_level": "Analyze",
        "difficulty_curve": [0.8, 1.0, 1.2, 1.4, 1.5]
    },
    5: {
        "name": "Does it Look the Same?",
        "concepts": ["symmetry", "reflection", "rotation"],
        "max_bloom_level": "Apply",
        "difficulty_curve": [0.5, 0.8, 1.0, 1.2, 1.4]
    },
    # ... more chapters
}

# Define which concepts are "critical" per chapter
CHAPTER_CRITICAL_CONCEPTS = {
    1: ["numbers", "operations"],  # Must master these
    2: ["geometry", "angles"],
    3: ["patterns", "spatial_reasoning"],
    4: ["fractions", "decimals"],
    5: ["symmetry", "reflection"],
}
```

---

## 📊 Data Flow Implementation Steps

### Phase 1: Database Setup (Week 1)

- [ ] Create `practice_sessions` table
- [ ] Add columns to `students` table
- [ ] Create indexes
- [ ] Test connectivity
- [ ] Verify schema

### Phase 2: Session Management (Week 2)

- [ ] Implement `SessionManager` service
- [ ] Create `/api/practice/session/start` endpoint
- [ ] Create `/api/practice/session/{id}/progress` endpoint
- [ ] Create `/api/practice/session/{id}/end` endpoint
- [ ] Test session creation & updates

### Phase 3: Bloom's Level Enforcement (Week 2-3)

- [ ] Implement `BloomLevelEnforcer` service
- [ ] Update question selection logic
- [ ] Lock/unlock levels based on accuracy
- [ ] Test progression logic

### Phase 4: Concept & Break Point Tracking (Week 3)

- [ ] Implement `ConceptMasteryTracker`
- [ ] Implement `BreakPointTracker`
- [ ] Update answer-checking logic to record break points
- [ ] Test break point detection

### Phase 5: Other Project Integration (Week 4)

- [ ] Implement `/api/practice/student/{id}/chapter/{id}/status` endpoint
- [ ] Ensure other project can query completion status
- [ ] Test inter-project communication
- [ ] Verify analytics flow

---

## ✅ Key Features of New Flow

### 1. Session Resumability
- ✅ Student can leave and come back
- ✅ Progress is saved
- ✅ Session continues from where it left

### 2. Sequential Progression
- ✅ Bloom's levels locked until 80% accuracy achieved
- ✅ Concepts must be covered in all Bloom's levels
- ✅ No jumping ahead

### 3. Analytics Richness
- ✅ Per-concept accuracy tracking
- ✅ Per-Bloom-level accuracy tracking
- ✅ Misconception frequency tracking
- ✅ Break point identification
- ✅ Session time tracking

### 4. Remediation Ready
- ✅ Break points recorded for teacher/parent view
- ✅ Weak concepts identified
- ✅ Misconceptions quantified
- ✅ Ready for targeted remediation

### 5. Integration Ready
- ✅ Clear completion status for other project
- ✅ Detailed analytics available
- ✅ Seamless handoff of data
- ✅ No data duplication

---

## 🗂️ Updated Project Structure

```
question-generator/
├── app_refactored.py
├── database.py (add practice_sessions model)
├── init_database.py (create practice_sessions table)
│
├── services/
│   ├── session_manager.py (NEW)
│   ├── bloom_level_enforcer.py (NEW)
│   ├── concept_mastery_tracker.py (NEW)
│   ├── break_point_tracker.py (NEW)
│   ├── adaptive_learning_service.py (UPDATED)
│   ├── orm_student_repository.py (UPDATED)
│   └── ... other services
│
├── models/
│   └── practice_session.py (NEW - Pydantic models for session)
│
└── config/
    └── chapter_config.py (NEW - Hardcoded chapter definitions)
```

---

## 📈 Expected Outcomes

### For Students
- ✅ Clear progress visibility (Remember ✅, Understand ✅, Apply ⏳)
- ✅ Saved progress across sessions
- ✅ Sequential, logical progression
- ✅ Immediate feedback on misconceptions

### For Other Project
- ✅ Query: "Is this chapter 80% done?" → Yes/No
- ✅ Detailed analytics on weak areas
- ✅ Misconceptions to address
- ✅ Break points for targeted remediation

### For Teachers/Parents
- ✅ Session duration tracking
- ✅ Misconceptions by frequency
- ✅ Weak concepts identified
- ✅ Break points for intervention

---

## 🎯 Success Criteria

- [ ] Student can start practice session
- [ ] Student can resume previous session
- [ ] Bloom's levels lock/unlock correctly
- [ ] Concepts tracked per Bloom level
- [ ] Session data persists in DB
- [ ] Other project can query completion status
- [ ] Analytics populated with session data
- [ ] Break points recorded for weak areas
- [ ] Misconceptions counted per session
- [ ] MVP works for Class 5 Maths

---

## 📝 Summary

This implementation will:

1. **Enable session-based learning** - Students can pause/resume
2. **Track granular analytics** - Know exactly where students struggle
3. **Enforce pedagogical progression** - Sequential Bloom's levels
4. **Provide remediation data** - Break points for targeted help
5. **Integrate with other project** - Clean API for completion checking
6. **Support MVP scope** - Class 5 Maths only, hardcoded chapters

The flow is clear, the database schema is defined, and the API contracts are specified. Ready to implement!

---

**Next Step**: Implement Phase 1 (Database Setup) starting Week 1.
