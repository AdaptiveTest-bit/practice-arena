# Notion CMS Migration Plan: Factors & Multiples

## Executive Summary

Migrate from on-the-fly SymPy-based generation (`FactorsMultiplesIntegrated`) to **Notion CMS + Redis Cache + Python Engine** architecture while preserving the existing adaptive learning layer (selector, sequencer, concept_graph, mastery).

**Key Constraint:** The new `NotionQuestionEngine` must implement the same interface as `FactorsMultiplesIntegrated`:
```python
def generate(self, concept_key: str = None, difficulty: int = None, bloom_level: BloomLevel = None) -> Question
```

---

## Current Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         SESSION SERVICE                              │
│  domain/session_management/service.py                               │
│  └── _get_adaptive_question()                                       │
└───────────────────────────┬─────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  ADAPTIVE QUESTION SELECTOR                          │
│  domain/adaptation/selector.py                                       │
│  ├── ConceptGraph (from concept_graph.py)                           │
│  ├── MasteryTracker (from mastery.py)                               │
│  ├── Sequencer (from sequencer.py)                                  │
│  └── self.generator = FactorsMultiplesIntegrated()  ◄── REPLACE    │
└───────────────────────────┬─────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│              FACTORS MULTIPLES GENERATOR (CURRENT)                   │
│  domain/content_generation/generators/factors_multiples.py          │
│  ├── 2015 lines of Python + SymPy + K.C. Nag stories               │
│  ├── Generates questions ON-THE-FLY                                 │
│  └── Returns: Question object                                       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Target Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         NOTION CMS                                   │
│  (Managed by Content Team - No Code Required)                        │
│  ├── Story Templates (50+ per concept)                              │
│  ├── Number Ranges per difficulty                                   │
│  ├── Distractor Rules                                               │
│  └── Solution Patterns                                              │
└───────────────────────────┬─────────────────────────────────────────┘
                            │ Background Sync (every 5 min)
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         REDIS CACHE                                  │
│  services/notion_sync.py                                             │
│  ├── notion:templates:{concept_key}:{difficulty} → List[Template]   │
│  ├── notion:distractors:{concept_key} → DistractorRules             │
│  └── notion:number_ranges:{concept_key}:{difficulty} → Range        │
└───────────────────────────┬─────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  NOTION QUESTION ENGINE (NEW)                        │
│  domain/content_generation/engines/notion_engine.py                 │
│  ├── Reads templates from Redis                                     │
│  ├── Applies variable substitution                                  │
│  ├── Generates infinite variations                                  │
│  └── Returns: Question object (SAME INTERFACE)                      │
└───────────────────────────┬─────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  ADAPTIVE QUESTION SELECTOR                          │
│  domain/adaptation/selector.py (MODIFIED)                           │
│  ├── ConceptGraph (UNCHANGED)                                       │
│  ├── MasteryTracker (UNCHANGED)                                     │
│  ├── Sequencer (UNCHANGED)                                          │
│  └── self.generator = NotionQuestionEngine()  ◄── NEW              │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Notion Database Schema

### Database 1: `Story Templates`

| Field | Type | Example |
|-------|------|---------|
| ID | Title | `factors_story_001` |
| Concept | Select | `factors`, `multiples`, `gcd`, `lcm`, `divisibility`, `prime_composite`, `factor_pairs`, `prime_factorization`, `word_problem` |
| Difficulty | Select | `1`, `2`, `3` |
| Bloom Level | Select | `REMEMBER`, `UNDERSTAND`, `APPLY`, `ANALYZE` |
| Question Template | Rich Text | `{name} has {total} {item}s. She wants to arrange them in equal rows. How many different ways can she arrange all the {item}s?` |
| Variables | Multi-select | `name`, `total`, `item` |
| Answer Expression | Text | `len(factors({total}))` |
| Hint Template | Rich Text | `Think about which numbers divide {total} evenly` |
| Solution Template | Rich Text | `To find the ways, we need all factors of {total}...` |
| Status | Select | `Draft`, `Review`, `Published` |
| Author | Person | Content team member |

