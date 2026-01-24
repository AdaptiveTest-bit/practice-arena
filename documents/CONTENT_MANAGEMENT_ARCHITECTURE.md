# Content Management Architecture for CBSE K-12 EdTech Platform

**Date:** 17 January 2026  
**Repository:** `practice-arena` (branch: `feature/ChaptersIntegration`)  
**Version:** 2.2 - Infrastructure Audit & Admin Panel Roadmap

---

## 0. Implementation Status Dashboard

> **This section maps architecture concepts to existing code. Use this to avoid duplication.**

### ✅ ALREADY BUILT (Do Not Rebuild)

| Architecture Component | Implementation | Location |
|----------------------|----------------|----------|
| **Concept Graph (DAG)** | `ConceptGraph` class | `domain/adaptation/concept_graph.py` |
| **Mastery Tracking** | `MasteryTracker`, Leitner boxes | `domain/adaptation/mastery.py` |
| **Adaptive Sequencer** | 4 strategies (MASTERY_FIRST, etc.) | `domain/adaptation/sequencer.py` |
| **Template Engine** | `LeanTemplateEngine`, `VariableGenerator` | `domain/template_engine/lean_template_engine.py` |
| **Admin Service** | `AdminTemplateService` (CRUD, workflow) | `domain/admin/template_service.py` |
| **Content Validation** | `TaxonomyValidator`, `RubricValidator` | `domain/content_validation/` |
| **DB: Templates** | `QuestionTemplate` (DRAFT→PUBLISHED) | `db/models/templates.py` |
| **DB: Concepts** | `ConceptCatalog`, `StudentConceptState` | `db/models/concepts.py` |
| **DB: Breakpoints** | `StudentBreakpoint` (wrong_streak) | `db/models/concepts.py` |
| **Taxonomy Config** | Math Class 5 (12 concepts) | `config/content/taxonomy/math.yaml` |
| **Graph Config** | Factors & Multiples DAG | `config/content/graphs/math/class5/factors_multiples.yaml` |
| **CLI: Coverage QA** | `coverage_qa_cli.py` | `tools/coverage_qa_cli.py` |
| **CLI: LLM Gen** | `llm_template_generator.py` | `tools/llm_template_generator.py` |
| **CLI: Migration** | `template_migrator.py` | `tools/template_migrator.py` |
| **Admin API: Graphs** | `graphs_router` (GET/PUT graph, validate) | `api/admin/graphs.py` |
| **Admin API: Coverage** | `coverage_router` (coverage report) | `api/admin/graphs.py` |
| **Admin API: Taxonomy** | `taxonomy_router` (concepts CRUD) | `api/admin/graphs.py` |
| **Admin UI: Graph Builder** | React Flow visual editor | `admin-ui/src/pages/GraphBuilder.tsx` |
| **Admin UI: ConceptNode** | Custom node component | `admin-ui/src/components/graph/ConceptNode.tsx` |
| **Admin UI: NodeInspector** | Side panel editor | `admin-ui/src/components/graph/NodeInspector.tsx` |

### 🔶 PARTIALLY BUILT (Extend, Don't Replace)

| Component | What Exists | What's Missing |
|-----------|-------------|----------------|
| **API Routes** | Quiz, Student, Health, **Admin Graph/Coverage/Taxonomy** | Template CRUD routes |
| **Concept Metadata** | Tracking in `StudentConceptState` | Nightly aggregation job for global stats |
| **Blueprints** | Directory exists | Coverage target YAML files |
| **Rubrics** | Directory exists | Quality rule YAML files |
| **Admin Panel UI** | Graph Builder (React Flow), Navigation | Template Builder, Simulator |

### ⬜ NOT YET BUILT (New Development Required)

| Component | Priority | Description |
|-----------|----------|-------------|
| **Template Builder UI** | Phase D | No-code template editor with live preview |
| **Path Simulator UI** | Phase E | Student journey simulation |
| **Dynamic Metadata Job** | Phase G | Nightly computation from attempts |

---

## 1. Executive Summary

This document defines the **content management architecture** for a production-grade CBSE K-12 EdTech platform operating at ₹200-300/month price point. The architecture is inspired by:
- **Khan Academy's** mastery-based progression
- **Duolingo's** adaptive skill trees
- **Testbook's** dynamic question metadata
- **Notion/Figma's** no-code content management philosophy

### Key Differentiators

| Feature | Traditional EdTech | Our Architecture |
|---------|-------------------|------------------|
| Content | Static question bank | **Generative templates** (infinite variations) |
| Difficulty | Pre-assigned by author | **Calculated from student performance** |
| Navigation | Linear chapter sequence | **DAG-based concept graph** with prerequisites |
| Remediation | Show solution video | **Auto-regress to prerequisite concept** |
| Metadata | Basic (topic, difficulty) | **Dynamic** (accuracy_rate, avg_time, skip_rate) |
| **Admin UX** | SQL queries / YAML files | **Visual drag-drop graph builder** |
| **Content Team** | Needs developer support | **Self-service (no code required)** |

---

## 2. The Content Hierarchy

```
CBSE Curriculum
└── Subject (Math, Science, English)
    └── Grade/Class (1-12)
        └── Chapter (NCERT textbook chapter)
            └── Topic (section within chapter)
                └── Concept Node (atomic micro-skill)
                    └── Generator (Python code/template producing questions)
                        └── Question Instance (runtime-generated)
```

### Concept ID Naming Convention

```
{subject}.class{grade}.{chapter_key}.{concept_slug}

Examples:
- math.class5.factors_multiples.divisibility
- math.class5.factors_multiples.prime_factorization
- math.class5.factors_multiples.gcd
```

---

## 3. The Knowledge Graph Architecture

### 3.1 Core Philosophy: DAG-Based Navigation

Instead of a flat list of chapters, we build a **Directed Acyclic Graph (DAG)** of concepts where:
- **Node** = A micro-concept (atomic learning unit)
- **Edge** = A dependency (prerequisite relationship)

This enables a student to start at "Basic Divisibility" and automatically navigate to "GCD Word Problems" without human guidance.

### 3.2 Database Schema (PostgreSQL)

> **⚠️ IMPLEMENTATION NOTE:** Most of these tables already exist in `db/models/`. Reference the actual SQLAlchemy models, not these SQL snippets.

#### Existing Models (in `db/models/`)

| Table | Model Class | File | Status |
|-------|-------------|------|--------|
| `concept_catalog` | `ConceptCatalog` | `concepts.py` | ✅ Built |
| `student_concept_state` | `StudentConceptState` | `concepts.py` | ✅ Built (Leitner boxes) |
| `student_breakpoints` | `StudentBreakpoint` | `concepts.py` | ✅ Built |
| `question_templates` | `QuestionTemplate` | `templates.py` | ✅ Built (full workflow) |
| `misconceptions` | `Misconception` | `templates.py` | ✅ Built |
| `learning_sessions` | `LearningSession` | `session.py` | ✅ Built |
| `learning_events` | `LearningEvent` | `events.py` | ✅ Built |

#### Table 1: `concept_nodes` (The Knowledge Map) — 🔶 PARTIAL

