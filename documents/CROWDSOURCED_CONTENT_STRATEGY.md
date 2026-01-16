# Crowdsourced Content Strategy: Solving the Question Bank Bottleneck

**Version:** 1.0  
**Date:** January 2025  
**Status:** Strategy Discussion  

---

## 1. The Core Problem: Content Bottleneck

### What We're Trying to Build

```
Goal: Replace ₹2,000-5,000/month private tutor for CBSE Classes 3-10
      with a ₹200/month AI-powered practice engine

Requirements:
├── Infinite question variations (no memorization possible)
├── Step-by-step solutions (like a tutor explains)
├── Concept-based progression (foundation → mastery)
├── Cross-concept questions (connecting ideas)
├── Competition-level questions (Olympiad, NTSE)
├── Personalized difficulty (adapts to each student)
└── Instant feedback with misconception detection
```

### The Bottleneck

```
┌─────────────────────────────────────────────────────────────────────┐
│                     CONTENT CREATION BOTTLENECK                      │
│                                                                      │
│  Traditional Approach:                                               │
│  ├── Hire content experts (expensive, slow)                          │
│  ├── 8 grades × 3 subjects × 14 chapters × 10 concepts = ~3,360 units│
│  ├── Each unit needs: 100+ question variations = 336,000 questions   │
│  ├── Cost: ₹10/question × 336K = ₹33.6 Lakhs                        │
│  ├── Time: 2-3 years to build comprehensive bank                    │
│  └── PROBLEM: Still finite, students can exhaust the bank           │
│                                                                      │
│  Our Solution: Hybrid approach                                       │
│  ├── Crowdsourced TEMPLATES (humans provide creativity)              │
│  ├── LLM VALIDATION (ensures quality at scale)                       │
│  ├── PARAMETRIC GENERATORS (infinite variations from templates)      │
│  └── COMMUNITY REWARDS (gig economy model)                          │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. The Strategy: Three Pillars

```
┌─────────────────────────────────────────────────────────────────────┐
│                     THREE-PILLAR STRATEGY                            │
│                                                                      │
│  PILLAR 1: CROWDSOURCED TEMPLATES                                   │
│  ├── Teachers, tutors, college students contribute                  │
│  ├── They provide: Story template + Solution pattern + Distractors  │
│  ├── NOT raw questions - TEMPLATES that can generate ∞ variations   │
│  └── Reward: ₹5-50 per approved template                            │
│                                                                      │
│  PILLAR 2: LLM QUALITY GATE                                         │
│  ├── Validates mathematical correctness                              │
│  ├── Checks pedagogical quality (grade-appropriate)                  │
│  ├── Scores against content rules (YAML configs)                    │
│  ├── Detects plagiarism / duplicate patterns                        │
│  └── Assigns quality score (0-100)                                  │
│                                                                      │
│  PILLAR 3: PARAMETRIC ENGINE                                        │
│  ├── Takes approved template                                         │
│  ├── Generates infinite number variations                            │
│  ├── Uses reverse construction (answer → question)                  │
│  └── Stored in Notion/Database (not code files!)                    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. Crowdsourced Content Platform

### 3.1 Contributor Types & Rewards