### Database 2: `Number Ranges`

| Field | Type | Example |
|-------|------|---------|
| Concept | Select | `factors` |
| Difficulty | Select | `1` |
| Variable | Text | `total` |
| Min Value | Number | `12` |
| Max Value | Number | `36` |
| Constraints | Text | `has_multiple_factors` |

### Database 3: `Distractor Rules`

| Field | Type | Example |
|-------|------|---------|
| Concept | Select | `factors` |
| Rule Type | Select | `off_by_one`, `common_misconception`, `partial_answer` |
| Expression | Text | `answer + 1` |
| Why Wrong | Rich Text | `This includes 1 extra number that doesn't divide evenly` |
| Teaching Point | Rich Text | `Remember: a factor must divide the number with no remainder` |

### Database 4: `Name Pools`

| Field | Type | Example |
|-------|------|---------|
| Culture | Select | `Indian`, `International`, `Mixed` |
| Gender | Select | `Male`, `Female`, `Neutral` |
| Name | Text | `Priya`, `Arjun`, `Sam` |

### Database 5: `Object Pools`

| Field | Type | Example |
|-------|------|---------|
| Category | Select | `food`, `stationery`, `nature`, `toys` |
| Singular | Text | `mango` |
| Plural | Text | `mangoes` |
| Countable | Checkbox | `true` |

---

## Implementation Plan

### Phase 1: Create Notion Databases (Day 1-2)

**Manual Setup:**
1. Create Notion workspace: `Practice Arena Content`
2. Create 5 databases with schema above
3. Create Notion Integration and get API token
4. Store token in `.env`: `NOTION_API_TOKEN=secret_xxx`

### Phase 2: Build NotionSyncService (Day 3-4)

Create `backend/services/notion_sync.py`:

