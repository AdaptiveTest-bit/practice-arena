# 🚀 IMPLEMENTATION QUICK START

**Phase-by-Phase Breakdown for 4-Week MVP Implementation**

---

## ⚡ Week 1: Database Foundation

### Tasks
1. **Create `practice_sessions` table**
   - Run migration script
   - Add indexes for student_id, chapter_id
   - Test table creation

2. **Update `students` table**
   - Add: `current_class_level`, `current_subject`, `current_chapter_id`
   - Add: `last_active_session_id` FK

3. **Create ORM Models**
   - File: `database.py`
   - Add `PracticeSession` model
   - Define relationships

4. **Test**
   - Verify table creation
   - Test insert/update/select
   - Verify foreign keys work

### Deliverable
✅ Database ready for session tracking

---

## 📅 Week 2: Session Management APIs

### Tasks
1. **Create `SessionManager` service**
   - File: `services/session_manager.py`
   - Methods:
     - `start_session()` - Create or resume
     - `update_progress()` - Update on each answer
     - `end_session()` - Finalize analytics

2. **Implement endpoints**
   - `POST /api/practice/session/start`
   - `GET /api/practice/session/{id}/progress`
   - `POST /api/practice/session/{id}/end`

3. **Update existing endpoints**
   - Modify `POST /api/question` to accept `session_id`
   - Modify `POST /api/check-answer` to update session

4. **Test**
   - Start session → Get progress → End session
   - Resume session → Continue
   - Verify DB updates

### Deliverable
✅ Session-based learning fully functional

---

## 🎓 Week 3: Progression & Analytics

### Tasks
1. **Create `BloomLevelEnforcer` service**
   - File: `services/bloom_level_enforcer.py`
   - Methods:
     - `can_advance_to_next_level()` - Check 80% rule
     - `lock_level()`, `unlock_level()`
     - `get_current_level()`

2. **Create `ConceptMasteryTracker`**
   - File: `services/concept_mastery_tracker.py`
   - Track accuracy per concept
   - Determine mastery status

3. **Create `BreakPointTracker`**
   - File: `services/break_point_tracker.py`
   - Record break points (accuracy < threshold)
   - Track misconceptions

4. **Update answer-checking logic**
   - In `/api/check-answer`:
     - Update concept accuracy
     - Check if concept mastered
     - Check if level can advance
     - Record break points

5. **Test**
   - Answer 5 questions at 80% → Advance level
   - Answer 3 questions at 60% → Record break point
   - Verify concept tracking

### Deliverable
✅ Full analytics pipeline working

---

## 🔗 Week 4: Integration & Polish

### Tasks
1. **Create status query endpoint**
   - `GET /api/practice/student/{id}/chapter/{id}/status`
   - For other project to check: Is 80% done?

2. **Create session summary endpoint**
   - `GET /api/practice/session/{id}/summary`
   - Return all analytics for other project

3. **Create chapter config**
   - File: `config/chapter_config.py`
   - Define max_bloom_level per chapter
   - Define critical concepts

4. **Final testing**
   - Complete end-to-end flow
   - Test with multiple students
   - Verify inter-project compatibility

5. **Documentation**
   - Update README with new APIs
   - Document chapter configuration
   - Create integration guide for other project

### Deliverable
✅ MVP complete and production-ready

---

## 📋 Detailed Implementation Checklist

### Week 1 Checklist

```
Database
├─ [ ] Create analytics.practice_sessions table
├─ [ ] Add columns to users.students
├─ [ ] Create indexes
├─ [ ] Add ORM model to database.py
└─ [ ] Test connectivity

Schema
├─ [ ] Define practice_sessions schema
├─ [ ] Document all JSON fields
├─ [ ] Create sample data
└─ [ ] Verify relationships
```

### Week 2 Checklist

```
SessionManager Service
├─ [ ] Implement start_session()
├─ [ ] Implement resume_session()
├─ [ ] Implement update_progress()
├─ [ ] Implement end_session()
└─ [ ] Add error handling

API Endpoints
├─ [ ] POST /api/practice/session/start
├─ [ ] GET /api/practice/session/{id}/progress
├─ [ ] POST /api/practice/session/{id}/end
├─ [ ] Update /api/question (add session_id)
└─ [ ] Update /api/check-answer (add session tracking)

Testing
├─ [ ] Start new session
├─ [ ] Resume existing session
├─ [ ] Get session progress
├─ [ ] End session
└─ [ ] Verify all data persists
```

### Week 3 Checklist

```
BloomLevelEnforcer
├─ [ ] Implement can_advance_to_next_level()
├─ [ ] Implement get_current_level()
├─ [ ] Add 80% accuracy check
└─ [ ] Lock/unlock logic

ConceptMasteryTracker
├─ [ ] Track per-concept accuracy
├─ [ ] Calculate mastery status
├─ [ ] Identify weak concepts
└─ [ ] Return structured data

BreakPointTracker
├─ [ ] Record break points
├─ [ ] Count misconceptions
├─ [ ] Provide remediation data
└─ [ ] Calculate thresholds

Integration
├─ [ ] Update /api/check-answer
├─ [ ] Call BloomLevelEnforcer on answer
├─ [ ] Call ConceptMasteryTracker on answer
├─ [ ] Call BreakPointTracker on answer
└─ [ ] Update session progress

Testing
├─ [ ] Test Bloom level progression
├─ [ ] Test concept mastery detection
├─ [ ] Test break point recording
├─ [ ] Test misconception counting
└─ [ ] End-to-end workflow test
```

### Week 4 Checklist