```
┌─────────────────────────────────────────────────────────────────────┐
│                     CONTRIBUTOR TIERS                                │
│                                                                      │
│  TIER 1: BASIC CONTRIBUTOR (12th Pass, College Students)            │
│  ├── Can submit: Story templates, solution steps                    │
│  ├── Reward: ₹5-15 per approved template                            │
│  ├── Quality threshold: Score ≥ 60/100                              │
│  └── Weekly limit: 50 templates (prevents spam)                     │
│                                                                      │
│  TIER 2: VERIFIED CONTRIBUTOR (B.Ed, Teachers)                      │
│  ├── Can submit: Complex questions, cross-concept templates         │
│  ├── Reward: ₹20-50 per approved template                           │
│  ├── Quality threshold: Score ≥ 70/100                              │
│  ├── Can review Tier 1 submissions (₹2 per review)                  │
│  └── Weekly limit: 100 templates                                    │
│                                                                      │
│  TIER 3: EXPERT CONTRIBUTOR (Subject Teachers, Tutors)              │
│  ├── Can submit: Competition-level, Olympiad questions              │
│  ├── Reward: ₹50-200 per approved template                          │
│  ├── Quality threshold: Score ≥ 80/100                              │
│  ├── Can create new content rules (YAML configs)                    │
│  └── Monthly retainer option: ₹5,000-15,000                         │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 Submission UI Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                     CONTRIBUTOR PORTAL                               │
│                                                                      │
│  Step 1: SELECT CONCEPT                                             │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │ Subject: [Math ▼]  Grade: [5 ▼]  Chapter: [Factors & Multiples ▼]│
│  │ Concept: [GCD ▼]   Difficulty: [●○○○ Easy]                      ││
│  └─────────────────────────────────────────────────────────────────┘│
│                                                                      │
│  Step 2: VIEW CONTENT RULES (from YAML)                             │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │ 📋 Content Rules for GCD (Class 5)                               ││
│  │ ├── Bloom Level: APPLY                                          ││
│  │ ├── Number Range: 6-100                                         ││
│  │ ├── Must use: Real-world context (grouping, distribution)       ││
│  │ ├── Solution must show: Factor listing method                   ││
│  │ └── Distractors must include: Product confusion, min(a,b)       ││
│  └─────────────────────────────────────────────────────────────────┘│
│                                                                      │
│  Step 3: SUBMIT TEMPLATE                                            │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │ Story Template (use {a}, {b}, {name} as placeholders):          ││
│  │ ┌───────────────────────────────────────────────────────────────┐│
│  │ │ {name} has {a} mangoes and {b} oranges. She wants to pack    ││
│  │ │ them into boxes with equal number of fruits in each box.     ││
│  │ │ What is the maximum number of fruits in each box?            ││
│  │ └───────────────────────────────────────────────────────────────┘│
│  │                                                                  ││
│  │ Solution Steps Template:                                         ││
│  │ ┌───────────────────────────────────────────────────────────────┐│
│  │ │ 1. Find factors of {a}: {factors_a}                          ││
│  │ │ 2. Find factors of {b}: {factors_b}                          ││
│  │ │ 3. Common factors: {common_factors}                          ││
│  │ │ 4. GCD = {answer}                                            ││
│  │ └───────────────────────────────────────────────────────────────┘│
│  │                                                                  ││
│  │ Distractor Ideas (why students might pick wrong):               ││
│  │ ┌───────────────────────────────────────────────────────────────┐│
│  │ │ 1. a × b (thinks multiply instead of GCD)                    ││
│  │ │ 2. min(a, b) (picks smaller number directly)                 ││
│  │ │ 3. a + b (adds instead of finding common divisor)            ││
│  │ └───────────────────────────────────────────────────────────────┘│
│  └─────────────────────────────────────────────────────────────────┘│
│                                                                      │
│  Step 4: LLM VALIDATION (Real-time)                                 │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │ 🤖 Validating your submission...                                ││
│  │                                                                  ││
│  │ ✅ Mathematical Correctness: 95/100                             ││
│  │    - Formula correct                                            ││
│  │    - Solution steps valid                                       ││
│  │                                                                  ││
│  │ ✅ Pedagogical Quality: 88/100                                  ││
│  │    - Grade-appropriate language                                 ││
│  │    - Clear context                                              ││
│  │    - ⚠️ Suggestion: Add "without any fruit left over"          ││
│  │                                                                  ││
│  │ ✅ Content Rule Compliance: 92/100                              ││
│  │    - Real-world context ✓                                       ││
│  │    - Distractors match required types ✓                        ││
│  │                                                                  ││
│  │ ✅ Originality: 100/100                                         ││
│  │    - No duplicate pattern found                                 ││
│  │                                                                  ││
│  │ 📊 OVERALL SCORE: 94/100 - APPROVED! 🎉                         ││
│  │ 💰 Reward: ₹15 credited to your wallet                         ││
│  └─────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────┘
```

### 3.3 LLM Validation Prompt