```python
"""
NotionSyncService: Syncs Notion CMS → Redis Cache

Runs every 5 minutes (background task) to pull latest templates.
Frontend reads from Redis (sub-millisecond) - never waits for Notion.
"""

from notion_client import Client
import redis
import json
from typing import List, Dict, Any
from config.settings import Settings
from config.logging_config import get_logger

logger = get_logger(__name__)


class NotionSyncService:
    """Syncs Notion databases to Redis cache."""
    
    # Database IDs (configured in settings)
    DATABASE_IDS = {
        "story_templates": None,  # Set from settings
        "number_ranges": None,
        "distractor_rules": None,
        "name_pools": None,
        "object_pools": None,
    }
    
    def __init__(self, settings: Settings):
        self.notion = Client(auth=settings.NOTION_API_TOKEN)
        self.redis = redis.from_url(settings.REDIS_URL)
        self.DATABASE_IDS = {
            "story_templates": settings.NOTION_DB_STORY_TEMPLATES,
            "number_ranges": settings.NOTION_DB_NUMBER_RANGES,
            "distractor_rules": settings.NOTION_DB_DISTRACTOR_RULES,
            "name_pools": settings.NOTION_DB_NAME_POOLS,
            "object_pools": settings.NOTION_DB_OBJECT_POOLS,
        }
    
    async def sync_all(self):
        """Full sync of all databases."""
        await self.sync_story_templates()
        await self.sync_number_ranges()
        await self.sync_distractor_rules()
        await self.sync_pools()
        logger.info("✅ Notion sync complete")
    
    async def sync_story_templates(self):
        """Sync story templates to Redis."""
        db_id = self.DATABASE_IDS["story_templates"]
        results = self._query_database(db_id, filter={"property": "Status", "select": {"equals": "Published"}})
        
        # Group by concept + difficulty
        templates_by_key = {}
        for page in results:
            props = page["properties"]
            concept = self._get_select(props, "Concept")
            difficulty = self._get_select(props, "Difficulty")
            
            template = {
                "id": page["id"],
                "question_template": self._get_rich_text(props, "Question Template"),
                "variables": self._get_multi_select(props, "Variables"),
                "answer_expression": self._get_text(props, "Answer Expression"),
                "hint_template": self._get_rich_text(props, "Hint Template"),
                "solution_template": self._get_rich_text(props, "Solution Template"),
                "bloom_level": self._get_select(props, "Bloom Level"),
            }
            
            key = f"notion:templates:{concept}:{difficulty}"
            if key not in templates_by_key:
                templates_by_key[key] = []
            templates_by_key[key].append(template)
        
        # Store in Redis
        for key, templates in templates_by_key.items():
            self.redis.set(key, json.dumps(templates), ex=3600)  # 1 hour TTL
            logger.debug(f"Synced {len(templates)} templates to {key}")
    
    async def sync_number_ranges(self):
        """Sync number ranges to Redis."""
        db_id = self.DATABASE_IDS["number_ranges"]
        results = self._query_database(db_id)
        
        for page in results:
            props = page["properties"]
            concept = self._get_select(props, "Concept")
            difficulty = self._get_select(props, "Difficulty")
            variable = self._get_text(props, "Variable")
            
            range_data = {
                "min": self._get_number(props, "Min Value"),
                "max": self._get_number(props, "Max Value"),
                "constraints": self._get_text(props, "Constraints"),
            }
            
            key = f"notion:ranges:{concept}:{difficulty}:{variable}"
            self.redis.set(key, json.dumps(range_data), ex=3600)
    
    async def sync_distractor_rules(self):
        """Sync distractor rules to Redis."""
        db_id = self.DATABASE_IDS["distractor_rules"]
        results = self._query_database(db_id)
        
        rules_by_concept = {}
        for page in results:
            props = page["properties"]
            concept = self._get_select(props, "Concept")
            
            rule = {
                "type": self._get_select(props, "Rule Type"),
                "expression": self._get_text(props, "Expression"),
                "why_wrong": self._get_rich_text(props, "Why Wrong"),
                "teaching_point": self._get_rich_text(props, "Teaching Point"),
            }
            
            if concept not in rules_by_concept:
                rules_by_concept[concept] = []
            rules_by_concept[concept].append(rule)
        
        for concept, rules in rules_by_concept.items():
            key = f"notion:distractors:{concept}"
            self.redis.set(key, json.dumps(rules), ex=3600)
    
    async def sync_pools(self):
        """Sync name and object pools to Redis."""
        # Names
        db_id = self.DATABASE_IDS["name_pools"]
        results = self._query_database(db_id)
        names = [self._get_text(p["properties"], "Name") for p in results]
        self.redis.set("notion:pools:names", json.dumps(names), ex=3600)
        
        # Objects
        db_id = self.DATABASE_IDS["object_pools"]
        results = self._query_database(db_id)
        objects = [
            {
                "singular": self._get_text(p["properties"], "Singular"),
                "plural": self._get_text(p["properties"], "Plural"),
            }
            for p in results
        ]
        self.redis.set("notion:pools:objects", json.dumps(objects), ex=3600)
    
    # ==================== HELPERS ====================
    
    def _query_database(self, database_id: str, filter: dict = None) -> List[dict]:
        """Query Notion database with pagination."""
        results = []
        cursor = None
        while True:
            response = self.notion.databases.query(
                database_id=database_id,
                filter=filter,
                start_cursor=cursor,
            )
            results.extend(response["results"])
            if not response["has_more"]:
                break
            cursor = response["next_cursor"]
        return results
    
    def _get_select(self, props: dict, name: str) -> str:
        return props.get(name, {}).get("select", {}).get("name", "")
    
    def _get_multi_select(self, props: dict, name: str) -> List[str]:
        return [opt["name"] for opt in props.get(name, {}).get("multi_select", [])]
    
    def _get_text(self, props: dict, name: str) -> str:
        title = props.get(name, {}).get("title", [])
        if title:
            return title[0].get("plain_text", "")
        rich = props.get(name, {}).get("rich_text", [])
        if rich:
            return rich[0].get("plain_text", "")
        return ""
    
    def _get_rich_text(self, props: dict, name: str) -> str:
        return "".join([t.get("plain_text", "") for t in props.get(name, {}).get("rich_text", [])])
    
    def _get_number(self, props: dict, name: str) -> int:
        return props.get(name, {}).get("number", 0)
```