```
Status Query Endpoint
├─ [ ] GET /api/practice/student/{id}/chapter/{id}/status
├─ [ ] Return completion_percentage
├─ [ ] Return is_ready_for_next_chapter
└─ [ ] Return weak_concepts

Chapter Config
├─ [ ] Create config/chapter_config.py
├─ [ ] Define Class 5 Maths chapters
├─ [ ] Define max_bloom_level per chapter
├─ [ ] Define critical_concepts per chapter
└─ [ ] Load config in app startup

Testing
├─ [ ] Complete full student journey
├─ [ ] Verify session resumability
├─ [ ] Verify Bloom progression locks
├─ [ ] Verify analytics completeness
├─ [ ] Test other project integration
└─ [ ] Performance testing (10+ students)

Documentation
├─ [ ] Update README with new APIs
├─ [ ] Document chapter configuration
├─ [ ] Create integration guide
├─ [ ] Document session lifecycle
└─ [ ] Add troubleshooting guide
```

---

## 🎯 Code Example Templates

### SessionManager.start_session()

```python
def start_session(self, student_id: int, chapter_id: int, 
                 class_level: int = 5, subject: str = 'Mathematics'):
    """
    Start a new practice session or resume existing one.
    
    1. Check if student has active session for this chapter
    2. If yes, return resume_data
    3. If no, create new session record
    4. Return session_id and initial data
    """
    # Check for active session
    existing = db.query(PracticeSession).filter(
        PracticeSession.student_id == student_id,
        PracticeSession.chapter_id == chapter_id,
        PracticeSession.status == 'in_progress'
    ).first()
    
    if existing:
        return {
            "session_id": existing.id,
            "status": "resumed",
            "progress": self._get_session_progress(existing.id)
        }
    
    # Create new session
    session = PracticeSession(
        student_id=student_id,
        chapter_id=chapter_id,
        class_level=class_level,
        subject=subject,
        status='in_progress',
        completion_percentage=0
    )
    db.add(session)
    db.commit()
    
    return {
        "session_id": session.id,
        "status": "new",
        "progress": self._get_session_progress(session.id)
    }
```

### BloomLevelEnforcer.can_advance()

```python
def can_advance_to_next_level(self, session_id: int, current_level: str) -> bool:
    """
    Check if student can advance from current Bloom level.
    Rule: Must have >= 80% accuracy at current level.
    """
    session = db.query(PracticeSession).filter_by(id=session_id).first()
    
    # Get accuracy for current level from session.bloom_levels_completed JSON
    current_stats = session.bloom_levels_completed.get(current_level, {})
    accuracy = current_stats.get('accuracy', 0)
    
    return accuracy >= 0.80
```

### BreakPointTracker.record_break_point()

```python
def record_break_point(self, session_id: int, concept: str, 
                      bloom_level: str, accuracy: float):
    """
    Record a break point when student struggles.
    Break point = accuracy < 70% for a concept at a Bloom level.
    """
    if accuracy < 0.70:  # Threshold
        session = db.query(PracticeSession).filter_by(id=session_id).first()
        
        break_point = {
            "concept": concept,
            "bloom_level": bloom_level,
            "accuracy": accuracy,
            "timestamp": datetime.now().isoformat()
        }
        
        if not session.break_points:
            session.break_points = []
        
        session.break_points.append(break_point)
        session.weak_concepts.append(concept)
        db.commit()
```

---

## 📊 Expected Database State After Implementation

### practice_sessions Table Sample

```json
{
  "id": 1,
  "student_id": 123,
  "chapter_id": 5,
  "class_level": 5,
  "subject": "Mathematics",
  "session_start_time": "2025-12-28T10:00:00",
  "session_end_time": "2025-12-28T10:45:00",
  "total_duration_minutes": 45,
  "completion_percentage": 87,
  "concepts_covered": ["place_value", "rounding", "comparing"],
  "concepts_mastered": ["place_value", "comparing"],
  "accuracy_by_concept": {
    "place_value": 0.90,
    "rounding": 0.65,
    "comparing": 0.85
  },
  "bloom_levels_completed": {
    "remember": {"status": "completed", "accuracy": 0.90},
    "understand": {"status": "completed", "accuracy": 0.80},
    "apply": {"status": "in_progress", "accuracy": 0.70},
    "analyze": {"status": "not_started"}
  },
  "misconceptions_detected": {
    "rounding_logic_error": 3,
    "place_value_confusion": 1
  },
  "break_points": [
    {
      "concept": "rounding",
      "bloom_level": "understand",
      "accuracy": 0.65,
      "timestamp": "2025-12-28T10:25:00"
    }
  ],
  "status": "completed"
}
```

---

## ✅ Success Metrics

### By End of Week 1
- ✅ Database tables exist and are queryable
- ✅ ORM models defined and working
- ✅ No migration errors

### By End of Week 2
- ✅ Student can start session
- ✅ Student can resume session
- ✅ Session data persists in DB
- ✅ API returns correct session info

### By End of Week 3
- ✅ Bloom levels lock/unlock correctly
- ✅ Concept accuracy tracked per session
- ✅ Break points recorded when accuracy < 70%
- ✅ Misconceptions counted accurately

### By End of Week 4
- ✅ Other project can query completion status
- ✅ All analytics data available
- ✅ Full end-to-end workflow tested
- ✅ Documentation complete

---

## 🚀 Ready to Build!

This plan gives you:
- ✅ Week-by-week breakdown
- ✅ Specific tasks per week
- ✅ Code templates
- ✅ Testing checklist
- ✅ Success criteria

Start with Week 1 Database setup, then proceed sequentially.

**Let's build!** 🎓