> **Exists as:** `ConceptCatalog` in `db/models/concepts.py`
> **Missing:** `difficulty_tier`, `bloom_levels[]`, `estimated_time_minutes`, `required_mastery_score`

```sql
CREATE TABLE concept_nodes (
    id SERIAL PRIMARY KEY,
    concept_id VARCHAR(100) UNIQUE NOT NULL,  -- 'math.class5.factors_multiples.gcd'
    
    -- Hierarchy
    subject VARCHAR(50) NOT NULL,             -- 'math'
    grade INT NOT NULL,                        -- 5
    chapter_key VARCHAR(100) NOT NULL,         -- 'factors_multiples'
    
    -- Display
    name VARCHAR(255) NOT NULL,                -- 'Find GCD of two numbers'
    description TEXT,
    sequence_order INT DEFAULT 0,              -- Display order within chapter
    
    -- Learning Parameters
    difficulty_tier INT DEFAULT 1,             -- 1=Easy, 2=Medium, 3=Hard (default)
    bloom_levels VARCHAR(50)[] DEFAULT ARRAY['REMEMBER'],
    estimated_time_minutes INT DEFAULT 10,
    
    -- Mastery Thresholds
    required_mastery_score DECIMAL(3,2) DEFAULT 0.80,  -- 80% to unlock next
    min_attempts_for_mastery INT DEFAULT 3,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_concept_chapter ON concept_nodes(subject, grade, chapter_key);
CREATE INDEX idx_concept_id ON concept_nodes(concept_id);
```

#### Table 2: `concept_edges` (The Dependency Rules) — ⬜ NOT IN DB

> **Currently:** Stored in YAML files at `config/content/graphs/`
> **Loaded by:** `ConceptGraph.load()` in `domain/adaptation/concept_graph.py`
> **Decision:** Keep in YAML for now (easier content team editing) or migrate to DB for Admin Panel

```sql
CREATE TABLE concept_edges (
    id SERIAL PRIMARY KEY,
    parent_concept_id VARCHAR(100) NOT NULL,   -- Prerequisite concept
    child_concept_id VARCHAR(100) NOT NULL,    -- Dependent concept
    
    -- Edge Type
    relationship_type VARCHAR(20) DEFAULT 'STRICT',
    -- STRICT: Must master parent before attempting child
    -- RECOMMENDED: Suggested but not enforced
    
    reason TEXT,  -- "Understanding factors is needed before GCD"
    
    FOREIGN KEY (parent_concept_id) REFERENCES concept_nodes(concept_id),
    FOREIGN KEY (child_concept_id) REFERENCES concept_nodes(concept_id),
    UNIQUE(parent_concept_id, child_concept_id),
    CHECK (parent_concept_id != child_concept_id)  -- No self-loops
);

CREATE INDEX idx_edge_parent ON concept_edges(parent_concept_id);
CREATE INDEX idx_edge_child ON concept_edges(child_concept_id);
```

#### Table 3: `student_concept_mastery` (The Save State) — ✅ BUILT

> **Exists as:** `StudentConceptState` in `db/models/concepts.py`
> **Features:** `leitner_box` (1-5), `due_at`, `attempts`, `correct`, `last_bloom_served`

```sql
CREATE TABLE student_concept_mastery (
    id SERIAL PRIMARY KEY,
    student_id VARCHAR(50) NOT NULL,
    concept_id VARCHAR(100) NOT NULL,
    
    -- Mastery Metrics
    current_mastery_score DECIMAL(3,2) DEFAULT 0.00,
    attempts INT DEFAULT 0,
    correct INT DEFAULT 0,
    accuracy DECIMAL(3,2) GENERATED ALWAYS AS (
        CASE WHEN attempts > 0 THEN correct::DECIMAL / attempts ELSE 0 END
    ) STORED,
    
    -- Leitner Spaced Repetition
    leitner_box INT DEFAULT 1,
    due_at TIMESTAMP DEFAULT NOW(),
    
    -- Status
    status VARCHAR(20) DEFAULT 'LOCKED',  -- 'LOCKED', 'ACTIVE', 'MASTERED'
    
    -- Performance
    avg_time_seconds INT,
    last_attempt_at TIMESTAMP,
    wrong_streak INT DEFAULT 0,  -- For remediation trigger
    
    UNIQUE(student_id, concept_id),
    FOREIGN KEY (concept_id) REFERENCES concept_nodes(concept_id)
);

CREATE INDEX idx_mastery_student ON student_concept_mastery(student_id);
CREATE INDEX idx_mastery_status ON student_concept_mastery(student_id, status);
```

#### Table 4: `concept_metadata` (Dynamic Stats - Testbook Style) — ⬜ NOT BUILT

> **Status:** Not yet implemented
> **Dependency:** Requires nightly job to compute from `learning_events`

```sql
-- Updated nightly from actual student performance
CREATE TABLE concept_metadata (
    concept_id VARCHAR(100) PRIMARY KEY,
    
    -- Calculated Difficulty (not pre-assigned!)
    calculated_difficulty DECIMAL(3,2),  -- 0.0 (easy) to 1.0 (hard)
    accuracy_rate DECIMAL(3,2),          -- Global accuracy
    
    -- Time Metrics (like Testbook's TTA)
    avg_time_to_solve_seconds INT,
    p50_time_seconds INT,
    p90_time_seconds INT,
    
    -- Engagement
    skip_rate DECIMAL(3,2),
    hint_request_rate DECIMAL(3,2),
    
    -- Volume
    total_attempts INT DEFAULT 0,
    total_students INT DEFAULT 0,
    
    -- Misconceptions
    most_common_misconception VARCHAR(100),
    misconception_frequency DECIMAL(3,2),
    
    computed_at TIMESTAMP DEFAULT NOW(),
    
    FOREIGN KEY (concept_id) REFERENCES concept_nodes(concept_id)
);
```

#### Table 5: `generator_mapping` (Template → Concept Link) — ✅ BUILT DIFFERENTLY

> **Exists as:** `QuestionTemplate.concept_id` in `db/models/templates.py`
> **Implementation:** Direct FK on template, not separate mapping table (simpler)

```sql
CREATE TABLE generator_mapping (
    id SERIAL PRIMARY KEY,
    concept_id VARCHAR(100) NOT NULL,
    
    generator_type VARCHAR(20) DEFAULT 'TEMPLATE',  -- 'TEMPLATE' or 'PYTHON'
    generator_ref VARCHAR(255) NOT NULL,
    -- TEMPLATE: template_code (e.g., 'gcd_basic_01')
    -- PYTHON: function path (e.g., 'generators.math.gcd.gen_gcd_basic')
    
    difficulty_tier INT DEFAULT 1,
    bloom_level VARCHAR(20) DEFAULT 'REMEMBER',
    weight INT DEFAULT 100,  -- Selection priority
    is_active BOOLEAN DEFAULT TRUE,
    
    FOREIGN KEY (concept_id) REFERENCES concept_nodes(concept_id)
);

CREATE INDEX idx_generator_concept ON generator_mapping(concept_id, is_active);
```

---

## 4. The Navigation Algorithm ("Concept Navigator Engine")

