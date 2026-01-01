# Backend Services Archive

**Date Archived:** January 1, 2026  
**Archive Reason:** Phase 2 Week 3 - Experimental services not integrated into main flow  
**Status:** Preserved for future use - can be reactivated if needed

---

## Overview

This directory contains experimental and dormant services that were built during development but were not integrated into the main quiz flow. These services represent legitimate features but were deprioritized or superseded by simpler alternatives.

**Total archived:** 5 services (~750 lines of code)  
**Status:** All code preserved, can be reactivated or referenced for future implementation

---

## Archived Services

### 1. adaptive_question_selector.py

**Purpose:** Advanced question selection based on student mastery levels  
**Size:** ~200 lines  
**Status:** Experimental  

**What it does:**
- Analyzes student learning gaps
- Selects questions that target specific gaps
- Calculates question difficulty dynamically
- Provides adaptive question sequencing

**Why not integrated:**
- SessionAdapter handles question routing more simply
- Would require significant integration work
- Adds complexity for modest benefit in current flow
- Deduplication service handles most use cases

**How to reactivate:**
1. Move from `archive/services/` back to `services/`
2. Add import to `services/__init__.py`
3. Integrate with SessionAdapter.get_next_question()
4. Test with end-to-end test suite
5. Expected effort: 4-6 hours

**Dependencies:**
- `sequencing_engine.py` (also archived, would need both)
- `bloom_level_enforcer.py` (deleted in Week 2, in git history)
- `concept_mastery_tracker.py` (deleted in Week 2, in git history)

---

### 2. sequencing_engine.py

**Purpose:** Optimal chapter sequencing for student learning path  
**Size:** ~150 lines  
**Status:** Experimental  

**What it does:**
- Determines next chapter based on mastery levels
- Optimizes learning path for student
- Tracks prerequisite knowledge
- Provides chapter recommendations

**Why not integrated:**
- AdaptiveLearningService handles chapter routing in Phase 2
- Much simpler implementation achieves same goal
- Would require mastery data accumulation
- Current approach works well enough

**How to reactivate:**
1. Move from `archive/services/` back to `services/`
2. Add import to `services/__init__.py`
3. Integrate with AdaptiveLearningService
4. Would need to enhance student mastery tracking
5. Expected effort: 6-8 hours

**Dependencies:**
- `concept_mastery_tracker.py` (deleted in Week 2, in git history)
- `bloom_level_enforcer.py` (deleted in Week 2, in git history)

---

### 3. remediation_generator.py

**Purpose:** Generate personalized remediation questions  
**Size:** ~150 lines  
**Status:** Experimental  

**What it does:**
- Identifies misconceptions from wrong answers
- Generates targeted remediation questions
- Tracks misconception resolution
- Provides remediation path

**Why not integrated:**
- MisconceptionDetector works without remediation flow
- Would require full remediation UI/UX design
- Quiz flow doesn't currently support remediation branches
- Could be valuable future enhancement

**How to reactivate:**
1. Move from `archive/services/` back to `services/`
2. Add import to `services/__init__.py`
3. Integrate with MisconceptionDetector
4. Design remediation question flow
5. Add frontend UI for remediation branch
6. Expected effort: 8-12 hours

**Dependencies:**
- `misconception_analyzer.py` (currently active, would integrate)
- Question generation strategies (currently active)

**Use Case:**
When student has misconception in concept X:
1. Store misconception in session
2. Generate remediation questions for X
3. Show remediation flow in quiz
4. Track remediation success
5. Return to main quiz

---

### 4. performance_tracker.py

**Purpose:** Track and analyze student performance metrics  
**Size:** ~150 lines  
**Status:** Experimental  

**What it does:**
- Tracks accuracy per concept
- Calculates time-to-answer metrics
- Generates performance reports
- Identifies struggling areas

**Why not integrated:**
- Basic tracking in SessionAdapter is sufficient for current needs
- Would require analytics dashboard to display
- More sophisticated than what students/teachers currently use
- Could be valuable for future analytics dashboard

**How to reactivate:**
1. Move from `archive/services/` back to `services/`
2. Add import to `services/__init__.py`
3. Integrate with SessionAdapter.submit_answer()
4. Add analytics dashboard endpoints
5. Design frontend analytics UI
6. Expected effort: 8-10 hours (mostly frontend)

**Potential Dashboard Features:**
- Performance by chapter
- Accuracy trends over time
- Time-to-answer analysis
- Difficulty progression
- Concept mastery visualization

**Dependencies:**
- `concept_mastery_tracker.py` (deleted in Week 2, in git history)
- Analytics database schema (would need to design)

---

