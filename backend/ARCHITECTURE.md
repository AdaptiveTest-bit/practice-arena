# Backend Architecture Documentation

**Last Updated:** January 1, 2026  
**Status:** Production-Ready  
**Phase 2 Completion:** Complete  

---

## Quick Start: How a Request Flows

```
HTTP Request → app_main.py → SessionAdapter → Database/Services → Response
```

Every quiz interaction follows this simple path:

1. **Request arrives** at `app_main.py` endpoint
2. **SessionAdapter** orchestrates the response
3. **Helper services** fetch data and process
4. **Response** sent back to frontend

---

## System Architecture Overview

### High-Level Components

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (Next.js)                      │
│                   Uses /api/quiz/* endpoints                    │
└────────────────────────────┬────────────────────────────────────┘
                             │
                    HTTP Requests/Responses
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                                                                  │
│                        app_main.py                              │
│                    (FastAPI Application)                        │
│                                                                  │
│  Endpoints:                                                     │
│  • /api/student/register       → User registration             │
│  • /api/quiz/session/*         → Session management            │
│  • /api/quiz/{id}/question     → Question generation           │
│  • /api/quiz/{id}/answer       → Answer submission             │
│  • /api/student/{id}/progress  → Progress tracking             │
│  • /api/content/question/rich  → Rich content generation       │
│                                                                  │
└────────────────────────────┬────────────────────────────────────┘
                             │
              Delegates to SessionAdapter & Routes
                             │
    ┌────────────────────────┼────────────────────────┐
    │                        │                        │
    ▼                        ▼                        ▼
┌──────────┐        ┌─────────────────┐      ┌──────────────┐
│SessionAdapter     │AdaptiveService  │      │RichQuestion  │
│(Orchestrator)     │(Chapter Routing)│      │Service       │
│                   │                 │      │              │
│Manages:           │Recommends:      │      │Generates:    │
│• Sessions         │• Next chapter   │      │• Story text  │
│• Questions        │• Mastery data   │      │• Rich HTML   │
│• Answers          │• Progression    │      │• LaTeX/Math  │
└────────┬──────────┴────────┬────────┴──────┴────────┬───────┘
         │                   │                        │
         └───────────────────┼────────────────────────┘
                             │
              Calls Helper Services Below
                             │
    ┌────────────┬───────────┼───────────┬──────────────┐
    │            │           │           │              │
    ▼            ▼           ▼           ▼              ▼
┌─────────┐ ┌─────────┐ ┌───────────┐ ┌──────────┐ ┌─────────┐
│Question │ │Misconc. │ │Deduplicat │ │Student   │ │Question │
│Factory  │ │Detector │ │Service    │ │Repository│ │Service  │
│         │ │         │ │           │ │          │ │         │
│Creates  │ │Analyzes │ │Prevents   │ │Database  │ │Caches   │
│Questions│ │Errors   │ │Duplicates │ │Access    │ │Questions│
└────┬────┘ └─────────┘ └───────────┘ └──────────┘ └─────────┘
     │
     ▼
┌──────────────────────────────────────┐
│      16 Chapter Strategies           │
│  (QuestionStrategy subclasses)       │
│                                      │
│  Factors, Decimals, Symmetry,       │
│  Rotation, Nets, Dice, Data,        │
│  Angles, Measurement, etc.          │
└──────────────────────────────────────┘
```

---

## Core Components (Active - Production)

### 1. SessionAdapter (Orchestrator)
**File:** `services/session_adapter.py`  
**Purpose:** Main request handler for all quiz operations  

**Responsibilities:**
- Create and manage quiz sessions
- Orchestrate question generation
- Process answer submissions
- Track student progress
- Detect misconceptions
- Handle hint requests
- Coordinate all helper services

**Key Methods:**
- `start_session()` - Initialize a quiz session
- `get_next_question()` - Generate next question
- `submit_answer()` - Process answer and update progress
- `get_misconceptions()` - Return detected misconceptions
- `end_session()` - Finalize session

**Used By:** All endpoints in app_main.py

---

### 2. ORMStudentRepository (Database)
**File:** `services/orm_student_repository.py`  
**Purpose:** All database access for students and sessions  

**Responsibilities:**
- Student CRUD operations
- Session persistence
- Answer recording
- Progress storage
- Query student data

**Database Tables:**
- `students` - Student profiles
- `student_sessions` - Quiz sessions
- `answers` - Submitted answers
- `misconceptions` - Detected misconceptions

**Used By:** SessionAdapter, progress tracking

---

### 3. AdaptiveLearningService (Adaptive Routing)
**File:** `services/adaptive_learning_service.py`  
**Purpose:** Recommend next chapter based on mastery  

**Responsibilities:**
- Calculate mastery levels
- Recommend next chapter
- Track learning progression
- Provide difficulty suggestions

**Algorithm:**
```
1. Get student's performance on current chapter
2. Calculate mastery percentage
3. If mastery > threshold:
   → Recommend next chapter (easier difficulty)
4. If mastery < threshold:
   → Recommend same chapter (harder questions)
5. Return recommendation with rationale
```

**Used By:** SessionAdapter.get_next_question()

---

### 4. MisconceptionDetector (Misconception Analysis)
**File:** `services/misconception_analyzer.py`  
**Purpose:** Identify and tag student misconceptions  

**Responsibilities:**
- Analyze wrong answers
- Identify misconception patterns
- Tag common mistakes
- Return misconception details

**Process:**
```
1. Student submits wrong answer
2. Analyze the wrong option chosen
3. Determine misconception type
4. Store in database
5. Return misconception info to frontend
```

**Used By:** SessionAdapter.submit_answer()

---

### 5. QuestionGeneratorFactory (Strategy Creation)
**File:** `factory.py`  
**Purpose:** Create appropriate question generator for chapter  

**Responsibilities:**
- Instantiate correct strategy class
- Handle chapter-to-strategy mapping
- Provide strategy instance to caller

**Supported Chapters:** 16 total
- Factors & Multiples
- Fractions & Decimals
- Symmetry & Rotation
- Data Handling
- Nets & Measurement
- And 11 more...

**Used By:** SessionAdapter, Question generation pipeline

---

### 6. QuestionStrategy Classes (Question Generation)
**Files:** `strategies/*.py` (16 total)  
**Purpose:** Generate questions for specific chapters  

**Naming Convention:** `{chapter}_integrated.py`  
**Each Strategy:**
- Inherits from base QuestionStrategy
- Implements `generate()` method
- Uses SymPy for math backbone
- Uses LLM for story context
- Returns Question object with:
  - Story narrative
  - Question text
  - Multiple choice options
  - Correct answer index
  - Rich content (HTML, LaTeX)

**Example:** `factors_multiples_integrated.py`
```python
class FactorsMultiplesStrategy(QuestionStrategy):
    def generate(self, difficulty=1.0, student=None):
        # 1. Use SymPy to generate math problem
        # 2. Get K.C. Nag story context from LLM
        # 3. Create distractors
        # 4. Render rich content
        # 5. Return Question object
```

**Used By:** QuestionGeneratorFactory → SessionAdapter

---

### 7. DeduplicationService (Duplicate Prevention)
**File:** `services/deduplication.py`  
**Purpose:** Prevent students from seeing same question twice  

**Responsibilities:**
- Track questions shown in session
- Check if question is duplicate
- Remove duplicates before returning

**Process:**
```
1. Question is generated
2. Check if seen in this session
3. If yes: regenerate question
4. If no: return to student
5. Mark as seen for this session
```

**Used By:** Question generation pipeline

---

## Data Flow Examples

### Example 1: Student Starts Quiz

```
Frontend: POST /api/quiz/session/start
         {student_id: "s1", chapter: "Factors"}
              ↓
app_main.py: start_quiz_session()
              ↓
SessionAdapter.start_session(student_id, chapter)
              ↓
ORMStudentRepository.create_session(student_id, chapter)
              ↓
Database: INSERT into student_sessions
              ↓
SessionAdapter: Returns session_id
              ↓
Frontend: Receives {session_id: "sess_123", status: "started"}
```

### Example 2: Get Next Question

```
Frontend: GET /api/quiz/sess_123/question
              ↓
app_main.py: get_quiz_question(session_id)
              ↓
SessionAdapter.get_next_question(session_id)
              ↓
Step 1: Get student data
└─→ ORMStudentRepository.get_student(student_id)
     └─→ Database query
     └─→ Returns student object

Step 2: Determine chapter to quiz on
└─→ AdaptiveLearningService.generate_recommendation(student)
     └─→ Calculate mastery on current chapter
     └─→ Recommend next chapter or stay
     └─→ Returns recommendation

Step 3: Generate question for recommended chapter
└─→ QuestionGeneratorFactory.create_strategy(chapter)
     └─→ Returns FactorsMultiplesStrategy (example)
└─→ strategy.generate(difficulty, student)
     └─→ Create math problem with SymPy
     └─→ Generate story with LLM
     └─→ Create options and correct answer
     └─→ Render rich content (HTML, LaTeX)
     └─→ Returns Question object

Step 4: Check for duplicates
└─→ DeduplicationService.check_duplicate(question, session_id)
     └─→ Is this question shown before in this session?
     └─→ If yes: go back to Step 3 (regenerate)
     └─→ If no: continue

Step 5: Cache and return
└─→ QuestionService.cache_question(question_id, question)
└─→ SessionAdapter.return_question(question)
     └─→ Returns Question to frontend
     
Frontend: Receives
{
  question_id: "q_456",
  question_text: "What are the factors of 24?",
  options: ["2, 3, 4", "1, 2, 3, 4, 6, 8, 12, 24", ...],
  correct_index: 1,
  rich_narrative: "In a bakery, 24 cookies...",
  rich_html_content: "<div>...</div>"
}
```

### Example 3: Submit Answer

```
Frontend: POST /api/quiz/sess_123/answer
         {question_id: "q_456", selected_index: 0}
              ↓
app_main.py: submit_quiz_answer(session_id, question_id, answer)
              ↓
SessionAdapter.submit_answer(session_id, question_id, selected_index)
              ↓
Step 1: Validate answer
└─→ Get question from cache
└─→ Compare selected_index with correct_index
└─→ Determine: correct or incorrect

Step 2: Analyze misconception (if wrong)
└─→ MisconceptionDetector.analyze(student, question, wrong_answer)
     └─→ Which option did student pick?
     └─→ What misconception does that represent?
     └─→ Tag the misconception
     └─→ Returns misconception_tags

Step 3: Update student progress
└─→ ORMStudentRepository.record_answer(...)
     └─→ Save answer to database
     └─→ Update mastery calculation
     └─→ Update accuracy for chapter

Step 4: Return feedback
└─→ SessionAdapter returns:
{
  is_correct: false,
  correct_answer: "1, 2, 3, 4, 6, 8, 12, 24",
  feedback: "Not quite. Remember that factors...",
  misconception: "counting_factors_incorrectly",
  mastery_update: {chapter: "Factors", new_accuracy: 0.65}
}

Frontend: Shows feedback to student
```

---

## Configuration

### Database
- **Type:** PostgreSQL
- **ORM:** SQLAlchemy
- **Connection:** Via `core/database.py`
- **Schema:** Auto-created from models

### Settings
- **File:** `config/settings.py`
- **Contains:** Database URL, API keys, logging config
- **Environment:** Load from environment variables

### Logging
- **File:** `config/logging_config.py`
- **Format:** JSON for structured logging
- **Levels:** DEBUG, INFO, WARNING, ERROR

---

## Adding a New Feature

### Scenario: Add a new chapter

**Steps:**

1. **Create Strategy Class**
   ```bash
   # Create: backend/strategies/new_chapter_integrated.py
   
   from models.question import Question
   from .base import QuestionStrategy
   
   class NewChapterStrategy(QuestionStrategy):
       def generate(self, difficulty=1.0, student=None):
           # Your implementation
           return Question(...)
   ```

2. **Register in Factory**
   ```python
   # File: backend/factory.py
   # Add to create() method:
   
   if chapter == ChapterEnum.NEW_CHAPTER:
       return NewChapterStrategy()
   ```

3. **Add to ChapterEnum**
   ```python
   # File: backend/models/question.py
   
   class ChapterEnum(str, Enum):
       NEW_CHAPTER = "new_chapter"  # Add this
   ```

4. **Test**
   ```python
   # File: backend/test_new_chapter.py
   
   def test_new_chapter():
       strategy = QuestionGeneratorFactory.create(ChapterEnum.NEW_CHAPTER)
       question = strategy.generate()
       assert question is not None
   ```

5. **Deploy**
   - All endpoints automatically pick up the new chapter
   - No other changes needed

---

## Deployment Considerations

### Environment Variables Required
```
DATABASE_URL=postgresql://user:pass@host/db
OPENAI_API_KEY=sk_...
REDIS_URL=redis://...  (optional, for caching)
LOG_LEVEL=INFO
```

### Startup Process
```
1. Load configuration (config/settings.py)
2. Initialize database connection
3. Create tables if needed (SQLAlchemy auto-create)
4. Initialize logging
5. Start FastAPI server
6. Load all strategies (lazy-loaded)
7. Ready to accept requests
```

### Health Check
```bash
curl http://localhost:8000/health
# Expected: 200 OK with status info
```

### Performance Notes
- Question generation: ~100-500ms (SymPy + LLM)
- Answer checking: ~10-50ms
- Database queries: ~5-20ms
- Total request time: ~200-600ms

---

## Monitoring & Debugging

### Logs Location
```
backend/backend.log  (if configured)
```

### Common Issues

**Problem:** Questions not being generated  
**Solution:** Check if strategy is registered in factory.py

**Problem:** Student answers not being saved  
**Solution:** Verify DATABASE_URL is set and database is accessible

**Problem:** Rich content not showing  
**Solution:** Ensure LLM API key is set and has quota

---

## Files Not in Use (Archived)

See `backend/archive/README.md` for:
- `adaptive_question_selector.py` - Advanced selection (not integrated)
- `sequencing_engine.py` - Optimal sequencing (not integrated)
- `remediation_generator.py` - Remediation flow (not integrated)
- `performance_tracker.py` - Analytics (not integrated)
- `question_cache_service.py` - Redis caching (not integrated)

These can be reactivated if features are prioritized.

---

## Summary

This backend provides a clean, modular architecture for generating adaptive math questions:

✅ **SessionAdapter** - Orchestrates all operations  
✅ **Services** - Modular, testable components  
✅ **Strategies** - Easy to add new chapters  
✅ **Database** - Persistent storage with SQLAlchemy  
✅ **Adaptive** - Routes students optimally  
✅ **Rich Content** - Beautiful, semantic questions  
✅ **Documented** - Architecture clear and explained  

Ready for production use and scaling.

---

**For More Information:**
- See `/backend/archive/README.md` for archived services
- See individual service docstrings for detailed APIs
- See tests for usage examples