```python
# backend/services/llm_validator.py

VALIDATION_PROMPT = """
You are a content quality validator for an educational platform.

CONTENT RULES (from YAML):
{content_rules}

SUBMISSION:
- Concept: {concept_id}
- Difficulty: {difficulty}
- Story Template: {story_template}
- Solution Steps: {solution_steps}
- Distractors: {distractors}

VALIDATION TASKS:

1. MATHEMATICAL CORRECTNESS (0-100):
   - Is the mathematical concept correctly applied?
   - Will the solution steps always produce the correct answer?
   - Are the distractor formulas valid (produce plausible wrong answers)?

2. PEDAGOGICAL QUALITY (0-100):
   - Is the language appropriate for grade {grade}?
   - Is the context relatable for Indian students?
   - Are the solution steps clear and educational?
   - Do distractors target real misconceptions?

3. CONTENT RULE COMPLIANCE (0-100):
   - Does it match the required Bloom level?
   - Is the number range appropriate?
   - Does it follow the required format?

4. ORIGINALITY (0-100):
   - Is this a unique template pattern?
   - Compare against existing templates: {existing_patterns}

OUTPUT FORMAT (JSON):
{
  "scores": {
    "mathematical": 95,
    "pedagogical": 88,
    "compliance": 92,
    "originality": 100
  },
  "overall": 94,
  "approved": true,
  "suggestions": ["Add 'without any fruit left over' for clarity"],
  "issues": [],
  "reward_amount": 15
}
"""
```

---

## 4. Question Type Coverage Strategy

### 4.1 The Five Question Tiers

```
┌─────────────────────────────────────────────────────────────────────┐
│                     QUESTION TIER SYSTEM                             │
│                                                                      │
│  TIER 1: CONCEPT FOUNDATION (Bloom: Remember, Understand)           │
│  ├── Source: Parametric engine (auto-generated)                     │
│  ├── Examples: "Find factors of 24", "Is 17 prime?"                │
│  ├── Variation: ∞ (just change numbers)                            │
│  └── Crowdsourcing need: LOW (formulas are standard)               │
│                                                                      │
│  TIER 2: APPLICATION (Bloom: Apply)                                 │
│  ├── Source: Crowdsourced story templates                          │
│  ├── Examples: Word problems with real contexts                     │
│  ├── Variation: ∞ (same story, different numbers)                  │
│  └── Crowdsourcing need: HIGH (need diverse contexts)              │
│                                                                      │
│  TIER 3: CROSS-CONCEPT (Bloom: Analyze)                            │
│  ├── Source: Expert contributors + LLM synthesis                   │
│  ├── Examples: GCD+LCM combined, Fractions+Decimals                │
│  ├── Variation: High (multiple concept combinations)               │
│  └── Crowdsourcing need: MEDIUM (experts design patterns)          │
│                                                                      │
│  TIER 4: HIGHER-ORDER (Bloom: Evaluate, Create)                    │
│  ├── Source: Teacher experts + Curated from textbooks              │
│  ├── Examples: Error analysis, assertion-reason                     │
│  ├── Variation: Medium (limited valid patterns)                    │
│  └── Crowdsourcing need: HIGH (need pedagogical expertise)         │
│                                                                      │
│  TIER 5: COMPETITION (Olympiad, NTSE)                              │
│  ├── Source: Expert contributors + Past paper analysis             │
│  ├── Examples: Multi-step proofs, trick questions                  │
│  ├── Variation: Low (each is unique)                               │
│  └── Crowdsourcing need: EXPERT ONLY (high reward)                 │
└─────────────────────────────────────────────────────────────────────┘
```

### 4.2 How Each Tier is Generated