### 5. question_cache_service.py

**Purpose:** Redis-based caching for frequently used questions  
**Size:** ~100 lines  
**Status:** Experimental  

**What it does:**
- Caches generated questions in Redis
- Reduces question generation latency
- Tracks cache hit rates
- Manages cache expiration

**Why not integrated:**
- Current question generation is fast enough
- Adds infrastructure requirement (Redis)
- Cache invalidation complexity
- Not needed for current scale

**How to reactivate:**
1. Move from `archive/services/` back to `services/`
2. Set up Redis server (if not already available)
3. Add to `services/__init__.py`
4. Integrate with QuestionService.generate_question()
5. Add cache stats endpoint (partially done in content_routes.py)
6. Expected effort: 2-4 hours

**Benefits if reactivated:**
- Reduced question generation latency
- Lower CPU load on question generation
- Faster response times for students
- Better user experience at scale

**Use Cases:**
- High-traffic periods
- Repeated questions in same session
- Popular chapter combinations

**Infrastructure Requirement:**
- Redis server (can be local or cloud-based)
- Connection pooling configuration
- Cache expiration policy

---

## How to Reactivate a Service

### General Steps

1. **Move service back to production**
   ```bash
   mv archive/services/SERVICE_NAME.py services/
   ```

2. **Update services __init__.py**
   ```python
   from .SERVICE_NAME import SomeClass
   __all__ = [..., "SomeClass"]
   ```

3. **Update integration points**
   - Add to SessionAdapter if needed
   - Update endpoint handlers
   - Add dependency injection where needed

4. **Run tests**
   ```bash
   python -m pytest tests/ -v
   ```

5. **Test in development**
   - Use local test endpoints
   - Verify integration with active services
   - Check database interactions

6. **Deploy when ready**

### Effort Estimates

| Service | Effort | Priority |
|---------|--------|----------|
| question_cache_service | 2-4 hours | Medium (performance) |
| performance_tracker | 8-10 hours | Low (analytics) |
| adaptive_question_selector | 4-6 hours | Medium (quality) |
| sequencing_engine | 6-8 hours | Low (routing) |
| remediation_generator | 8-12 hours | Low (new feature) |

---

## Deleted Services (Not in Archive)

These services were deleted in Week 2 because they were dead code with no path to integration:

1. **session_manager.py** - Only used by deleted practice_routes
2. **bloom_level_enforcer.py** - Only used by deleted practice_routes
3. **concept_mastery_tracker.py** - Only used by deleted practice_routes
4. **break_point_tracker.py** - Only used by deleted practice_routes

**Recovery:** Available in git history if needed

---

## Archive Structure

```
archive/
├── README.md (this file)
├── docs/
│   └── (future documentation)
└── services/
    ├── adaptive_question_selector.py
    ├── sequencing_engine.py
    ├── remediation_generator.py
    ├── performance_tracker.py
    └── question_cache_service.py
```

---

## Why Archive Instead of Delete?

1. **Preserve Development Work**
   - ~750 lines of code (~20 hours of development)
   - Represents legitimate engineering effort
   - Reference implementations for future features

2. **Avoid Future Reimplementation**
   - If requirements change, code exists locally
   - No need to rebuild from scratch
   - Faster reactivation if prioritized

3. **Historical Record**
   - Track evolution of architecture
   - Understand design decisions
   - Learn from experimental approaches

4. **Git History**
   - All code still in git history
   - Can revert if needed
   - Full audit trail preserved

---

## Testing Archived Services

If you need to test an archived service before reactivation:

1. **Copy service back temporarily**
   ```bash
   cp archive/services/SERVICE_NAME.py services/SERVICE_NAME.py
   ```

2. **Run relevant tests**
   ```bash
   python -m pytest tests/test_service_name.py -v
   ```

3. **Remove if not reactivating**
   ```bash
   rm services/SERVICE_NAME.py
   ```

---

## Future Integration Paths

### Phase 3: Enhanced Features
- remediation_generator.py → Remediation quiz flow
- performance_tracker.py → Analytics dashboard

### Phase 4: Optimization
- question_cache_service.py → Production caching
- adaptive_question_selector.py → Advanced routing

### Phase 5: Advanced Learning
- sequencing_engine.py → Optimal learning paths
- All together → Complete adaptive learning system

---

## Questions About Archived Code?

Refer to:
1. Service docstrings (in each .py file)
2. Original implementation comments
3. Git history for context
4. Phase 2 Week 3 execution notes

---

**Archive Created:** January 1, 2026  
**Phase:** 2 Week 3  
**Status:** Ready for future activation  
**Last Updated:** January 1, 2026