### Phase 3: Build NotionQuestionEngine (Day 5-7)

Create `backend/domain/content_generation/engines/notion_engine.py`:

```python
"""
NotionQuestionEngine: Generates questions from Notion templates

This engine:
1. Reads pre-synced templates from Redis (fast!)
2. Picks a random template for concept + difficulty
3. Fills variables with random values from ranges
4. Evaluates answer expression
5. Generates distractors from rules
6. Returns Question object (same interface as FactorsMultiplesIntegrated)
"""

import random
import json
import math
from typing import List, Dict, Any, Optional
import redis
from sympy import factorint, divisors, gcd, lcm, isprime

from api.models.quiz import Question, ChapterEnum
from api.models.cognitive_levels import BloomLevel
from api.models.distractor import MisconceptionType, DistractorInfo
from config.settings import get_settings
from config.logging_config import get_logger

logger = get_logger(__name__)


class NotionQuestionEngine:
    """
    Drop-in replacement for FactorsMultiplesIntegrated.
    
    Implements the same interface:
        generate(concept_key: str, difficulty: int, bloom_level: BloomLevel) -> Question
    """
    
    chapter = ChapterEnum.FACTORS_MULTIPLES
    chapter_name = "Factors & Multiples"
    
    # Stable concept IDs (must match existing taxonomy)
    CONCEPT_IDS = {
        "factors": "math.class5.factors_multiples.factors",
        "multiples": "math.class5.factors_multiples.multiples",
        "gcd": "math.class5.factors_multiples.gcd",
        "lcm": "math.class5.factors_multiples.lcm",
        "divisibility": "math.class5.factors_multiples.divisibility",
        "prime_composite": "math.class5.factors_multiples.prime_composite",
        "factor_pairs": "math.class5.factors_multiples.factor_pairs",
        "prime_factorization": "math.class5.factors_multiples.prime_factorization",
        "word_problem": "math.class5.factors_multiples.word_problem",
    }
    
    # Expression evaluator context
    EVAL_CONTEXT = {
        "len": len,
        "sum": sum,
        "min": min,
        "max": max,
        "gcd": lambda a, b: int(gcd(a, b)),
        "lcm": lambda a, b: int(lcm(a, b)),
        "factors": lambda n: list(divisors(n)),
        "factor_count": lambda n: len(divisors(n)),
        "multiples": lambda n, count=10: [n * i for i in range(1, count + 1)],
        "is_prime": isprime,
        "prime_factors": lambda n: list(factorint(n).keys()),
        "factor_pairs": lambda n: [(i, n // i) for i in divisors(n) if i <= n // i],
    }
    
    def __init__(self):
        settings = get_settings()
        self.redis = redis.from_url(settings.REDIS_URL)
        self._names_cache = None
        self._objects_cache = None
    
    def generate(
        self, 
        concept_key: str = None, 
        difficulty: int = None, 
        bloom_level: BloomLevel = None
    ) -> Question:
        """
        Generate a question from Notion templates.
        
        Args:
            concept_key: Target concept (e.g., "factors", "gcd")
            difficulty: Target difficulty 1-3
            bloom_level: Target Bloom's level (optional)
        
        Returns:
            Question object compatible with existing adaptive layer
        """
        # Defaults
        if concept_key is None:
            concept_key = random.choice(list(self.CONCEPT_IDS.keys()))
        if difficulty is None:
            difficulty = random.randint(1, 3)
        
        # Fetch template from Redis
        template = self._get_random_template(concept_key, difficulty)
        
        if template is None:
            # Fallback: try any difficulty for this concept
            for d in [1, 2, 3]:
                template = self._get_random_template(concept_key, d)
                if template:
                    difficulty = d
                    break
        
        if template is None:
            raise ValueError(f"No template found for concept={concept_key}, difficulty={difficulty}")
        
        # Generate variable values
        variables = self._generate_variables(concept_key, difficulty, template["variables"])
        
        # Fill templates
        question_text = self._fill_template(template["question_template"], variables)
        hint_text = self._fill_template(template.get("hint_template", ""), variables)
        solution_text = self._fill_template(template.get("solution_template", ""), variables)
        
        # Evaluate answer
        correct_answer = self._evaluate_expression(template["answer_expression"], variables)
        
        # Generate distractors
        options, distractor_info = self._generate_options(
            concept_key, correct_answer, variables
        )
        correct_index = options.index(str(correct_answer))
        
        # Determine Bloom level
        if bloom_level is None:
            bloom_level = BloomLevel[template.get("bloom_level", "APPLY")]
        
        # Build Question object
        question = Question(
            question=question_text,
            options=options,
            correct_option=correct_index,
            explanation=solution_text,
            difficulty=difficulty,
            meta=self._build_meta(concept_key, difficulty, bloom_level),
            hint=hint_text,
            misconception_info=distractor_info,
        )
        
        logger.debug(f"Generated question: concept={concept_key}, difficulty={difficulty}")
        return question
    
    def _get_random_template(self, concept_key: str, difficulty: int) -> Optional[Dict]:
        """Fetch random template from Redis."""
        key = f"notion:templates:{concept_key}:{difficulty}"
        data = self.redis.get(key)
        if data:
            templates = json.loads(data)
            return random.choice(templates) if templates else None
        return None
    
    def _generate_variables(
        self, concept_key: str, difficulty: int, variable_names: List[str]
    ) -> Dict[str, Any]:
        """Generate variable values from number ranges."""
        variables = {}
        
        for var_name in variable_names:
            if var_name == "name":
                variables["name"] = self._get_random_name()
            elif var_name == "item":
                obj = self._get_random_object()
                variables["item"] = obj["singular"]
                variables["items"] = obj["plural"]
            else:
                # Numeric variable - get range from Redis
                key = f"notion:ranges:{concept_key}:{difficulty}:{var_name}"
                data = self.redis.get(key)
                if data:
                    range_info = json.loads(data)
                    value = self._generate_number_with_constraints(
                        range_info["min"],
                        range_info["max"],
                        range_info.get("constraints", "")
                    )
                    variables[var_name] = value
                else:
                    # Default fallback range based on difficulty
                    variables[var_name] = random.randint(10 * difficulty, 50 * difficulty)
        
        return variables
    
    def _generate_number_with_constraints(
        self, min_val: int, max_val: int, constraints: str
    ) -> int:
        """Generate number satisfying constraints."""
        for _ in range(100):  # Max attempts
            n = random.randint(min_val, max_val)
            
            if not constraints:
                return n
            
            # Check constraints
            if "has_multiple_factors" in constraints and len(divisors(n)) < 4:
                continue
            if "is_prime" in constraints and not isprime(n):
                continue
            if "is_composite" in constraints and isprime(n):
                continue
            if "is_even" in constraints and n % 2 != 0:
                continue
            if "is_odd" in constraints and n % 2 == 0:
                continue
            
            return n
        
        return random.randint(min_val, max_val)  # Give up, return any
    
    def _fill_template(self, template: str, variables: Dict[str, Any]) -> str:
        """Fill template with variable values."""
        result = template
        for key, value in variables.items():
            result = result.replace(f"{{{key}}}", str(value))
        return result
    
    def _evaluate_expression(self, expression: str, variables: Dict[str, Any]) -> Any:
        """Safely evaluate answer expression."""
        try:
            context = {**self.EVAL_CONTEXT, **variables}
            return eval(expression, {"__builtins__": {}}, context)
        except Exception as e:
            logger.error(f"Expression eval failed: {expression}, error: {e}")
            return 0
    
    def _generate_options(
        self, concept_key: str, correct_answer: Any, variables: Dict[str, Any]
    ) -> tuple[List[str], List[Dict]]:
        """Generate options with distractors."""
        options = [str(correct_answer)]
        distractor_info = [{
            "option_index": 0,
            "value": str(correct_answer),
            "misconception_type": "CORRECT",
            "why_wrong": None,
            "teaching_point": None,
            "is_correct": True,
        }]
        
        # Get distractor rules from Redis
        key = f"notion:distractors:{concept_key}"
        data = self.redis.get(key)
        rules = json.loads(data) if data else []
        
        # Generate 3 distractors
        used_values = {str(correct_answer)}
        
        for rule in rules[:3]:  # Use up to 3 rules
            try:
                # Evaluate distractor expression
                context = {
                    **self.EVAL_CONTEXT,
                    **variables,
                    "answer": correct_answer,
                }
                distractor_value = eval(rule["expression"], {"__builtins__": {}}, context)
                distractor_str = str(distractor_value)
                
                if distractor_str not in used_values and distractor_value > 0:
                    used_values.add(distractor_str)
                    options.append(distractor_str)
                    distractor_info.append({
                        "option_index": len(options) - 1,
                        "value": distractor_str,
                        "misconception_type": rule["type"],
                        "why_wrong": rule["why_wrong"],
                        "teaching_point": rule["teaching_point"],
                        "is_correct": False,
                    })
            except Exception as e:
                logger.warning(f"Distractor eval failed: {rule}, error: {e}")
        
        # Fill remaining with random if needed
        while len(options) < 4:
            if isinstance(correct_answer, int):
                fake = correct_answer + random.choice([-2, -1, 1, 2, 3])
                if fake > 0 and str(fake) not in used_values:
                    used_values.add(str(fake))
                    options.append(str(fake))
                    distractor_info.append({
                        "option_index": len(options) - 1,
                        "value": str(fake),
                        "misconception_type": "random",
                        "why_wrong": "This is not the correct answer",
                        "teaching_point": "Check your calculation",
                        "is_correct": False,
                    })
        
        # Shuffle options (keeping track of correct index)
        combined = list(zip(options, distractor_info))
        random.shuffle(combined)
        options, distractor_info = zip(*combined)
        options = list(options)
        distractor_info = list(distractor_info)
        
        # Update indices after shuffle
        for i, info in enumerate(distractor_info):
            info["option_index"] = i
        
        return options, distractor_info
    
    def _get_random_name(self) -> str:
        """Get random name from pool."""
        if self._names_cache is None:
            data = self.redis.get("notion:pools:names")
            self._names_cache = json.loads(data) if data else ["Priya", "Arjun", "Sam", "Maya"]
        return random.choice(self._names_cache)
    
    def _get_random_object(self) -> Dict[str, str]:
        """Get random object from pool."""
        if self._objects_cache is None:
            data = self.redis.get("notion:pools:objects")
            self._objects_cache = json.loads(data) if data else [
                {"singular": "mango", "plural": "mangoes"},
                {"singular": "book", "plural": "books"},
            ]
        return random.choice(self._objects_cache)
    
    def _build_meta(
        self, concept_key: str, difficulty: int, bloom_level: BloomLevel
    ) -> Dict[str, Any]:
        """Build meta dict for Question contract compliance."""
        return {
            "subject": "math",
            "grade": 5,
            "chapter": "factors_multiples",
            "chapter_id": "factors_multiples",
            "concept_id": self.CONCEPT_IDS.get(
                concept_key, f"math.class5.factors_multiples.{concept_key}"
            ),
            "concept_key": concept_key,
            "difficulty": difficulty,
            "bloom_level": bloom_level.value if hasattr(bloom_level, "value") else str(bloom_level),
            "source": "notion_cms",  # Track that this came from Notion
        }
```