```
TIER 1 (Foundation) - FULLY AUTOMATED
┌──────────────────────────────────────────────────────────────────┐
│ Input: Concept + Difficulty                                       │
│ Engine: Parametric Generator (Python)                            │
│ Process:                                                          │
│   1. Pick number range based on difficulty                       │
│   2. Generate numbers using reverse construction                  │
│   3. Apply standard question template                            │
│   4. Generate formula-based distractors                          │
│ Output: Infinite unique questions                                 │
│ LLM Role: NONE (pure math)                                       │
└──────────────────────────────────────────────────────────────────┘

TIER 2 (Application) - CROWDSOURCED TEMPLATES
┌──────────────────────────────────────────────────────────────────┐
│ Input: Concept + Difficulty + Story Template (from crowd)        │
│ Engine: Template Engine + Parametric Numbers                     │
│ Process:                                                          │
│   1. Select random approved story template                       │
│   2. Generate numbers using reverse construction                  │
│   3. Fill template placeholders                                  │
│   4. Generate contextual distractors                             │
│ Output: Infinite variations per template                          │
│ LLM Role: Validate templates (one-time), NOT runtime             │
└──────────────────────────────────────────────────────────────────┘

TIER 3 (Cross-Concept) - ORCHESTRATOR + TEMPLATES
┌──────────────────────────────────────────────────────────────────┐
│ Input: Concept pair (from graph co-requisites) + Difficulty      │
│ Engine: Orchestrator + Composite Template Engine                 │
│ Process:                                                          │
│   1. Orchestrator checks student mastery on both concepts        │
│   2. Selects cross-concept template from approved pool           │
│   3. Generates numbers satisfying both concept constraints       │
│   4. Builds multi-part question or relationship question         │
│ Output: Infinite variations, but more constrained                │
│ LLM Role: Help design cross-concept templates (one-time)         │
└──────────────────────────────────────────────────────────────────┘

TIER 4 (Higher-Order) - EXPERT + LLM SYNTHESIS
┌──────────────────────────────────────────────────────────────────┐
│ Input: Expert-designed template + Multiple correct/wrong paths   │
│ Engine: Template Engine + Reasoning Validator                    │
│ Process:                                                          │
│   1. Expert provides assertion-reason pair or error scenario     │
│   2. LLM validates logical consistency                           │
│   3. Engine generates variations with same logical structure     │
│   4. Each variation requires validation                          │
│ Output: Limited variations (logic must be preserved)             │
│ LLM Role: Validate reasoning chains (one-time per template)      │
└──────────────────────────────────────────────────────────────────┘

TIER 5 (Competition) - CURATED + MINIMAL VARIATION
┌──────────────────────────────────────────────────────────────────┐
│ Input: Past Olympiad questions + Expert-created originals        │
│ Engine: Curated Bank + Number Substitution (limited)             │
│ Process:                                                          │
│   1. Expert submits competition-level question                   │
│   2. LLM validates difficulty and correctness                    │
│   3. Stored as semi-fixed template                               │
│   4. Limited number variations (preserve trick/insight)          │
│ Output: Finite but high-quality questions                        │
│ LLM Role: Validate difficulty level, ensure not too easy         │
└──────────────────────────────────────────────────────────────────┘
```

---

## 5. Economics of Crowdsourcing

### 5.1 Cost Comparison

```
┌─────────────────────────────────────────────────────────────────────┐
│                     COST ANALYSIS                                    │
│                                                                      │
│  TRADITIONAL: Hire Full-Time Content Team                           │
│  ├── 5 content writers × ₹40K/month = ₹2L/month                    │
│  ├── 1 subject expert × ₹80K/month = ₹0.8L/month                   │
│  ├── Output: ~1,000 questions/month                                 │
│  ├── Cost per question: ₹280                                       │
│  └── Time to 100K questions: 100 months (8+ years!)                │
│                                                                      │
│  CROWDSOURCED: Gig Economy Model                                    │
│  ├── 1,000 Tier 1 contributors × 20 templates/month = 20K templates│
│  ├── Average reward: ₹10/template = ₹2L/month                      │
│  ├── LLM validation: ₹0.5/validation × 30K submissions = ₹15K/month│
│  ├── Platform overhead: ₹50K/month                                 │
│  ├── Total: ₹2.65L/month                                           │
│  ├── Output: ~15K approved templates/month                         │
│  ├── Each template → ∞ variations                                   │
│  ├── Cost per template: ₹18                                        │
│  └── Time to 100K templates: 7 months                              │
│                                                                      │
│  SAVINGS: 94% cost reduction + 10x faster                          │
│  BONUS: Each template = infinite questions!                         │
└─────────────────────────────────────────────────────────────────────┘
```

### 5.2 Reward Structure

```yaml
# config/rewards.yaml

tiers:
  basic:
    question_types: [foundation, application]
    difficulties: [1, 2]
    rewards:
      approved: ₹5-15  # Based on quality score
      bonus_for_100_score: ₹5
      streak_bonus: ₹50/week (if 5+ approved daily)
    penalties:
      rejection: -₹1 (from pending balance)
      plagiarism: Account suspension
    
  verified:
    question_types: [foundation, application, cross_concept]
    difficulties: [1, 2, 3]
    rewards:
      approved: ₹20-50
      review_others: ₹2/review
      bonus_for_100_score: ₹10
    
  expert:
    question_types: [all]
    difficulties: [1, 2, 3, 4]
    rewards:
      approved: ₹50-200
      competition_level: ₹200-500
      new_content_rule: ₹1000
      monthly_retainer: ₹5000-15000

quality_multipliers:
  score_90_plus: 1.5x
  score_95_plus: 2.0x
  first_in_concept: 2.0x  # Bonus for filling gaps
  trending_concept: 1.3x  # Concepts students struggle with
```