> **✅ ALREADY IMPLEMENTED** in `domain/adaptation/`
> - `concept_graph.py` — DAG loading and traversal
> - `sequencer.py` — 4 strategies: MASTERY_FIRST, EXPLORATION, STRUGGLING_FOCUS, SPACED_REVIEW
> - `mastery.py` — MasteryLevel enum, decay, Leitner integration

### 4.1 The Frontier Algorithm (Core Logic) — ✅ BUILT

When a student starts practicing, the system finds the "frontier" - concepts they can work on:

> **Reference Implementation:** See `Sequencer.get_next_target()` in `domain/adaptation/sequencer.py`

```python
class ConceptNavigator:
    """DAG-based concept navigation - Khan Academy/Duolingo style."""
    
    def get_learning_frontier(self, student_id: str, chapter_key: str) -> list:
        """
        Frontier = nodes where:
        1. All STRICT prerequisites are MASTERED
        2. Status is NOT 'MASTERED' yet
        3. Ordered by difficulty_tier (Zone of Proximal Development)
        """
        chapter_concepts = self.get_chapter_concepts(chapter_key)
        mastery_map = self.get_student_mastery(student_id, chapter_key)
        graph = self.build_dependency_graph(chapter_concepts)
        
        frontier = []
        for concept in chapter_concepts:
            if mastery_map.get(concept.id, {}).get('status') == 'MASTERED':
                continue  # Already mastered
            
            prerequisites = graph.get_prerequisites(concept.id)
            all_prereqs_done = all(
                mastery_map.get(p, {}).get('status') == 'MASTERED'
                for p in prerequisites
                if graph.get_edge_type(p, concept.id) == 'STRICT'
            )
            
            if all_prereqs_done:
                frontier.append(concept)
        
        frontier.sort(key=lambda c: (c.difficulty_tier, c.sequence_order))
        return frontier
    
    def get_next_concept(self, student_id: str, chapter_key: str):
        """Pick the single best concept to practice next."""
        frontier = self.get_learning_frontier(student_id, chapter_key)
        if not frontier:
            return None  # Chapter complete!
        
        mastery_map = self.get_student_mastery(student_id, chapter_key)
        
        # Check for struggling student (needs backtrack)
        for concept in frontier:
            mastery = mastery_map.get(concept.concept_id, {})
            if mastery.get('wrong_streak', 0) >= 3:
                return self._check_for_backtrack(student_id, concept)
        
        # Check spaced repetition
        for concept in frontier:
            mastery = mastery_map.get(concept.concept_id, {})
            if mastery.get('due_at') and mastery['due_at'] <= datetime.utcnow():
                return concept
        
        return frontier[0]  # Default: easiest available
    
    def _check_for_backtrack(self, student_id, struggling_concept):
        """If failing repeatedly, check if prerequisite needs review."""
        for prereq_id in self.graph.get_prerequisites(struggling_concept.concept_id):
            if self.get_recent_accuracy(student_id, prereq_id, last_n=5) < 0.70:
                self.set_concept_status(student_id, prereq_id, 'ACTIVE')
                return self.get_concept(prereq_id)  # Backtrack!
        return struggling_concept
```

### 4.2 Status State Machine

```
┌────────┐  prerequisites  ┌────────┐  mastery   ┌──────────┐
│ LOCKED │ ───────────────▶│ ACTIVE │ ─────────▶ │ MASTERED │
└────────┘   mastered      └────────┘  achieved  └──────────┘
                                │                      │
                                │ wrong_streak ≥ 3     │
                                │ + prereq weak        │
                                ▼                      │
                          ┌───────────┐                │
                          │REMEDIATION│ ◀──────────────┘
                          └───────────┘   decay/review
```

### 4.3 When Student Selects a Chapter

```
Student Action: Select "Chapter 9: Factors & Multiples" for practice
                            ↓
System Flow:
┌─────────────────────────────────────────────────────────────────────┐
│ 1. Load Chapter Graph                                               │
│    → Load graphs/math/class5/factors_multiples.yaml                 │
│    → Build concept dependency graph                                 │
│                                                                     │
│ 2. Load Student's Concept Mastery State                             │
│    → Query StudentConceptState for all chapter concepts             │
│    → Identify: mastered, learning, not_started                      │
│                                                                     │
│ 3. Determine Starting Point                                         │
│    → If new student: Start from foundation (divisibility)           │
│    → If returning: Resume from lowest unmastered concept            │
│    → Honor prerequisites: Don't serve GCD before factors mastered   │
│                                                                     │
│ 4. Generate Adaptive Learning Path                                  │
│    → Topological sort of concepts by prerequisites                  │
│    → Adjust based on student's current mastery                      │
│    → Result: Ordered list of concepts to practice                   │
└─────────────────────────────────────────────────────────────────────┘
```

### 4.2 During Practice Session

```
┌─────────────────────────────────────────────────────────────────────┐
│ For Each Question:                                                  │
│                                                                     │
│ 1. Select Next Concept (Adaptive Selector)                          │
│    → Check mastery state of current concept                         │
│    → If mastered: Move to next in path                              │
│    → If struggling: Stay or go to prerequisite                      │
│                                                                     │
│ 2. Select Question for Concept                                      │
│    → Query templates: (concept_id, status=published)                │
│    → Filter by appropriate difficulty (based on student level)      │
│    → Pick template not recently served                              │
│                                                                     │
│ 3. Generate Question Instance                                       │
│    → LeanTemplateEngine.generate(template, variables)               │
│    → Return lean payload (no correct answer)                        │
│                                                                     │
│ 4. Student Answers                                                  │
│    → Evaluate correctness server-side                               │
│    → Update StudentConceptState (Leitner box, mastery)              │
│    → If wrong: Return misconception feedback                        │
│                                                                     │
│ 5. Adaptive Decision                                                │
│    → Update mastery tracker                                         │
│    → Decide: same concept, next concept, or remedial?               │
└─────────────────────────────────────────────────────────────────────┘
```

### 4.3 Mastery & Progression

**Concept Mastery Criteria:**
```python
def is_concept_mastered(state: StudentConceptState) -> bool:
    """A concept is mastered when:
    - At least 3 questions attempted
    - Accuracy >= 80%
    - Leitner box >= 3
    """
    return (
        state.attempts >= 3 and
        state.correct / state.attempts >= 0.80 and
        state.leitner_box >= 3
    )
```

**Progression Rules:**
1. Cannot attempt higher Bloom level until lower is mastered
2. Cannot attempt dependent concept until prerequisites are mastered
3. If accuracy drops, system may revert to remedial path

---

## 5. Admin Panel: Visual Content Management Tool

> **Core Philosophy:** Content writers and curriculum designers should be able to manage concepts, templates, and learning paths **without writing code, SQL, or YAML**. Everything happens through a visual interface.

