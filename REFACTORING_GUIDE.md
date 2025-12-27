"""ARCHITECTURE REFACTORING GUIDE

This document explains the new architecture, how to migrate from the old codebase,
and how to extend it with new chapters.

## OVERVIEW

The refactored codebase follows SOLID principles using three main design patterns:

1. **Strategy Pattern**: Each chapter (e.g., Large Numbers, Geometry) has its own
   strategy class inheriting from BaseChapterStrategy

2. **Factory Pattern**: QuestionGeneratorFactory instantiates the correct strategy
   based on chapter name, eliminating large if-else blocks

3. **Service Layer**: QuestionService orchestrates generation, deduplication, and caching

## FOLDER STRUCTURE

```
question-generator/
├── app_refactored.py               # FastAPI application (new)
├── models/
│   ├── question.py                 # Pydantic models (Question, Response types)
│   └── __init__.py
├── strategies/
│   ├── base.py                     # BaseChapterStrategy abstract class
│   ├── large_numbers.py            # Example implementation
│   ├── dice_logic.py               # TODO
│   ├── cube_counting.py            # TODO
│   └── __init__.py
├── factory.py                      # QuestionGeneratorFactory
├── services/
│   ├── deduplication.py            # Session-level uniqueness tracking
│   ├── question_service.py         # Business logic orchestrator
│   └── __init__.py
└── question_generator.py           # (Original, keep for backward compatibility)
```

## KEY COMPONENTS

### 1. BaseChapterStrategy (strategies/base.py)

Abstract base class that all chapter strategies inherit from.

**Key Methods:**
- `generate()`: Abstract method that subclasses must implement
- `ensure_unique_options()`: Static helper to deduplicate MCQ options
- `shuffle_options_keep_correct()`: Shuffles options while tracking correct answer
- `_validate_question()`: Validates question structure

**Why**: Ensures consistency across all chapters, provides shared utilities

### 2. QuestionGeneratorFactory (factory.py)

Factory that creates strategy instances without exposing concrete classes.

**Usage:**
```python
from models.question import ChapterEnum
from factory import QuestionGeneratorFactory

# Create a strategy
strategy = QuestionGeneratorFactory.create(ChapterEnum.LARGE_NUMBERS)

# Or from string
strategy = QuestionGeneratorFactory.create("large_numbers")
```

**Benefits**:
- No hardcoded if-else checks for chapter names
- Easy to add/remove chapters
- Testable and mockable

### 3. Question Model (models/question.py)

Pydantic BaseModel for strict validation of all question data.

**Fields**:
- topic, logical_trap, data_representation, question_text
- solution_steps, answer
- options (optional): List of 4 MCQ choices
- correct_option_index (optional): Index of correct answer
- chapter: ChapterEnum

**Methods**:
- `get_fingerprint()`: SHA256 hash for deduplication
- `format_for_display()`: Human-readable output

### 4. QuestionService (services/question_service.py)

High-level service orchestrating generation, deduplication, and caching.

**Key Methods**:
- `create_session()`: Create a new dedup session
- `generate_question(session_id, chapter)`: Generate unique question with automatic retry
- `get_question_by_id(question_id)`: Retrieve cached question
- `get_session_stats(session_id)`: Get dedup statistics
- `end_session(session_id)`: Clean up session

### 5. DeduplicationService (services/deduplication.py)

Tracks question fingerprints per session to prevent duplicates.

**Key Methods**:
- `create_session()`: Create new session
- `is_duplicate()`: Check if question was generated before
- `track_question()`: Add fingerprint to session
- `get_stats()`: Get dedup statistics

## MIGRATION GUIDE

### Step 1: Keep Old Codebase (Parallel)

The original `question_generator.py` is NOT deleted. This allows:
- Gradual migration
- Testing new architecture side-by-side
- Rollback if issues found

### Step 2: Convert Existing Generators to Strategies

For each generator in `question_generator.py`:

**Before (Old Code):**
```python
class DiceLogicGenerator(QuestionGenerator):
    def generate(self) -> Question:
        # ... generate logic ...
        return Question(...)
```

**After (New Strategy):**
```python
# File: strategies/dice_logic.py
from strategies.base import BaseChapterStrategy
from models.question import Question, ChapterEnum

class DiceLogicStrategy(BaseChapterStrategy):
    chapter = ChapterEnum.DICE_LOGIC
    chapter_name = "Dice Logic"
    
    def generate(self) -> Question:
        # ... same generate logic ...
        question = Question(
            chapter=self.chapter,
            topic="...",
            # ... other fields ...
        )
        self._validate_question(question)
        return question
```

**Key Changes**:
1. Inherit from `BaseChapterStrategy` instead of `QuestionGenerator`
2. Set `chapter`, `chapter_name` class attributes
3. Add `chapter=self.chapter` to Question constructor
4. Call `self._validate_question(question)` before returning

### Step 3: Register Strategies in Factory

In `app_refactored.py` lifespan startup:

```python
QuestionGeneratorFactory.register(ChapterEnum.DICE_LOGIC, DiceLogicStrategy)
QuestionGeneratorFactory.register(ChapterEnum.CUBE_COUNTING, CubeCountingStrategy)
# ... etc for all chapters
```

### Step 4: Update API Calls

**Old (Flask):**
```python
generator = GENERATORS[category]
question = generator.generate()
questions_cache[question_id] = question
```

**New (FastAPI with Service):**
```python
question, question_id = service.generate_question(session_id, chapter)
# Caching handled automatically by service
```

## EXTENDING WITH NEW CHAPTERS

To add a new chapter (e.g., "Algebra"):

### 1. Create Strategy Class

```python
# File: strategies/algebra.py
from strategies.base import BaseChapterStrategy
from models.question import Question, ChapterEnum

class AlgebraStrategy(BaseChapterStrategy):
    chapter = ChapterEnum.ALGEBRA
    chapter_name = "Algebra"
    description = "Variables, equations, expressions"
    
    def generate(self) -> Question:
        problem_type = random.choice(["linear_equation", "variable_expression"])
        
        if problem_type == "linear_equation":
            return self._generate_linear_equation()
        else:
            return self._generate_variable_expression()
    
    def _generate_linear_equation(self) -> Question:
        # Your implementation
        question = Question(
            chapter=self.chapter,
            topic="Algebra - Linear Equations",
            logical_trap="...",
            data_representation="...",
            question_text="...",
            solution_steps=[...],
            answer="...",
            options=self.ensure_unique_options([...]),
            correct_option_index=...
        )
        self._validate_question(question)
        return question
```

### 2. Add to ChapterEnum

```python
# In models/question.py
class ChapterEnum(str, Enum):
    # ... existing ...
    ALGEBRA = "algebra"
```

### 3. Register in Factory

```python
# In app_refactored.py lifespan
QuestionGeneratorFactory.register(ChapterEnum.ALGEBRA, AlgebraStrategy)
```

### 4. Add Metadata

```python
# In app_refactored.py
CHAPTER_METADATA = {
    # ... existing ...
    ChapterEnum.ALGEBRA: {
        'name': 'Algebra',
        'icon': '🔤',
        'chapter': 'Algebra',
        'description': 'Variables, equations, expressions'
    }
}
```

## ADVANTAGES OF THIS ARCHITECTURE

### 1. Separation of Concerns
- Strategy classes contain ONLY question generation logic
- Service layer handles orchestration and caching
- Models define data contracts
- Factory handles instantiation

### 2. Easy to Test
```python
# Can test strategy in isolation
strategy = AlgebraStrategy()
question = strategy.generate()
assert question.chapter == ChapterEnum.ALGEBRA

# Can test deduplication separately
service = QuestionService()
session = service.create_session()
q1, _ = service.generate_question(session, ChapterEnum.ALGEBRA)
q2, _ = service.generate_question(session, ChapterEnum.ALGEBRA)
assert q1.get_fingerprint() != q2.get_fingerprint()
```

### 3. Type Safety
- Pydantic models validate all data
- ChapterEnum prevents typos
- IDE autocomplete works better

### 4. Scalability
- Adding 10 new chapters = 10 new files
- No changes to factory, service, or API logic
- Strategies can be in separate modules/packages

### 5. Maintainability
- Changes to one chapter don't affect others
- No large if-else blocks to navigate
- Clear separation of responsibilities

## PYDANTIC MODELS BREAKDOWN

### Question Model

Validates that every question has:
- Required fields: topic, logical_trap, data_representation, etc.
- Consistent MCQ structure (4 options if provided)
- Valid correct_option_index (0-3)

### Response Models

- **QuestionResponse**: API response for question generation
- **CheckAnswerResponse**: API response for answer checking
- **RevealAnswerResponse**: API response for revealing answer
- **CheckAnswerRequest**: Validates incoming request body

Benefits:
- Auto documentation (Swagger/OpenAPI)
- Type checking at runtime
- Automatic serialization to JSON
- Clear contract between client and server

## SESSION & DEDUPLICATION FLOW

```
1. Client creates session:
   POST /api/session
   <- Returns sessionId

2. Client requests question with session:
   POST /api/question
   Body: { "sessionId": "uuid", "chapter": "large_numbers" }
   
3. Service generates question:
   a. Creates strategy via factory
   b. Calls strategy.generate()
   c. Checks dedup service: is_duplicate(sessionId, question)?
   d. If duplicate: retry (max 5 times)
   e. If unique: add to dedup set, cache, return
   
4. Client submits answer:
   POST /api/check-answer/{questionId}
   Body: { "selectedIndex": 2 }
   <- Service looks up cached question, compares index
   
5. Client asks for stats:
   GET /api/session/{sessionId}/stats
   <- Returns unique_count, duplicate_count, success_rate
   
6. Session cleanup:
   DELETE /api/session/{sessionId}
   <- Removes session from dedup service
```

## REQUIREMENTS.TXT UPDATE

Add to requirements.txt:
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.4.2
pydantic-settings==2.0.3
```

Keep existing dependencies for backward compatibility.

## ROLLOUT STRATEGY

**Phase 1 (Week 1):**
- Deploy refactored code alongside old code
- Update API to use new QuestionService
- Keep old Flask app running for comparison
- Monitor for bugs

**Phase 2 (Week 2):**
- Replace Flask with FastAPI entirely
- Migrate all chapter generators to strategies
- Run comprehensive tests
- Document new API for clients

**Phase 3 (Week 3):**
- Remove old question_generator.py imports from Flask app
- Archive old code in git tag
- Full cutover to new architecture

**Rollback Plan:**
- Keep old Flask app runnable
- Git branching allows quick revert
- Data migration is automatic (no schema changes)

## NOTES & BEST PRACTICES

1. **Always Validate**: Call `self._validate_question()` in every strategy
2. **Use Helpers**: Leverage `ensure_unique_options()` to avoid duplicate MCQ options
3. **Type Hints**: Use `ChapterEnum` not strings for chapters
4. **Logging**: Add logger.info() calls for debugging
5. **Session Management**: Always cleanup sessions with DELETE endpoint
6. **Error Handling**: Return meaningful HTTP errors (400, 404, 500)
"""