---

## 6. Quality Control Pipeline

### 6.1 Multi-Stage Validation

```
┌─────────────────────────────────────────────────────────────────────┐
│                     QUALITY PIPELINE                                 │
│                                                                      │
│  STAGE 1: AUTOMATED CHECKS (Instant)                                │
│  ├── Syntax validation (placeholders correct)                       │
│  ├── Number range check (within difficulty bounds)                  │
│  ├── Duplicate detection (fuzzy match against existing)             │
│  └── Spam detection (rate limiting, pattern detection)              │
│                                                                      │
│  STAGE 2: LLM VALIDATION (2-5 seconds)                              │
│  ├── Mathematical correctness                                        │
│  ├── Pedagogical quality                                             │
│  ├── Content rule compliance                                         │
│  └── Generates quality score                                         │
│                                                                      │
│  STAGE 3: PEER REVIEW (For borderline cases: 60-75 score)           │
│  ├── 2 verified contributors must approve                           │
│  ├── Reviewers earn ₹2 per review                                   │
│  └── Disagreements escalated to expert                              │
│                                                                      │
│  STAGE 4: FIELD TESTING (Post-approval)                             │
│  ├── Deployed to 1% of students                                     │
│  ├── Track: completion rate, time, error patterns                   │
│  ├── Auto-flag if: >40% wrong, >2min avg time, complaints          │
│  └── Flagged → Re-review → Fix or remove                            │
│                                                                      │
│  STAGE 5: CONTINUOUS MONITORING                                     │
│  ├── Student feedback button on each question                       │
│  ├── Teacher review queue (monthly)                                 │
│  └── A/B testing new templates vs established ones                  │
└─────────────────────────────────────────────────────────────────────┘
```

### 6.2 LLM Validation Cost

```
Per validation:
├── Input: ~500 tokens (rules + submission)
├── Output: ~200 tokens (JSON response)
├── Total: ~700 tokens
├── Cost: ₹0.5 per validation (DeepSeek)

Monthly (30K submissions):
├── Validations: 30,000
├── LLM cost: ₹15,000/month
└── Per approved template: ₹1 (if 50% approval rate)

COMPARISON: Human reviewer would cost ₹5-10 per review
SAVINGS: 90% cost reduction
```

---

## 7. Platform Architecture

### 7.1 System Design

```
┌─────────────────────────────────────────────────────────────────────┐
│                     CROWDSOURCING PLATFORM                           │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │                    CONTRIBUTOR PORTAL                           ││
│  │  ├── Registration (Aadhaar/Phone verification)                  ││
│  │  ├── Skill assessment (MCQ test for tier placement)            ││
│  │  ├── Dashboard (earnings, submissions, badges)                  ││
│  │  ├── Submission UI (concept selector + template editor)        ││
│  │  └── Wallet (UPI withdrawal, min ₹100)                         ││
│  └─────────────────────────────────────────────────────────────────┘│
│                              │                                       │
│                              ▼                                       │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │                    VALIDATION SERVICE                           ││
│  │  ├── Automated checks (syntax, duplicates, spam)               ││
│  │  ├── LLM validator (DeepSeek API)                              ││
│  │  ├── Peer review queue                                          ││
│  │  └── Score calculator                                           ││
│  └─────────────────────────────────────────────────────────────────┘│
│                              │                                       │
│                              ▼                                       │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │                    TEMPLATE STORE (Notion/DB)                   ││
│  │  ├── Approved templates                                         ││
│  │  ├── Version history                                            ││
│  │  ├── Usage analytics                                            ││
│  │  └── Contributor attribution                                    ││
│  └─────────────────────────────────────────────────────────────────┘│
│                              │                                       │
│                              ▼                                       │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │                    QUESTION ENGINE                              ││
│  │  ├── Template selector (based on concept, difficulty)          ││
│  │  ├── Number generator (reverse construction)                    ││
│  │  ├── Distractor generator                                       ││
│  │  └── Solution step builder                                      ││
│  └─────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────┘
```

### 7.2 Database Schema for Crowdsourcing