### 5.1 The Admin Dashboard Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  📚 EdTech Admin Panel                                    [Content Writer ▼]│
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  📊 Dashboard│  │ 🗺️ Graph    │  │ 📝 Templates│  │ 🧪 Simulator│        │
│  │             │  │   Builder   │  │             │  │             │        │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
│                                                                             │
│  Quick Stats:                                                               │
│  ┌─────────────────┬─────────────────┬─────────────────┬──────────────────┐│
│  │ Total Concepts  │ Active Templates│ Pending Review  │ Coverage Gaps    ││
│  │     127         │      534        │      12         │      3           ││
│  └─────────────────┴─────────────────┴─────────────────┴──────────────────┘│
│                                                                             │
│  Recent Activity:                                                           │
│  • Priya added 5 templates to "HCF Word Problems" (2 hours ago)            │
│  • Rahul approved 3 templates for "LCM Basics" (yesterday)                 │
│  • System flagged "Divisibility" - low accuracy (34%) needs review         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Visual Graph Builder (React Flow Based)

Instead of editing YAML files, content writers use a **drag-and-drop canvas**:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  🗺️ Concept Graph Builder          Math > Class 5 > Factors & Multiples    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Toolbar: [+ Add Node] [🔗 Link Nodes] [💾 Save] [🧪 Validate] [📤 Publish]│
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                                                                         ││
│  │    ┌──────────────┐                                                     ││
│  │    │ Divisibility │ ──────┐                                             ││
│  │    │ ✅ 12 templates│      │                                             ││
│  │    │ 🟢 Published  │      │                                             ││
│  │    └──────────────┘      │                                             ││
│  │           │              ▼                                             ││
│  │           │     ┌──────────────┐      ┌──────────────┐                  ││
│  │           └────▶│   Factors    │─────▶│     GCD      │                  ││
│  │                 │ ✅ 8 templates│      │ ⚠️ 3 templates│                  ││
│  │                 │ 🟢 Published  │      │ 🟡 Draft     │                  ││
│  │                 └──────────────┘      └──────────────┘                  ││
│  │                        │                     │                          ││
│  │                        ▼                     ▼                          ││
│  │                 ┌──────────────┐      ┌──────────────┐                  ││
│  │                 │  Multiples   │─────▶│     LCM      │                  ││
│  │                 │ ✅ 10 templates│     │ ❌ 0 templates│                  ││
│  │                 │ 🟢 Published  │      │ 🔴 No Content│                  ││
│  │                 └──────────────┘      └──────────────┘                  ││
│  │                                                                         ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                             │
│  Node Inspector (Click a node):                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │ Concept: GCD (Greatest Common Divisor)                                  ││
│  │ ID: math.class5.factors_multiples.gcd                                   ││
│  │                                                                         ││
│  │ Prerequisites: [Factors ✓] [Divisibility ✓]                            ││
│  │ Difficulty Tier: [1] [2●] [3]                                           ││
│  │ Bloom Levels: [☑ REMEMBER] [☑ UNDERSTAND] [☐ APPLY]                    ││
│  │                                                                         ││
│  │ Linked Generators:                                                      ││
│  │ ┌─────────────────────────────────────────────┐                         ││
│  │ │ gen_gcd_basic_v1      │ Tier 1 │ [Edit] [×] │                         ││
│  │ │ gen_gcd_word_problem  │ Tier 2 │ [Edit] [×] │                         ││
│  │ │ [+ Link Generator]                          │                         ││
│  │ └─────────────────────────────────────────────┘                         ││
│  │                                                                         ││
│  │ [💾 Save Node] [🗑️ Delete Node]                                         ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Key Features:**
- **Drag nodes** to reposition
- **Draw edges** by clicking and dragging between nodes
- **Color coding**: 🟢 Published, 🟡 Draft, 🔴 Missing Content
- **Inline stats**: Template count, accuracy rate on each node
- **Click to inspect**: Edit properties in side panel

### 5.3 Template Builder (No-Code Interface)

Content writers create question templates visually:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  📝 Template Builder                              [Save Draft] [Submit] ▼   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Concept: [math.class5.factors_multiples.gcd        ▼]                     │
│  Difficulty: [○ Easy  ● Medium  ○ Hard]                                    │
│  Bloom Level: [UNDERSTAND ▼]                                               │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │ Question Text:                                                          ││
│  │ ┌─────────────────────────────────────────────────────────────────────┐ ││
│  │ │ Find the GCD of {a} and {b}.                                        │ ││
│  │ │                                                                     │ ││
│  │ │ [Insert Variable ▼]  [Insert Formula ▼]  [Insert Image 📷]          │ ││
│  │ └─────────────────────────────────────────────────────────────────────┘ ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │ Variables:                                                              ││
│  │ ┌────────┬──────────┬─────┬─────┬──────────────────────────────────────┐││
│  │ │ Name   │ Type     │ Min │ Max │ Constraints                          │││
│  │ ├────────┼──────────┼─────┼─────┼──────────────────────────────────────┤││
│  │ │ a      │ Integer  │ 10  │ 100 │ Must have common factor with b       │││
│  │ │ b      │ Integer  │ 10  │ 100 │ Must have common factor with a       │││
│  │ └────────┴──────────┴─────┴─────┴──────────────────────────────────────┘││
│  │ [+ Add Variable]                                                        ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │ Answer Options:                                                         ││
│  │ ┌──────┬──────────────────────────────────┬─────────────────────────┐  ││
│  │ │ ✅   │ {gcd(a, b)}                      │ Correct Answer           │  ││
│  │ │ ❌   │ {a * b}                          │ Misconception: Product   │  ││
│  │ │ ❌   │ {lcm(a, b)}                      │ Misconception: LCM       │  ││
│  │ │ ❌   │ {min(a, b)}                      │ Misconception: Smaller   │  ││
│  │ └──────┴──────────────────────────────────┴─────────────────────────┘  ││
│  │ [+ Add Option]                                                          ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │ Solution Explanation:                                                   ││
│  │ ┌─────────────────────────────────────────────────────────────────────┐ ││
│  │ │ Step 1: Find factors of {a}: {factors(a)}                           │ ││
│  │ │ Step 2: Find factors of {b}: {factors(b)}                           │ ││
│  │ │ Step 3: Common factors: {intersection}                              │ ││
│  │ │ Step 4: Greatest common factor = {gcd(a, b)}                        │ ││
│  │ └─────────────────────────────────────────────────────────────────────┘ ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │ 👁️ Live Preview:                                      [Regenerate 🔄]  ││
│  │ ┌─────────────────────────────────────────────────────────────────────┐ ││
│  │ │ Q: Find the GCD of 24 and 36.                                       │ ││
│  │ │                                                                     │ ││
│  │ │ ○ 12  ○ 864  ○ 72  ○ 24                                             │ ││
│  │ └─────────────────────────────────────────────────────────────────────┘ ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Features:**
- **Live preview** with actual generated values
- **Regenerate button** to see different variable combinations
- **Drag-and-drop** variable insertion
- **Built-in math functions**: gcd(), lcm(), factors(), primeFactors()
- **Misconception tagging** for analytics

### 5.4 Student Path Simulator ("Test Mode")