### Phase 4: Modify AdaptiveQuestionSelector (Day 8)

Update `backend/domain/adaptation/selector.py`:

```python
# At the top, add new import:
from domain.content_generation.engines.notion_engine import NotionQuestionEngine

# Change GENERATORS mapping:
class AdaptiveQuestionSelector:
    # Map chapter keys to generator classes
    GENERATORS = {
        "factors_multiples": NotionQuestionEngine,  # ◄── CHANGED from FactorsMultiplesGenerator
    }
    
    # ... rest unchanged ...
```

**That's it!** The selector calls `self.generator.generate(concept_key=..., difficulty=...)` which is the same interface for both engines.

### Phase 5: Add Background Sync Task (Day 9)

Update `backend/core/lifecycle.py`:

```python
from services.notion_sync import NotionSyncService
import asyncio

async def startup():
    # ... existing startup code ...
    
    # Start Notion sync background task
    notion_sync = NotionSyncService(get_settings())
    asyncio.create_task(notion_sync_loop(notion_sync))

async def notion_sync_loop(sync_service: NotionSyncService):
    """Background loop to sync Notion → Redis every 5 minutes."""
    while True:
        try:
            await sync_service.sync_all()
        except Exception as e:
            logger.error(f"Notion sync failed: {e}")
        await asyncio.sleep(300)  # 5 minutes
```