```sql
-- Contributors
CREATE TABLE contributors (
    id UUID PRIMARY KEY,
    phone VARCHAR(15) UNIQUE NOT NULL,
    aadhaar_hash VARCHAR(64),  -- For verification
    name VARCHAR(100),
    tier VARCHAR(20) DEFAULT 'basic',  -- basic, verified, expert
    total_submissions INT DEFAULT 0,
    total_approved INT DEFAULT 0,
    approval_rate DECIMAL(5,2),
    total_earnings DECIMAL(10,2) DEFAULT 0,
    wallet_balance DECIMAL(10,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    banned_until TIMESTAMP
);

-- Template Submissions
CREATE TABLE template_submissions (
    id UUID PRIMARY KEY,
    contributor_id UUID REFERENCES contributors(id),
    
    -- Content
    concept_id VARCHAR(128) NOT NULL,
    difficulty INT NOT NULL,
    story_template TEXT NOT NULL,
    solution_template TEXT NOT NULL,
    distractor_templates JSONB NOT NULL,
    
    -- Validation
    status VARCHAR(20) DEFAULT 'pending',  -- pending, validating, approved, rejected
    llm_score JSONB,  -- {mathematical: 95, pedagogical: 88, ...}
    overall_score INT,
    rejection_reason TEXT,
    
    -- Review
    peer_reviews JSONB,  -- [{reviewer_id, approved, comments}]
    expert_review JSONB,
    
    -- Rewards
    reward_amount DECIMAL(10,2),
    reward_paid BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT NOW(),
    validated_at TIMESTAMP,
    approved_at TIMESTAMP
);

-- Approved Templates (Production)
CREATE TABLE approved_templates (
    id UUID PRIMARY KEY,
    submission_id UUID REFERENCES template_submissions(id),
    contributor_id UUID REFERENCES contributors(id),
    
    -- Content (denormalized for fast access)
    concept_id VARCHAR(128) NOT NULL,
    difficulty INT NOT NULL,
    story_template TEXT NOT NULL,
    solution_template TEXT NOT NULL,
    distractor_templates JSONB NOT NULL,
    
    -- Usage stats
    times_used BIGINT DEFAULT 0,
    avg_completion_rate DECIMAL(5,2),
    avg_correct_rate DECIMAL(5,2),
    student_ratings DECIMAL(3,2),
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    flagged BOOLEAN DEFAULT FALSE,
    flag_reason TEXT,
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_templates_concept ON approved_templates(concept_id, difficulty);
CREATE INDEX idx_submissions_status ON template_submissions(status);
CREATE INDEX idx_contributors_tier ON contributors(tier);
```

---

## 8. Gamification & Engagement

### 8.1 Contributor Gamification