Before publishing, admins can simulate a student journey:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  🧪 Student Path Simulator              Math > Class 5 > Factors & Multiples│
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Simulation Profile:                                                        │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │ Student Type: [New Student ▼]  Accuracy: [70% ▼]  Speed: [Average ▼]   ││
│  │ [🚀 Start Simulation]  [⏸️ Pause]  [⏭️ Skip to End]                      ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                             │
│  Simulation Log:                                                            │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │ Step │ Concept        │ Question         │ Result │ Next Action         ││
│  │──────┼────────────────┼──────────────────┼────────┼─────────────────────││
│  │  1   │ Divisibility   │ div_basic_01     │ ✅     │ Continue            ││
│  │  2   │ Divisibility   │ div_basic_03     │ ✅     │ Continue            ││
│  │  3   │ Divisibility   │ div_apply_01     │ ❌     │ Stay (1/3 wrong)    ││
│  │  4   │ Divisibility   │ div_apply_02     │ ✅     │ Mastery! → Factors  ││
│  │  5   │ Factors        │ factors_basic_01 │ ❌     │ Stay (1/3 wrong)    ││
│  │  6   │ Factors        │ factors_basic_02 │ ❌     │ Stay (2/3 wrong)    ││
│  │  7   │ Factors        │ factors_basic_03 │ ❌     │ ⚠️ BACKTRACK check   ││
│  │  8   │ Divisibility   │ div_review_01    │ ✅     │ Back to Factors     ││
│  │ ...  │                │                  │        │                     ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                             │
│  ⚠️ Issues Found:                                                           │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │ ❌ DEAD END: "LCM" has 0 templates - student cannot progress           ││
│  │ ⚠️ LOW COVERAGE: "GCD Word Problems" has only 2 templates (min: 5)     ││
│  │ ✅ PASS: All prerequisites have content                                 ││
│  │ ✅ PASS: No cycles detected in graph                                    ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                             │
│  Path Visualization:                                                        │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                                                                         ││
│  │  [Divisibility] ━━▶ [Factors] ━━▶ [GCD] ━━▶ [LCM] ━━▶ ❌ BLOCKED       ││
│  │       4 Q            ↺ 8 Q        3 Q         0 Q                       ││
│  │                   (backtrack)                                           ││
│  │                                                                         ││
│  │  Total Questions: 15    Estimated Time: 22 min    Mastery: 2/5 concepts ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Simulation Features:**
- **Profile presets**: New student, struggling student, advanced student
- **Accuracy slider**: Control simulated student's correctness rate
- **Step-by-step playback**: Watch the algorithm make decisions
- **Dead end detection**: Alerts if any path leads to no content
- **Coverage warnings**: Highlights concepts with insufficient templates

### 5.5 Validation Rules Engine

The system validates content automatically:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  ✅ Validation Rules                                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  On Concept Creation:                                                       │
│  ├── ✅ Concept ID follows pattern: {subject}.class{grade}.{chapter}.{slug}│
│  ├── ✅ All prerequisites exist in the graph                               │
│  ├── ✅ No circular dependencies (DAG check)                               │
│  ├── ✅ Difficulty tier is 1, 2, or 3                                      │
│  └── ✅ At least one Bloom level selected                                  │
│                                                                             │
│  On Template Creation:                                                      │
│  ├── ✅ Concept exists and is active                                       │
│  ├── ✅ At least 4 answer options defined                                  │
│  ├── ✅ Exactly 1 correct answer marked                                    │
│  ├── ✅ All variables have valid ranges (min < max)                        │
│  ├── ✅ Question text contains at least one variable                       │
│  ├── ✅ Solution explanation is provided                                   │
│  └── ✅ Live preview generates without errors (10 iterations)              │
│                                                                             │
│  On Publish:                                                                │
│  ├── ✅ Concept has minimum 5 templates                                    │
│  ├── ✅ Templates cover all specified Bloom levels                         │
│  ├── ✅ All prerequisite concepts are already published                    │
│  ├── ✅ Student path simulation passes (no dead ends)                      │
│  └── ✅ Senior reviewer approval received                                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.6 Role-Based Access Control

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Admin Roles                                                                │
├────────────────┬────────────────────────────────────────────────────────────┤
│ Role           │ Permissions                                                │
├────────────────┼────────────────────────────────────────────────────────────┤
│ Content Writer │ • Create/edit templates (own)                              │
│                │ • View concept graph (read-only)                           │
│                │ • Run simulations                                          │
│                │ • Submit for review                                        │
├────────────────┼────────────────────────────────────────────────────────────┤
│ Curriculum     │ • All Content Writer permissions                           │
│ Designer       │ • Create/edit concepts                                     │
│                │ • Edit concept graph (add nodes, edges)                    │
│                │ • Set coverage targets                                     │
├────────────────┼────────────────────────────────────────────────────────────┤
│ Reviewer       │ • All Curriculum Designer permissions                      │
│                │ • Approve/reject templates                                 │
│                │ • View quality metrics                                     │
│                │ • Publish content                                          │
├────────────────┼────────────────────────────────────────────────────────────┤
│ Admin          │ • All permissions                                          │
│                │ • Manage users and roles                                   │
│                │ • Access analytics                                         │
│                │ • Configure system settings                                │
└────────────────┴────────────────────────────────────────────────────────────┘
```

### 5.7 Admin Panel Tech Stack

```
Frontend (Admin SPA):
├── React 18 + TypeScript
├── React Flow (graph visualization)
├── Shadcn/UI (component library)
├── TanStack Query (data fetching)
└── Zustand (state management)

