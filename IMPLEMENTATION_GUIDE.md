"""QUICK START: IMPLEMENTING THE REFACTORED ARCHITECTURE

This guide walks through the refactoring step-by-step with complete code examples.

## SETUP (5 minutes)

### 1. Install Dependencies

\`\`\`bash
pip install fastapi==0.104.1 uvicorn[standard]==0.24.0 pydantic==2.4.2
\`\`\`

### 2. Create Directory Structure

\`\`\`bash
mkdir -p models strategies services
touch models/__init__.py strategies/__init__.py services/__init__.py
touch factory.py
\`\`\`

## IMPLEMENTATION GUIDE

### Phase 1: Core Infrastructure (20 minutes)

#### Step 1.1: Create Pydantic Models

**File: models/question.py** ✓ DONE (provided)

Contains:
- ChapterEnum: All 12 chapters as type-safe enums
- Question: Main data model with validation
- Response models: QuestionResponse, CheckAnswerResponse, etc.

#### Step 1.2: Create Base Strategy Class

**File: strategies/base.py** ✓ DONE (provided)

Key features:
- \`ensure_unique_options()\`: Static helper for MCQ dedup
- \`shuffle_options_keep_correct()\`: Helper for option shuffling
- \`_validate_question()\`: Validates question structure

Usage:
\`\`\`python
class MyStrategy(BaseChapterStrategy):
    chapter = ChapterEnum.MY_CHAPTER
    chapter_name = "My Chapter"
    
    def generate(self) -> Question:
        # Generate your question
        question = Question(...)
        self._validate_question(question)  # Always validate!
        return question
    
    # Use helpers:
    options = self.ensure_unique_options([correct] + distractors)
    options, correct_idx = self.shuffle_options_keep_correct(correct, distractors)
\`\`\`

#### Step 1.3: Create Factory Pattern

**File: factory.py** ✓ DONE (provided)

Usage:
\`\`\`python
# Register a strategy (typically in app startup)
QuestionGeneratorFactory.register(ChapterEnum.LARGE_NUMBERS, LargeNumbersStrategy)

# Create strategy instance
strategy = QuestionGeneratorFactory.create(ChapterEnum.LARGE_NUMBERS)
strategy = QuestionGeneratorFactory.create("large_numbers")  # Works with strings too

# List all registered
chapters = QuestionGeneratorFactory.list_chapters()
\`\`\`

#### Step 1.4: Create Services

**File: services/deduplication.py** ✓ DONE (provided)

Session-level dedup tracking:
\`\`\`python
service = DeduplicationService()

# Create session for a user
session_id = service.create_session()

# Track questions
is_dup = service.is_duplicate(session_id, question)
service.track_question(session_id, question)

# Get stats
stats = service.get_stats(session_id)
# Returns: {unique_questions: 10, duplicates_regenerated: 1, success_rate: 90.9}

# Cleanup
service.delete_session(session_id)
\`\`\`

**File: services/question_service.py** ✓ DONE (provided)

High-level orchestration:
\`\`\`python
service = QuestionService()

# Create session
session_id = service.create_session()

# Generate question with auto-dedup
question, question_id = service.generate_question(session_id, ChapterEnum.LARGE_NUMBERS)
# Automatically retries up to 5 times if duplicate detected

# Retrieve cached question
question = service.get_question_by_id(question_id)

# Get stats
stats = service.get_session_stats(session_id)

# Cleanup
service.end_session(session_id)
\`\`\`

### Phase 2: Implement One Example Strategy (15 minutes)

**File: strategies/large_numbers.py** ✓ DONE (provided)

Key points:
- Inherits from BaseChapterStrategy
- Sets chapter, chapter_name, description
- Implements generate() with random problem type
- Each problem type is a separate method
- Always validates before returning

Example method structure:
\`\`\`python
def _generate_place_value(self) -> Question:
    # 1. Generate problem data
    scenario = random.choice(scenarios)
    
    # 2. Create correct answer
    correct_answer = scenario['words']
    
    # 3. Create distractors (wrong answers)
    distractors = [
        scenario['words'].replace("lakh", "million"),
        # ... more distractors ...
    ]
    
    # 4. Ensure unique options and shuffle
    options, correct_idx = self.shuffle_options_keep_correct(correct_answer, distractors)
    
    # 5. Create question with all required fields
    question = Question(
        chapter=self.chapter,
        topic="Number Systems - Large Numbers & Place Value",
        logical_trap="Students confuse...",
        data_representation="...",
        question_text="...",
        solution_steps=["Step 1", "Step 2", ...],
        answer=correct_answer,
        options=options,
        correct_option_index=correct_idx
    )
    
    # 6. Always validate
    self._validate_question(question)
    return question
\`\`\`

### Phase 3: Create FastAPI Application (30 minutes)

**File: app_refactored.py** ✓ DONE (provided)

Three main components:

#### 3.1 Lifespan (Startup/Shutdown)

\`\`\`python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP: Register strategies
    QuestionGeneratorFactory.register(ChapterEnum.LARGE_NUMBERS, LargeNumbersStrategy)
    # ... register other strategies ...
    
    # Initialize service
    app.state.question_service = QuestionService()
    
    yield  # App runs here
    
    # SHUTDOWN: Cleanup
    logger.info("Shutting down...")

app = FastAPI(lifespan=lifespan)
\`\`\`

#### 3.2 API Routes

**Session Management:**
\`\`\`python
@app.post("/api/session")
async def create_session():
    service = app.state.question_service
    session_id = service.create_session()
    return {"success": True, "sessionId": session_id}

@app.delete("/api/session/{session_id}")
async def end_session(session_id: str):
    service = app.state.question_service
    service.end_session(session_id)
    return {"success": True}
\`\`\`

**Question Generation:**
\`\`\`python
@app.post("/api/question", response_model=QuestionResponse)
async def generate_question(request: Request):
    service = app.state.question_service
    body = await request.json()
    
    session_id = body["sessionId"]
    chapter = ChapterEnum(body.get("chapter", "large_numbers"))
    
    question, question_id = service.generate_question(session_id, chapter)
    
    return QuestionResponse(
        success=True,
        questionId=question_id,
        chapter=chapter.value,
        topic=question.topic,
        logicalTrap=question.logical_trap,
        # ... rest ...
    )
\`\`\`

**Answer Checking:**
\`\`\`python
@app.post("/api/check-answer/{question_id}", response_model=CheckAnswerResponse)
async def check_answer(question_id: str, body: CheckAnswerRequest):
    service = app.state.question_service
    question = service.get_question_by_id(question_id)
    
    is_correct = body.selectedIndex == question.correct_option_index
    
    return CheckAnswerResponse(
        success=True,
        isCorrect=is_correct,
        correctIndex=question.correct_option_index,
        solutionSteps=question.solution_steps,
        answer=question.answer
    )
\`\`\`

## TESTING THE IMPLEMENTATION

### Manual Testing

\`\`\`bash
# Start server
python -m uvicorn app_refactored:app --reload --port 5002

# In another terminal:

# 1. Create session
curl -X POST http://localhost:5002/api/session

# 2. Get question ID from response
# 3. Request question
curl -X POST http://localhost:5002/api/question \\
  -H "Content-Type: application/json" \\
  -d '{
    "sessionId": "YOUR_SESSION_ID",
    "chapter": "large_numbers"
  }'

# 4. Check answer
curl -X POST http://localhost:5002/api/check-answer/YOUR_QUESTION_ID \\
  -H "Content-Type: application/json" \\
  -d '{"selectedIndex": 2}'

# 5. Get stats
curl http://localhost:5002/api/session/YOUR_SESSION_ID/stats

# 6. Cleanup
curl -X DELETE http://localhost:5002/api/session/YOUR_SESSION_ID
\`\`\`

### Unit Tests

\`\`\`python
# test_strategies.py
from strategies.large_numbers import LargeNumbersStrategy
from models.question import ChapterEnum

def test_large_numbers_strategy():
    strategy = LargeNumbersStrategy()
    
    # Generate multiple questions
    for _ in range(10):
        question = strategy.generate()
        
        # Validate structure
        assert question.chapter == ChapterEnum.LARGE_NUMBERS
        assert len(question.options) == 4
        assert len(set(question.options)) == 4  # All unique
        assert question.correct_option_index in [0, 1, 2, 3]
        assert question.answer in question.options
        
        # Validate content
        assert question.topic is not None
        assert question.logical_trap is not None
        assert question.question_text is not None
        assert len(question.solution_steps) > 0

def test_factory():
    from factory import QuestionGeneratorFactory
    
    strategy = QuestionGeneratorFactory.create(ChapterEnum.LARGE_NUMBERS)
    assert strategy.chapter == ChapterEnum.LARGE_NUMBERS
    
    # Should work with string too
    strategy2 = QuestionGeneratorFactory.create("large_numbers")
    assert type(strategy) == type(strategy2)

def test_deduplication():
    from services.deduplication import DeduplicationService
    
    service = DeduplicationService()
    session = service.create_session()
    
    # Create two identical questions
    q1 = Question(
        chapter=ChapterEnum.LARGE_NUMBERS,
        topic="Test",
        logical_trap="Test",
        data_representation="Test",
        question_text="What is 2+2?",
        solution_steps=["2+2=4"],
        answer="4"
    )
    q2 = Question(
        chapter=ChapterEnum.LARGE_NUMBERS,
        topic="Different",
        logical_trap="Different",
        data_representation="Different",
        question_text="What is 2+2?",
        solution_steps=["Different"],
        answer="4"
    )
    
    # Same question_text + answer = same fingerprint
    assert q1.get_fingerprint() == q2.get_fingerprint()
    
    # Track first
    assert not service.is_duplicate(session, q1)
    service.track_question(session, q1)
    
    # Second should be detected as duplicate
    assert service.is_duplicate(session, q2)
\`\`\`

## CONVERTING EXISTING GENERATORS

### Example: Converting DiceLogicGenerator

**Original Code (question_generator.py):**
\`\`\`python
class DiceLogicGenerator(QuestionGenerator):
    def generate(self) -> Question:
        problem_type = random.choice(["standard_dice", "logic_trap", ...])
        # ... implementation ...
        return Question(...)
\`\`\`

**Refactored Code (strategies/dice_logic.py):**
\`\`\`python
from strategies.base import BaseChapterStrategy
from models.question import Question, ChapterEnum

class DiceLogicStrategy(BaseChapterStrategy):
    chapter = ChapterEnum.DICE_LOGIC
    chapter_name = "Dice Logic"
    description = "Opposite faces sum to 7"
    
    def generate(self) -> Question:
        problem_type = random.choice(["standard_dice", "logic_trap", ...])
        
        if problem_type == "standard_dice":
            return self._generate_standard_dice()
        elif problem_type == "logic_trap":
            return self._generate_logic_trap()
        # ... etc
    
    def _generate_standard_dice(self) -> Question:
        # Copy existing implementation
        # CHANGE: Add chapter=self.chapter to Question()
        # CHANGE: Call self._validate_question(question) before return
        question = Question(
            chapter=self.chapter,
            # ... rest of fields ...
        )
        self._validate_question(question)
        return question
    
    # Copy all other _generate_* methods
    # Add self._validate_question() to each one
\`\`\`

**Steps:**
1. Create new file: strategies/dice_logic.py
2. Copy class definition, rename to DiceLogicStrategy
3. Change parent class to BaseChapterStrategy
4. Add chapter, chapter_name, description attributes
5. Copy all _generate_* methods
6. In each method:
   - Add chapter=self.chapter to Question()
   - Add self._validate_question(question) before return
   - Use self.ensure_unique_options() instead of manual dedup
7. Register in app_refactored.py:
   - \`QuestionGeneratorFactory.register(ChapterEnum.DICE_LOGIC, DiceLogicStrategy)\`
8. Add to CHAPTER_METADATA
9. Test

## DEPLOYMENT STRATEGY

### Week 1: Parallel Deployment

\`\`\`
POST /api/question (OLD Flask app)
↓
Still works, backward compatible

POST /api/question (NEW FastAPI app on port 5002)
↓
Testing and monitoring
\`\`\`

### Week 2: Gradual Migration

\`\`\`
Client requests to /api/question
↓
50% → OLD Flask
50% → NEW FastAPI (via load balancer or canary)
↓
Monitor metrics, error rates
\`\`\`

### Week 3: Full Cutover

\`\`\`
Client requests to /api/question
↓
100% → NEW FastAPI
\`\`\`

## VERIFICATION CHECKLIST

Before deploying:

- [ ] All Pydantic models validate correctly
- [ ] Factory creates correct strategy instances
- [ ] All strategies have chapter attribute
- [ ] All strategies implement generate()
- [ ] All questions pass _validate_question()
- [ ] MCQ options are always 4 unique items
- [ ] Correct answer is always in options
- [ ] DeduplicationService tracks fingerprints
- [ ] QuestionService retries on duplicates
- [ ] FastAPI routes return correct response models
- [ ] No duplicate options in 36+ generated questions (100% success rate)
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Load test shows acceptable performance

## NEXT STEPS

1. Implement remaining 11 chapter strategies (copy/paste with small changes)
2. Register all in factory
3. Update CHAPTER_METADATA for all
4. Run comprehensive tests
5. Deploy to staging
6. Integration test with real frontend
7. Deploy to production
8. Archive old code

Good luck! 🚀
"""