```
┌─────────────────────────────────────────────────────────────────────┐
│                     GAMIFICATION FEATURES                            │
│                                                                      │
│  BADGES:                                                            │
│  ├── 🌟 Rising Star: First 10 approved templates                   │
│  ├── 🎯 Sharpshooter: 10 consecutive 90+ scores                    │
│  ├── 📚 Subject Expert: 100 templates in one subject               │
│  ├── 🏆 Top Contributor: Monthly leaderboard winner                │
│  └── 🎓 Mentor: Reviewed 100 peer submissions                      │
│                                                                      │
│  LEADERBOARDS:                                                      │
│  ├── Daily: Top earners today                                      │
│  ├── Weekly: Most approvals this week                              │
│  ├── Monthly: Highest quality scores                               │
│  └── All-time: Total contribution value                            │
│                                                                      │
│  STREAKS:                                                           │
│  ├── 5-day streak: ₹50 bonus                                       │
│  ├── 15-day streak: ₹200 bonus                                     │
│  ├── 30-day streak: ₹500 bonus + tier upgrade consideration        │
│  └── Streak freeze: ₹20 (1 allowed per month)                      │
│                                                                      │
│  REFERRAL PROGRAM:                                                  │
│  ├── Refer a friend: ₹50 when they earn ₹100                       │
│  ├── 5% of referral's earnings (first 3 months)                    │
│  └── Cap: ₹5000/month from referrals                               │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 9. Integration with Existing Architecture

### 9.1 How It Fits

```
┌─────────────────────────────────────────────────────────────────────┐
│                     UNIFIED ARCHITECTURE                             │
│                                                                      │
│  LAYER 4: CROWDSOURCING PLATFORM (NEW)                              │
│  ├── Contributor Portal                                             │
│  ├── LLM Validator                                                  │
│  └── Template Store (feeds into Layer 2)                            │
│                                                                      │
│  LAYER 3: ORCHESTRATOR (existing)                                   │
│  ├── Reads YAML configs                                             │
│  ├── Selects templates from Template Store                         │
│  └── Calls Question Engine                                          │
│                                                                      │
│  LAYER 2: CONTENT CONFIGS (existing + crowdsourced)                 │
│  ├── taxonomy/ (concepts, bloom levels)                             │
│  ├── blueprints/ (coverage, difficulty mix)                         │
│  ├── graphs/ (prerequisites)                                        │
│  └── templates/ (crowdsourced story templates) ← NEW                │
│                                                                      │
│  LAYER 1: QUESTION ENGINE (simplified)                              │
│  ├── Number generator (reverse construction)                        │
│  ├── Template filler                                                │
│  ├── Distractor calculator                                          │
│  └── Solution builder                                               │
└─────────────────────────────────────────────────────────────────────┘
```

### 9.2 Template Store in Notion

Instead of code files, templates live in **Notion**:

```
Notion Workspace: EdTech Content
├── 📚 Concepts (existing YAML → synced to Notion)
├── 📖 Story Templates (crowdsourced)
│   ├── Math / Class 5 / Factors & Multiples / GCD
│   │   ├── Template 1: Ribbon cutting problem
│   │   ├── Template 2: Fruit distribution
│   │   ├── Template 3: Room tiling
│   │   └── ... (50+ templates)
│   └── ...
├── ❌ Distractors (crowdsourced)
├── 📝 Solution Patterns (crowdsourced)
└── 🏆 Competition Questions (expert-curated)
```

---

## 10. Rollout Plan

### Phase 1: Foundation (Month 1-2)
- [ ] Build Contributor Portal MVP
- [ ] Integrate LLM Validator (DeepSeek)
- [ ] Seed with 500 templates (internal team)
- [ ] Pilot with 50 beta contributors

### Phase 2: Scale (Month 3-4)
- [ ] Open registration (Tier 1 only)
- [ ] Target: 1000 contributors, 10K templates
- [ ] Add peer review system
- [ ] Launch gamification

### Phase 3: Quality (Month 5-6)
- [ ] Add field testing pipeline
- [ ] Introduce Tier 2 (verified) contributors
- [ ] Build teacher review dashboard
- [ ] Target: 50K templates

### Phase 4: Competition (Month 7+)
- [ ] Add Tier 3 (expert) program
- [ ] Launch competition-level questions
- [ ] Partner with coaching institutes
- [ ] Target: 100K templates

---

## 11. Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Low-quality spam | Rate limiting + LLM validation + tiered access |
| Plagiarism | Fuzzy duplicate detection + originality score |
| Gaming the system | Randomized review + field testing + user reports |
| LLM hallucination | Conservative thresholds + peer review for borderline |
| Contributor churn | Competitive rewards + gamification + referral program |
| Platform abuse | KYC verification + phone OTP + earnings cap |

---

## 12. Success Metrics

| Metric | Target (6 months) |
|--------|-------------------|
| Active contributors | 5,000 |
| Templates submitted/month | 30,000 |
| Approval rate | 50%+ |
| Avg quality score | 80+ |
| Templates in production | 100,000 |
| Question variations possible | ∞ (infinite) |
| Cost per template | < ₹20 |
| Student satisfaction | > 4.5/5 |

---

## Summary: How This Solves the Bottleneck

```
BEFORE:
├── 5 content writers producing 1,000 questions/month
├── Cost: ₹2.8L/month
├── Output: Finite question bank
└── Problem: Students exhaust questions

AFTER:
├── 5,000 contributors producing 15,000 templates/month
├── Cost: ₹2.65L/month (similar!)
├── Output: Each template = ∞ question variations
├── Quality: LLM-validated, peer-reviewed, field-tested
└── Result: Truly infinite, high-quality question bank

THE MAGIC:
├── Humans provide CREATIVITY (stories, contexts, teaching hints)
├── LLM provides QUALITY CONTROL (validation, scoring)
├── Math engine provides VARIATION (number generation)
└── Together: Infinite high-quality questions at low cost
```

---

*Document End - Ready for Implementation Discussion*