Backend (Admin API):
├── FastAPI (existing backend)
├── /api/admin/concepts/* (CRUD)
├── /api/admin/templates/* (CRUD)
├── /api/admin/graphs/* (edges)
├── /api/admin/simulate/* (path testing)
└── /api/admin/validate/* (rule engine)
```

---

## 6. Admin Workflow (YAML-Free): Adding New Concept & Questions

> **✅ Service Layer Exists:** `AdminTemplateService` in `domain/admin/template_service.py`
> - `ingest_template()` — Creates template with validation
> - `submit_for_review()` — DRAFT → REVIEW transition
> - `approve_template()` — REVIEW → APPROVED
> - `publish_template()` — APPROVED → PUBLISHED
> - `get_templates_by_concept()` — Query templates

### 5.1 Step 1: Update Taxonomy

**Admin Action:** Add new concept to taxonomy

```yaml
# backend/config/content/taxonomy/math.yaml
concepts:
  # ... existing concepts ...
  
  # NEW CONCEPT
  - id: math.class5.factors_multiples.common_factors
    name: Find common factors of two numbers
    grades: [5]
    bloom_level: UNDERSTAND
    difficulty_range: [2, 3]
    prerequisites:
      - math.class5.factors_multiples.factors
```

**Validation:** System validates:
- ✅ Concept ID follows naming convention
- ✅ Prerequisites exist in taxonomy
- ✅ Bloom level is valid
- ✅ Difficulty range is valid

---

### 5.2 Step 2: Update Concept Graph

**Admin Action:** Add concept node and edges

```yaml
# backend/config/content/graphs/math/class5/factors_multiples.yaml
nodes:
  # ... existing nodes ...
  
  # NEW NODE
  - concept_id: math.class5.factors_multiples.common_factors
    bloom_targets: [UNDERSTAND, APPLY]
    difficulty_default: 2
    description: "Find factors common to two numbers"

edges:
  # ... existing edges ...
  
  # NEW EDGES
  - from: math.class5.factors_multiples.factors
    to: math.class5.factors_multiples.common_factors
    kind: prerequisite
    reason: "Must know how to find factors of individual numbers first"
    
  - from: math.class5.factors_multiples.common_factors
    to: math.class5.factors_multiples.gcd
    kind: prerequisite
    reason: "Common factors are needed to understand GCD"
```

---

### 5.3 Step 3: Update Blueprint (Coverage Target)

**Admin Action:** Set content coverage target

```yaml
# backend/config/content/blueprints/math/class5/factors_multiples.yaml
coverage_targets:
  by_concept_id:
    # ... existing ...
    
    math.class5.factors_multiples.common_factors:
      min_per_week: 8
      difficulty_mix: {"2": 0.6, "3": 0.4}
      bloom_mix: {UNDERSTAND: 0.7, APPLY: 0.3}
      priority: high
      notes: "Bridge concept between factors and GCD"
```

---

### 5.4 Step 4: Create Question Templates

**Admin Action:** Create templates via Admin API

```bash
POST /api/admin/templates/ingest
```

```json
{
  "templates": [
    {
      "concept_id": "math.class5.factors_multiples.common_factors",
      "template_code": "common_factors_basic_01",
      "difficulty": 2,
      "bloom_level": "UNDERSTAND",
      "question_pattern": "Find the common factors of {{a}} and {{b}}.",
      "variable_schema": {
        "a": {"type": "integer", "min": 10, "max": 50},
        "b": {"type": "integer", "min": 10, "max": 50}
      },
      "option_patterns": [
        {"pattern": "{{common_factors}}", "is_correct": true},
        {"pattern": "{{distractor_1}}", "is_correct": false, "misconception_id": "only_small_factors"},
        {"pattern": "{{distractor_2}}", "is_correct": false, "misconception_id": "all_factors_of_a"},
        {"pattern": "{{distractor_3}}", "is_correct": false, "misconception_id": "all_factors_of_b"}
      ],
      "answer_logic": "set(factors(a)) & set(factors(b))",
      "estimated_time": 120
    }
  ]
}
```

---

### 5.5 Step 5: Review & Publish Workflow

```
Template Lifecycle:
┌────────┐    ┌────────┐    ┌──────────┐    ┌───────────┐    ┌──────────┐
│ DRAFT  │ →  │ REVIEW │ →  │ APPROVED │ →  │ PUBLISHED │ →  │ ARCHIVED │
└────────┘    └────────┘    └──────────┘    └───────────┘    └──────────┘
     ↑              │              │               │
     └──────────────┴──────────────┘               │
           (rejected - return to draft)            │
                                                   ↓
                                        (retired after 6 months)
```

**Validation at Each Stage:**

| Stage | Validation |
|-------|------------|
| DRAFT → REVIEW | Taxonomy validation (concept exists) |
| REVIEW → APPROVED | Rubric validation (quality gate) |
| APPROVED → PUBLISHED | Coverage check (meets blueprint targets) |

---

## 7. Data Models Overview

> **✅ All models implemented** in `db/models/`

### 6.1 Current Configuration Files (YAML)

```
backend/config/content/
├── taxonomy/
│   └── math.yaml           # All valid concept IDs
├── graphs/
│   └── math/class5/
│       └── factors_multiples.yaml   # Prerequisite graph
├── blueprints/
│   └── math/class5/
│       └── factors_multiples.yaml   # Coverage targets
└── rubrics/
    └── question_quality.yaml        # Quality rules
```

### 6.2 Database Tables (PostgreSQL)

```sql
-- Concept mastery per student
student_concept_state (
    student_id, concept_id, 
    leitner_box, due_at, 
    attempts, correct, accuracy
)

-- Question templates (Phase 3)
question_templates (
    id, concept_id, template_code,
    question_pattern, variable_schema, answer_logic,
    difficulty, bloom_level, status
)

-- Learning events (audit trail)
learning_events (
    student_id, session_id, 
    event_type, concept_id, 
    payload, timestamp
)
```

---

## 8. API Endpoints for Content Management

### 8.1 Admin APIs (Content Management) — 🔶 PARTIAL

> **Service layer exists:** `AdminTemplateService` handles business logic
> **Missing:** FastAPI route handlers in `api/routes/admin.py`

```
# Taxonomy Management — ⬜ NOT BUILT (use YAML for now)
GET  /api/admin/taxonomy/{subject}           # Get all concepts
POST /api/admin/taxonomy/{subject}/concepts  # Add new concept
PUT  /api/admin/taxonomy/{subject}/concepts/{id}  # Update concept

# Graph Management  
GET  /api/admin/graphs/{subject}/{grade}/{chapter}  # Get concept graph
PUT  /api/admin/graphs/{subject}/{grade}/{chapter}  # Update graph

# Template Management
POST /api/admin/templates/ingest             # Bulk ingest templates
GET  /api/admin/templates?concept_id=X       # Query templates
POST /api/admin/templates/{id}/submit        # Submit for review
POST /api/admin/templates/{id}/approve       # Approve template
POST /api/admin/templates/{id}/publish       # Publish template

# Coverage QA
GET  /api/admin/coverage/{subject}/{grade}/{chapter}  # Coverage report
```

### 8.2 Student APIs (Runtime) — ✅ BUILT

> **Implemented in:** `backend/app_main.py`

```
# Session Management — ✅ BUILT
POST /api/quiz/session/start                 # Start practice session
GET  /api/quiz/{session_id}/question         # Get next question
POST /api/quiz/{session_id}/answer           # Submit answer
GET  /api/quiz/{session_id}/hint             # Get hint
POST /api/quiz/{session_id}/end              # End session

# Progress Tracking — ✅ BUILT
POST /api/student/register                   # Register student
GET  /api/student/{id}/progress              # Overall progress
GET  /api/student/{id}/misconceptions        # Misconception report
GET  /api/student/{id}/mastery/{chapter}     # Chapter mastery
POST /api/student/{id}/mastery/{chapter}/reset  # Reset progress
```

---

## 9. Dynamic Metadata (Testbook-Style Analytics) — ⬜ NOT BUILT

> **Dependency:** Requires `concept_metadata` table and nightly job
> **Data Source:** `learning_events` table (exists)

### 9.1 The Problem with Static Difficulty

Traditional approach: Author assigns `difficulty: MEDIUM` when creating question.
Problem: This is subjective and may not reflect actual student experience.

### 9.2 Calculated Difficulty

Our approach: Compute difficulty from actual student performance data.

```python
# Nightly job: backend/jobs/compute_concept_metadata.py

def compute_concept_metadata():
    """Update concept_metadata table from actual student attempts."""
    for concept in get_all_concepts():
        attempts = get_recent_attempts(concept.id, days=30)
        if not attempts:
            continue
        
        total = len(attempts)
        correct = sum(1 for a in attempts if a.is_correct)
        times = [a.time_spent for a in attempts]
        
        metadata = {
            'accuracy_rate': correct / total,
            'calculated_difficulty': 1 - (correct / total),  # Inverse of accuracy
            'avg_time_to_solve_seconds': sum(times) / len(times),
            'p50_time_seconds': percentile(times, 50),
            'p90_time_seconds': percentile(times, 90),
            'skip_rate': count_skips(concept.id) / total,
            'total_attempts': total,
            'total_students': count_unique_students(attempts),
        }
        
        upsert_concept_metadata(concept.id, metadata)
```

### 9.3 Using Dynamic Metadata

```python
# Query "genuinely hard" questions
def get_hard_mode_questions(chapter_key):
    return db.query(ConceptNodes).join(ConceptMetadata).filter(
        ConceptNodes.chapter_key == chapter_key,
        ConceptMetadata.calculated_difficulty > 0.6,  # <40% accuracy
    ).all()

# Adaptive time limits
def get_time_limit(concept_id):
    metadata = get_concept_metadata(concept_id)
    return metadata.p90_time_seconds * 1.2  # 20% buffer over 90th percentile
```

---

## 10. Concept Navigation Visualization

When a student starts Chapter 9, the system can visualize their learning path:

```
Student: John Doe
Chapter: Factors & Multiples
Progress: 3/11 concepts mastered

┌─────────────────────────────────────────────────────────────────────┐
│                        CONCEPT MAP                                  │
│                                                                     │
│   ✅ Divisibility ─────┬──────→ ✅ Factors ────→ 🔄 GCD ──────┐    │
│         │              │              │                        │    │
│         │              │              └──→ 🔄 Common Factors ──┤    │
│         │              │                                       │    │
│         └──────→ ✅ Prime/Composite ──→ ⬜ Prime Factorization │    │
│                        │                                       │    │
│                        └──────→ ⬜ Multiples ───→ ⬜ LCM ──────┤    │
│                                                                │    │
│                                          ⬜ Word Problems ←────┘    │
│                                                  │                  │
│                                                  ↓                  │
│                                    ⬜ Assertion-Reason              │
│                                          │                          │
│                                          ↓                          │
│                                    ⬜ Error Analysis                 │
│                                                                     │
│   Legend: ✅ Mastered  🔄 Learning  ⬜ Not Started                  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 11. Implementation Checklist

### Phase A: Content Structure Refinement — ✅ COMPLETE
- [x] Standardize concept ID naming: `{subject}.{grade}.{chapter}.{concept}` → `config/content/taxonomy/math.yaml`
- [x] Complete taxonomy for Class 5 Math (12 concepts in Factors & Multiples)
- [x] Create concept graphs → `config/content/graphs/math/class5/factors_multiples.yaml`
- [ ] Create blueprints with coverage targets (directory exists, files pending)

### Phase B: Admin API Implementation — ✅ COMPLETE
- [x] Template CRUD service (`domain/admin/template_service.py`)
- [x] Taxonomy validation (`domain/content_validation/taxonomy_validator.py`)
- [x] Rubric validation (`domain/content_validation/rubric_validator.py`)
- [x] REST endpoints (`/api/admin/taxonomy/*`) — `api/admin/graphs.py`
p;- [x] Graph management API (`/api/admin/graphs/*`) — `api/admin/graphs.py`
- [x] Coverage report API (`/api/admin/coverage/*`) — `api/admin/graphs.py`
- [x] Graph validation endpoint (`POST /validate`)
- [x] REST endpoints (`/api/admin/templates/*`) — `api/admin/templates.py`
- [x] Misconceptions API (`/api/admin/templates/misconceptions/*`) — `api/admin/templates.py`
- [ ] Simulation API (`/api/admin/simulate/*`) — Phase E

### Phase C: Admin Panel - Graph Builder — ✅ COMPLETE
- [x] React Flow graph builder (drag-drop nodes) — `admin-ui/src/pages/GraphBuilder.tsx`
- [x] Node inspector panel — `admin-ui/src/components/graph/NodeInspector.tsx`
- [x] Custom ConceptNode component — `admin-ui/src/components/graph/ConceptNode.tsx`
- [x] Edge creation UI (click and drag between nodes)
- [x] Validation feedback (validate button with toast notifications)
- [x] Save/Reset functionality
- [x] MiniMap and zoom controls
- [x] Subject/Grade/Chapter filters
- [x] Navigation link in sidebar

### Phase D: Admin Panel - Template Builder — ✅ COMPLETE
- [x] Template list page with filtering — `admin-ui/src/pages/TemplateList.tsx`
- [x] Enhanced template editor with live preview — `admin-ui/src/pages/TemplateEditorEnhanced.tsx`
- [x] Variable schema visual editor — `admin-ui/src/components/template/VariableSchemaEditor.tsx`
- [x] Option pattern editor with correct answer marking
- [x] Misconception tagging UI — `admin-ui/src/components/template/MisconceptionTagger.tsx`
- [x] Live preview panel — `admin-ui/src/components/template/LivePreviewPanel.tsx`
- [x] Quality content editors (solution, hints, narrative patterns)
- [x] Diagram configuration selector (CDN integration)
- [x] Submit for review workflow
- [x] Backend preview endpoint (`POST /api/admin/templates/{id}/preview`)

### Phase E: Admin Panel - Path Simulator — ⬜ NOT STARTED
- [ ] Student path simulator backend API
- [ ] Simulator UI component
- [ ] Profile presets (new, struggling, advanced)
- [ ] Dead-end detection
- [ ] Coverage warnings

### Phase F: ConceptNavigator Integration — ✅ COMPLETE
- [x] `ConceptGraph` class (`domain/adaptation/concept_graph.py`)
- [x] `Sequencer` with 4 strategies (`domain/adaptation/sequencer.py`)
- [x] `MasteryTracker` with Leitner (`domain/adaptation/mastery.py`)
- [x] Prerequisite-aware question selection

### Phase G: Nightly Metadata Computation — ⬜ NOT STARTED
- [ ] Create `concept_metadata` table
- [ ] Nightly job to compute from `learning_events`
- [ ] API to expose dynamic difficulty

### Phase H: Student-Facing Visualization — 🔶 PARTIAL
- [x] Chapter selection in frontend
- [x] Progress tracking (`StudentConceptState`)
- [ ] Concept map visualization during practice

---

## 12. Best Practices for Content Quality

### 12.1 Concept Design
- Each concept should be **atomic** (one skill/understanding)
- Concept name should be **action-oriented** (verb + noun)
- Prerequisites should be **explicitly declared**

### 12.2 Question Templates
- Minimum 10 templates per concept
- Cover all allowed Bloom levels
- Include common misconceptions as distractors
- Variable schemas should generate diverse instances

### 12.3 Quality Assurance
- All templates pass rubric validation before publishing
- Coverage QA runs weekly to identify gaps
- Student analytics inform content iteration

---

## 13. Summary: Our Architecture vs Industry Leaders

### Comparison Table

| Aspect | Traditional EdTech | Testbook | Khan Academy | **Our System** |
|--------|-------------------|----------|--------------|----------------|
| Content | Static questions | Static + metadata | Videos + exercises | **Generative templates** |
| Difficulty | Pre-assigned | Calculated from data | Fixed per exercise | **Calculated dynamically** |
| Navigation | Linear chapters | Tag-based filtering | Skill tree | **DAG with prerequisites** |
| Remediation | Show solution | Hint videos | Mastery challenges | **Auto-backtrack to prereq** |
| Scaling | Add more questions | Add more questions | Add content creators | **Add templates/generators** |
| Quality | Manual review | Crowd feedback | Expert curated | **Rubric-validated** |
| **Admin UX** | SQL/Code | Form-based | CMS | **Visual drag-drop** |
| Personalization | Basic | Weak question history | Strong | **Strong + spaced repetition** |

### Key Differentiators

1. **Infinite Question Variety**: 500 templates can generate 50,000+ unique questions
2. **True Adaptive Learning**: DAG traversal ensures no concept is attempted before prerequisites
3. **Automatic Remediation**: System detects struggling students and backtracks to weak prerequisites
4. **Data-Driven Difficulty**: Difficulty is calculated from actual student performance, not author opinion
5. **Scalable Content Pipeline**: New concepts require YAML + templates, not database migrations
6. **Quality Gates**: Every template passes rubric validation before reaching students

### Architecture Principles

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CONTENT MANAGEMENT PRINCIPLES                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. SINGLE SOURCE OF TRUTH                                          │
│     └── Database → Admin Panel → All services reference             │
│                                                                     │
│  2. PREREQUISITE-FIRST NAVIGATION                                   │
│     └── Cannot attempt GCD until Factors is MASTERED               │
│                                                                     │
│  3. CALCULATED, NOT ASSIGNED                                        │
│     └── Difficulty = 1 - (global_accuracy_rate)                    │
│                                                                     │
│  4. GENERATOR-TO-CONCEPT MAPPING                                    │
│     └── Questions are generated for concepts, not chapters          │
│                                                                     │
│  5. MASTERY-GATED PROGRESSION                                       │
│     └── 80% accuracy + 3 attempts + Leitner box 3 = MASTERED       │
│                                                                     │
│  6. AUTOMATIC REMEDIATION                                           │
│     └── 3 wrong in a row + weak prerequisite = BACKTRACK           │
│                                                                     │
│  7. NO-CODE CONTENT MANAGEMENT                                      │
│     └── Content writers use visual tools, never touch code/SQL     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Next Steps: Implementation Phases

| Phase | Scope | Status | Notes |
|-------|-------|--------|-------|
| **A** | Content structure (taxonomy, graphs) | ✅ Done | `config/content/` populated |
| **B** | Admin APIs (REST endpoints) | ✅ Done | `api/admin/graphs.py` — Graph, Coverage, Taxonomy APIs |
| **C** | **Admin Panel - Graph Builder** (React Flow) | ✅ Done | `admin-ui/src/pages/GraphBuilder.tsx` |
| **D** | **Admin Panel - Template Builder** (live preview) | ⬜ Not started | Next priority |
| **E** | **Admin Panel - Path Simulator** (test mode) | ⬜ Not started | |
| **F** | ConceptNavigator engine integration | ✅ Done | `domain/adaptation/` |
| **G** | Nightly metadata computation job | ⬜ Not started | |
| **H** | Student-facing concept map visualization | 🔶 Partial | Progress exists, map UI pending |

---

*This architecture enables a ₹200-300/month platform to deliver Khan Academy-level adaptive learning with Testbook-level analytics, powered by generative content and a visual admin panel that empowers non-developers to manage curriculum.*

---

## Appendix: Code Reference Map

Quick lookup for developers:

```
ADAPTIVE LEARNING ENGINE
├── domain/adaptation/
│   ├── concept_graph.py    # ConceptGraph.load(), get_prerequisites(), get_ready_concepts()
│   ├── sequencer.py        # Sequencer.get_next_target(), SequencingStrategy enum
│   ├── mastery.py          # MasteryTracker, MasteryLevel, ConceptMastery
│   └── selector.py         # Question selection logic

TEMPLATE ENGINE
├── domain/template_engine/
│   └── lean_template_engine.py  # LeanTemplateEngine.generate(), VariableGenerator

ADMIN SERVICE
├── domain/admin/
│   └── template_service.py      # AdminTemplateService (ingest, workflow, publish)

CONTENT VALIDATION
├── domain/content_validation/
│   ├── taxonomy_validator.py    # validate_concept_id(), validate_bloom_level()
│   └── rubric_validator.py      # Quality gate rules

DATABASE MODELS
├── db/models/
│   ├── concepts.py         # ConceptCatalog, StudentConceptState, StudentBreakpoint
│   ├── templates.py        # QuestionTemplate, TemplateStatus, Misconception
│   ├── session.py          # LearningSession
│   └── events.py           # LearningEvent

CONFIGURATION (YAML)
├── config/content/
│   ├── taxonomy/math.yaml           # 12 concepts for Factors & Multiples
│   ├── graphs/math/class5/          # DAG definitions
│   ├── blueprints/                  # Coverage targets (pending)
│   └── rubrics/                     # Quality rules (pending)

ADMIN API ROUTES
├── api/admin/
│   ├── graphs.py           # graphs_router, coverage_router, taxonomy_router
│   │   ├── GET  /api/admin/graphs/{subject}/{grade}/{chapter}
│   │   ├── PUT  /api/admin/graphs/{subject}/{grade}/{chapter}
│   │   ├── POST /api/admin/graphs/{subject}/{grade}/{chapter}/validate
│   │   ├── GET  /api/admin/coverage/{subject}/{grade}/{chapter}
│   │   └── GET  /api/admin/taxonomy/{subject}
│   └── templates.py        # Template CRUD routes (existing)

ADMIN PANEL UI (admin-ui/)
├── src/
│   ├── pages/
│   │   ├── GraphBuilder.tsx              # React Flow concept graph editor
│   │   ├── Dashboard.tsx                 # Admin dashboard
│   │   ├── TemplateList.tsx              # Template listing
│   │   ├── TemplateEditor.tsx            # Basic template editor
│   │   ├── TemplateEditorEnhanced.tsx    # Enhanced editor with live preview (Phase D)
│   │   ├── CoverageDashboard.tsx         # Coverage reports
│   │   └── ReviewQueue.tsx               # Template review queue
│   ├── components/
│   │   ├── graph/
│   │   │   ├── ConceptNode.tsx           # Custom React Flow node
│   │   │   └── NodeInspector.tsx         # Side panel for node editing
│   │   ├── template/                     # Phase D: Template editor components
│   │   │   ├── VariableSchemaEditor.tsx  # Visual JSON schema editor
│   │   │   ├── MisconceptionTagger.tsx   # Option-misconception linking UI
│   │   │   ├── LivePreviewPanel.tsx      # Real-time template preview
│   │   │   └── index.ts                  # Component exports
│   │   └── Layout.tsx                    # Main layout with navigation
│   └── api.ts                            # API client with TanStack Query hooks

CLI TOOLS
├── tools/
│   ├── coverage_qa_cli.py           # Check template coverage
│   ├── llm_template_generator.py    # Batch generate with LLM
│   ├── template_migrator.py         # Migrate legacy templates
│   └── seed_concepts.py             # Seed taxonomy to DB
```