### Phase 6: Bootstrap Content in Notion (Day 10-14)

Use LLM to generate initial templates:

**LLM Prompt for Template Generation:**
```
Generate 10 story templates for the "factors" concept in a Class 5 math course.

Requirements:
1. Use Indian names and contexts (markets, festivals, schools)
2. Variables: {name}, {total}, {item}, {items}
3. Difficulty 1: numbers 12-36
4. Make engaging K.C. Nag style word problems

Format for each:
- Question Template: ...
- Answer Expression: factor_count({total})
- Hint Template: ...
- Solution Template: ...
```

**Expected Output (50+ templates per concept):**
- factors: 50 templates × 3 difficulties = 150
- multiples: 50 templates × 3 difficulties = 150
- gcd: 30 templates × 3 difficulties = 90
- lcm: 30 templates × 3 difficulties = 90
- etc.

---

## Integration Verification Checklist

- [ ] AdaptiveQuestionSelector still works with Sequencer
- [ ] MasteryTracker updates work correctly
- [ ] ConceptGraph relationships still honored
- [ ] Question object format unchanged
- [ ] Frontend receives same response structure
- [ ] Misconception info populated correctly
- [ ] Meta contains all required fields

---

## Rollback Plan

If issues arise, simply change the GENERATORS mapping back:

```python
GENERATORS = {
    "factors_multiples": FactorsMultiplesGenerator,  # Rollback to original
}
```

Both engines implement the same interface, so rollback is instant.

---

## Cost Analysis

| Component | One-Time Cost | Monthly Cost |
|-----------|---------------|--------------|
| LLM Template Generation (1000 templates) | ₹10,000 | ₹0 |
| Notion Pro (content team) | ₹0 | $10 ≈ ₹830 |
| Redis (AWS ElastiCache) | ₹0 | $15 ≈ ₹1,250 |
| **Total** | **₹10,000** | **₹2,080** |

**Savings vs. On-the-fly LLM:**
- On-the-fly: ₹0.50/question × 100,000 questions/month = ₹50,000/month
- Notion CMS: ₹2,080/month
- **Savings: ₹47,920/month (96% reduction)**

---

## File Changes Summary

| File | Action | Description |
|------|--------|-------------|
| `backend/services/notion_sync.py` | CREATE | Notion → Redis sync service |
| `backend/domain/content_generation/engines/notion_engine.py` | CREATE | New question engine |
| `backend/domain/adaptation/selector.py` | MODIFY | Change GENERATORS mapping |
| `backend/core/lifecycle.py` | MODIFY | Add background sync task |
| `backend/config/settings.py` | MODIFY | Add Notion config |
| `backend/requirements.txt` | MODIFY | Add `notion-client` package |

---

## Next Steps

1. **Review this plan** - Any adjustments needed?
2. **Set up Notion workspace** - Create databases with schema
3. **Implement Phase 2-5** - I can create all the files
4. **Bootstrap content** - Use LLM to generate initial templates
5. **Test integration** - Verify adaptive layer works correctly
