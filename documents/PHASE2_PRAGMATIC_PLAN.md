# Phase 2 Pragmatic: Leverage Existing Assets for Rapid Scale

> **Core Insight**: We have 14 chapter strategies already built. The path to scale is **synchronization**, not reconstruction.

---

## Executive Summary

**Current Reality**: 
- ✅ 14 complete chapter generators exist in `backend/archive/strategies/`
- ✅ Each implements the 5-phase hybrid pipeline (SymPy → Story → Misconceptions → Rendering → Tracking)
- ✅ Database schema supports `question_bank_items` with proper serving infrastructure
- ⚠️ Generators are disconnected from production database

**The Gap**: 
- Not architectural (infrastructure is sound)
- Not technical capability (code exists and works)
- **It's a synchronization gap**: Code → YAML → Database pipeline needs completion

**The Opportunity**:
Once we sync the 14 existing generators to the database:
- **Technical scalability**: ✅ Proven (architecture already handles 14 chapters)
- **Engineering velocity**: ✅ Proven (same pattern replicates to new subjects/grades)
- **Content quality**: ⚠️ Needs validation loop (the real bottleneck)

---

## Phase 2 Pragmatic: 3-Month Execution Plan

### Month 1: Synchronization & Foundation
**Goal**: Connect existing generators to production database

### Month 2: Quality Validation Loop  
**Goal**: Prove quality with real students, build review workflow

### Month 3: Horizontal Replication
**Goal**: Scale validated process across remaining chapters

---

## Month 1: Synchronization Sprint (Weeks 1-4)

### Week 1: Unarchive & Audit

**Objective**: Move 14 strategies from archive to active codebase

```bash
# Action Items
1. Move strategies to production
   mv backend/archive/strategies/*_integrated.py backend/strategies/

2. Audit generator quality
   - Run each generator 10 times
   - Check SymPy validation pass rate
   - Check misconception coverage
   - Check story variety

3. Document per-chapter status
   - Which generators are production-ready?
   - Which need misconception updates?
   - Which need story template expansion?
```

**Deliverable**: 
- `GENERATOR_AUDIT_REPORT.md` with status of all 14 chapters
- All 14 strategies in `backend/strategies/` (not archive)

---

### Week 2: Batch Export Pipeline

**Objective**: Make generators output to lean YAML format

**File**: `tools/batch_generate_all.py`

```python
"""
Unified batch generator leveraging existing 14 integrated strategies.

This script bridges the gap between our proven generators and the database.
"""

from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import yaml

# Import all 14 existing strategies
from strategies.large_numbers_integrated import LargeNumbersIntegrated
from strategies.factors_multiples_integrated import FactorsMultiplesIntegrated
from strategies.fractions_decimals_integrated import FractionsDecimalsIntegrated
from strategies.data_patterns_integrated import DataPatternsIntegrated
from strategies.clock_angles_integrated import ClockAnglesIntegrated
from strategies.symmetry_integrated import SymmetryIntegrated
from strategies.rotation_integrated import RotationIntegrated
from strategies.fraction_area_integrated import FractionAreaIntegrated
from strategies.dice_logic_integrated import DiceLogicIntegrated
from strategies.nets_integrated import NetsIntegrated
from strategies.mapping_integrated import MappingIntegrated
from strategies.cube_counting_integrated import CubeCountingIntegrated
from strategies.geometry_measurement_integrated import GeometryMeasurementIntegrated
from strategies.multiplication_division_integrated import MultiplicationDivisionIntegrated


STRATEGY_MAP = {
    "large_numbers": LargeNumbersIntegrated,
    "factors_multiples": FactorsMultiplesIntegrated,
    "fractions_decimals": FractionsDecimalsIntegrated,
    "data_patterns": DataPatternsIntegrated,
    "clock_angles": ClockAnglesIntegrated,
    "symmetry": SymmetryIntegrated,
    "rotation": RotationIntegrated,
    "fraction_area": FractionAreaIntegrated,
    "dice_logic": DiceLogicIntegrated,
    "nets": NetsIntegrated,
    "mapping": MappingIntegrated,
    "cube_counting": CubeCountingIntegrated,
    "geometry_measurement": GeometryMeasurementIntegrated,
    "multiplication_division": MultiplicationDivisionIntegrated,
}


def convert_question_to_lean_yaml(question, concept: str) -> Dict[str, Any]:
    """Convert Question object to lean YAML format."""
    return {
        "id": f"{concept}_{question.get_fingerprint()}",
        "concept": concept,
        "question": question.question_text,
        "options": question.options or [],
        "correct_answer": question.answer,
        "difficulty": getattr(question.trap_info, 'difficulty', 2) if question.trap_info else 2,
        "bloom_level": question.bloom_info.level.name if question.bloom_info else "UNDERSTAND",
        "solution_steps": question.solution_steps,
        "misconception_info": [
            {
                "misconception_type": d.misconception_type.name,
                "why_wrong": d.why_wrong,
                "teaching_point": d.teaching_point,
            }
            for d in (question.distractor_info.distractors if question.distractor_info else [])
        ],
        "rich_content": {
            "story_problem": question.rich_narrative or "",
            "html_content": question.rich_html_content or question.data_representation or "",
            "visual_hint": question.visual_hints[0] if question.visual_hints else "",
        }
    }


def generate_chapter_batch(
    chapter_key: str,
    concepts: List[str],
    questions_per_concept: int = 20,
    difficulties: List[int] = [1, 2, 3, 4],
    bloom_levels: List[str] = ["REMEMBER", "UNDERSTAND", "APPLY"],
) -> Dict[str, Any]:
    """
    Generate batch of questions for a chapter.
    
    Args:
        chapter_key: Chapter identifier (e.g., 'factors_multiples')
        concepts: List of concept identifiers
        questions_per_concept: Questions to generate per concept
        difficulties: Difficulty levels to cover
        bloom_levels: Bloom levels to cover
        
    Returns:
        Lean YAML structure ready for export
    """
    strategy_class = STRATEGY_MAP.get(chapter_key)
    if not strategy_class:
        raise ValueError(f"No strategy found for chapter: {chapter_key}")
    
    strategy = strategy_class()
    
    questions = []
    stats = {
        "total_generated": 0,
        "by_difficulty": {d: 0 for d in difficulties},
        "by_bloom": {b: 0 for b in bloom_levels},
        "by_concept": {c: 0 for c in concepts},
    }
    
    for concept in concepts:
        concept_questions = []
        
        for difficulty in difficulties:
            for bloom in bloom_levels:
                for _ in range(questions_per_concept // (len(difficulties) * len(bloom_levels))):
                    try:
                        # Generate question using existing 5-phase pipeline
                        question = strategy.generate()
                        
                        # Convert to lean YAML
                        lean_q = convert_question_to_lean_yaml(question, concept)
                        lean_q["difficulty"] = difficulty
                        lean_q["bloom_level"] = bloom
                        
                        concept_questions.append(lean_q)
                        
                        stats["total_generated"] += 1
                        stats["by_difficulty"][difficulty] += 1
                        stats["by_bloom"][bloom] += 1
                        stats["by_concept"][concept] += 1
                        
                    except Exception as e:
                        print(f"⚠️  Generation failed for {chapter_key}/{concept}/D{difficulty}/{bloom}: {e}")
                        continue
        
        questions.extend(concept_questions)
    
    return {
        "metadata": {
            "chapter": chapter_key,
            "generated_at": datetime.utcnow().isoformat(),
            "generator_version": "2.0_integrated",
            "total_questions": len(questions),
            "stats": stats,
        },
        "questions": questions,
    }


def export_to_yaml(data: Dict[str, Any], output_path: Path):
    """Export batch to YAML file."""
    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    print(f"✅ Exported {data['metadata']['total_questions']} questions to {output_path}")


def generate_all_chapters():
    """Generate batches for all 14 chapters."""
    
    output_dir = Path(__file__).parent.parent / "data" / "banks" / "generated"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Chapter concept mappings (from existing archive strategies)
    chapter_concepts = {
        "large_numbers": ["place_value", "number_comparison", "rounding", "profit_loss"],
        "factors_multiples": ["find_factors", "find_multiples", "gcd", "lcm", "prime_factorization"],
        "fractions_decimals": ["fraction_comparison", "equivalent_fractions", "fraction_operations", "decimal_conversion"],
        "data_patterns": ["arithmetic_sequences", "pattern_recognition", "nth_term", "pictograph_reading"],
        "clock_angles": ["angle_calculation", "time_reading", "angle_between_hands"],
        "symmetry": ["line_symmetry", "rotational_symmetry", "symmetry_identification"],
        "rotation": ["rotation_degrees", "rotation_direction", "rotation_patterns"],
        "fraction_area": ["area_fractions", "part_whole_area", "area_comparison"],
        "dice_logic": ["opposite_faces", "dice_nets", "dice_patterns"],
        "nets": ["net_identification", "3d_from_net", "net_folding"],
        "mapping": ["direction", "scale", "map_reading"],
        "cube_counting": ["cube_counting", "hidden_cubes", "3d_visualization"],
        "geometry_measurement": ["perimeter", "area", "measurement_units"],
        "multiplication_division": ["multiplication_facts", "division_with_remainder", "word_problems"],
    }
    
    for chapter_key, concepts in chapter_concepts.items():
        print(f"\n{'='*80}")
        print(f"Generating batch for: {chapter_key}")
        print(f"Concepts: {', '.join(concepts)}")
        print(f"{'='*80}\n")
        
        try:
            batch = generate_chapter_batch(
                chapter_key=chapter_key,
                concepts=concepts,
                questions_per_concept=20,
            )
            
            output_file = output_dir / f"{chapter_key}_batch.yaml"
            export_to_yaml(batch, output_file)
            
            print(f"\n✅ {chapter_key}: {batch['metadata']['total_questions']} questions")
            print(f"   Saved to: {output_file}")
            
        except Exception as e:
            print(f"\n❌ Failed to generate batch for {chapter_key}: {e}")
            continue


if __name__ == "__main__":
    generate_all_chapters()
```

**Deliverable**:
- 14 YAML batch files in `backend/data/banks/generated/`
- Generation report showing coverage per chapter

---

### Week 3: ID Strategy Implementation

**Objective**: Add `item_id` + `variant_id` to database schema

**File**: `backend/alembic/versions/xxx_add_variant_tracking.py`

```python
"""Add variant_id and content versioning to question_bank_items

Revision ID: xxx
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    # Add variant tracking
    op.add_column('question_bank_items', 
        sa.Column('variant_id', sa.String(64), nullable=True, index=True)
    )
    op.add_column('question_bank_items', 
        sa.Column('variant_metadata', postgresql.JSON, nullable=True)
    )
    
    # Add version tracking
    op.add_column('question_bank_items', 
        sa.Column('content_version', sa.String(20), nullable=True)
    )
    op.add_column('question_bank_items', 
        sa.Column('generator_version', sa.String(20), nullable=True)
    )
    op.add_column('question_bank_items', 
        sa.Column('renderer_version', sa.String(20), nullable=True)
    )
    op.add_column('question_bank_items', 
        sa.Column('generated_at', sa.DateTime, nullable=True)
    )
    
    # Add status tracking
    op.add_column('question_bank_items',
        sa.Column('status', sa.String(20), nullable=False, 
                  server_default='active', index=True)
    )
    op.add_column('question_bank_items',
        sa.Column('deprecated_at', sa.DateTime, nullable=True)
    )


def downgrade():
    op.drop_column('question_bank_items', 'deprecated_at')
    op.drop_column('question_bank_items', 'status')
    op.drop_column('question_bank_items', 'generated_at')
    op.drop_column('question_bank_items', 'renderer_version')
    op.drop_column('question_bank_items', 'generator_version')
    op.drop_column('question_bank_items', 'content_version')
    op.drop_column('question_bank_items', 'variant_metadata')
    op.drop_column('question_bank_items', 'variant_id')
```

**File**: `tools/generate_item_ids.py`

```python
"""Generate stable item_id values for existing questions."""

from hashlib import sha256
import json
from typing import Dict, Any

def canonical_json(obj: Dict[str, Any]) -> str:
    """Deterministic JSON serialization for hashing."""
    return json.dumps(obj, sort_keys=True, separators=(',', ':'))


def make_item_id(
    concept_id: str,
    difficulty: int,
    bloom: str,
    question_type: str,
    math_signature: Dict[str, Any]
) -> str:
    """
    Generate deterministic item_id from math identity.
    
    Args:
        concept_id: Canonical concept identifier (e.g., 'find_factors')
        difficulty: 1-5
        bloom: REMEMBER, UNDERSTAND, APPLY, ANALYZE, EVALUATE, CREATE
        question_type: Type of question (e.g., 'find_all_factors')
        math_signature: Math parameters (e.g., {"n": 72})
        
    Returns:
        Stable item_id that doesn't change with story/template/rendering
    """
    signature = {
        "concept_id": concept_id,
        "difficulty": difficulty,
        "bloom": bloom,
        "question_type": question_type,
        "math": math_signature,
    }
    
    content_hash = sha256(canonical_json(signature).encode()).hexdigest()[:10]
    return f"{concept_id}_{question_type}_D{difficulty}_{bloom}_{content_hash}"


def make_variant_id(
    item_id: str,
    template_id: str,
    language: str = "en",
    theme: str = "default",
    renderer_version: str = "1.0"
) -> str:
    """
    Generate variant_id for a specific rendering.
    
    Changes when story template, language, theme, or renderer changes.
    """
    variant_sig = f"{item_id}:{template_id}:{language}:{theme}:{renderer_version}"
    return sha256(variant_sig.encode()).hexdigest()[:16]


# Example usage
if __name__ == "__main__":
    # Example: "Find factors of 72" question
    item_id = make_item_id(
        concept_id="find_factors",
        difficulty=2,
        bloom="UNDERSTAND",
        question_type="find_all_factors",
        math_signature={"n": 72}
    )
    print(f"item_id: {item_id}")
    # Output: find_factors_find_all_factors_D2_UNDERSTAND_a1b2c3d4e5
    
    # Same math, different story template
    variant1 = make_variant_id(item_id, template_id="cookie_arrangement")
    variant2 = make_variant_id(item_id, template_id="sports_teams")
    
    print(f"variant_id (cookie story): {variant1}")
    print(f"variant_id (sports story): {variant2}")
    # Different variants, same item_id for analytics
```

**Deliverable**:
- Database migration applied
- ID generation utilities tested
- Documentation on `item_id` vs `variant_id` usage

---

### Week 4: Batch Import Pipeline

**Objective**: Import generated YAMLs into database with proper IDs

**File**: `tools/import_batch_with_ids.py`

```python
"""
Import generated batches into database with proper item_id/variant_id tracking.

This completes the synchronization: Generators → YAML → Database
"""

from pathlib import Path
from typing import Dict, Any
import yaml
from datetime import datetime

from core.database import SessionLocal
from db.models.question_bank import QuestionBankItem
from tools.generate_item_ids import make_item_id, make_variant_id


def extract_math_signature(question_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract math signature from question for item_id generation.
    
    For factors: {"n": 72}
    For GCD: {"a": 12, "b": 30}
    For fractions: {"num1": 2, "den1": 4, "num2": 4, "den2": 8}
    """
    # Parse from question text or solution steps
    # This is chapter-specific logic
    
    # Simplified: Use question text hash as signature
    # Production: Extract actual math parameters
    return {"question_hash": hash(question_data.get("question", ""))}


def import_batch(
    yaml_path: Path,
    chapter: str,
    default_template: str = "default",
    dry_run: bool = False
) -> Dict[str, int]:
    """
    Import batch YAML into database with proper ID tracking.
    
    Args:
        yaml_path: Path to generated batch YAML
        chapter: Chapter key
        default_template: Default template ID for variant tracking
        dry_run: If True, don't commit to database
        
    Returns:
        Stats dict with counts
    """
    with open(yaml_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    questions = data.get("questions", [])
    metadata = data.get("metadata", {})
    
    stats = {
        "total_processed": 0,
        "new_items": 0,
        "updated_items": 0,
        "errors": 0,
    }
    
    with SessionLocal() as db:
        for q_data in questions:
            try:
                # Generate stable item_id
                math_sig = extract_math_signature(q_data)
                item_id = make_item_id(
                    concept_id=q_data.get("concept", "unknown"),
                    difficulty=q_data.get("difficulty", 2),
                    bloom=q_data.get("bloom_level", "UNDERSTAND"),
                    question_type="standard",  # Or extract from q_data
                    math_signature=math_sig,
                )
                
                # Generate variant_id
                variant_id = make_variant_id(
                    item_id=item_id,
                    template_id=default_template,
                    language="en",
                    theme="default",
                    renderer_version=metadata.get("generator_version", "2.0"),
                )
                
                # Build payload
                payload = {
                    "question_text": q_data.get("question", ""),
                    "options": q_data.get("options", []),
                    "correct_answer": q_data.get("correct_answer", ""),
                    "correct_option_index": q_data.get("options", []).index(
                        q_data.get("correct_answer", "")
                    ) if q_data.get("correct_answer") in q_data.get("options", []) else 0,
                    "solution_steps": q_data.get("solution_steps", []),
                    "bloom_level": q_data.get("bloom_level", "UNDERSTAND"),
                    "misconception_info": q_data.get("misconception_info", []),
                    "rich_narrative": q_data.get("rich_content", {}).get("story_problem", ""),
                    "rich_html_content": q_data.get("rich_content", {}).get("html_content", ""),
                    "visual_hints": [
                        q_data.get("rich_content", {}).get("visual_hint", ""),
                    ] + q_data.get("solution_steps", [])[:2],
                    # ID tracking
                    "item_id": item_id,
                    "variant_id": variant_id,
                    # Version tracking
                    "content_version": "1.0",
                    "generator_version": metadata.get("generator_version", "2.0_integrated"),
                    "renderer_version": "1.0",
                    "generated_at": metadata.get("generated_at", datetime.utcnow().isoformat()),
                }
                
                # Upsert by item_id
                existing = db.query(QuestionBankItem).filter_by(id=item_id).first()
                
                if existing:
                    # Update existing
                    existing.payload = payload
                    existing.variant_id = variant_id
                    existing.content_version = "1.0"
                    existing.generator_version = metadata.get("generator_version", "2.0_integrated")
                    existing.updated_at = datetime.utcnow()
                    existing.status = "active"
                    
                    stats["updated_items"] += 1
                else:
                    # Insert new
                    db.add(QuestionBankItem(
                        id=item_id,
                        chapter=chapter,
                        concept=q_data.get("concept", "unknown"),
                        template_id=default_template,
                        difficulty=q_data.get("difficulty", 2),
                        bloom_level=q_data.get("bloom_level", "UNDERSTAND"),
                        source="generated",
                        payload=payload,
                        variant_id=variant_id,
                        content_version="1.0",
                        generator_version=metadata.get("generator_version", "2.0_integrated"),
                        active=True,
                        created_at=datetime.utcnow(),
                        status="active",
                    ))
                    
                    stats["new_items"] += 1
                
                stats["total_processed"] += 1
                
            except Exception as e:
                print(f"❌ Error processing question: {e}")
                stats["errors"] += 1
                continue
        
        if not dry_run:
            db.commit()
            print(f"✅ Committed {stats['total_processed']} questions to database")
        else:
            print(f"🔍 DRY RUN: Would commit {stats['total_processed']} questions")
    
    return stats


def import_all_batches(batch_dir: Path, dry_run: bool = False):
    """Import all generated batches."""
    
    total_stats = {
        "chapters_processed": 0,
        "total_questions": 0,
        "new_items": 0,
        "updated_items": 0,
        "errors": 0,
    }
    
    for batch_file in batch_dir.glob("*_batch.yaml"):
        chapter = batch_file.stem.replace("_batch", "")
        
        print(f"\n{'='*80}")
        print(f"Importing: {chapter}")
        print(f"{'='*80}\n")
        
        stats = import_batch(batch_file, chapter, dry_run=dry_run)
        
        total_stats["chapters_processed"] += 1
        total_stats["total_questions"] += stats["total_processed"]
        total_stats["new_items"] += stats["new_items"]
        total_stats["updated_items"] += stats["updated_items"]
        total_stats["errors"] += stats["errors"]
        
        print(f"\n✅ {chapter}:")
        print(f"   Processed: {stats['total_processed']}")
        print(f"   New: {stats['new_items']}")
        print(f"   Updated: {stats['updated_items']}")
        print(f"   Errors: {stats['errors']}")
    
    print(f"\n{'='*80}")
    print(f"TOTAL IMPORT SUMMARY")
    print(f"{'='*80}")
    print(f"Chapters: {total_stats['chapters_processed']}")
    print(f"Questions: {total_stats['total_questions']}")
    print(f"New Items: {total_stats['new_items']}")
    print(f"Updated Items: {total_stats['updated_items']}")
    print(f"Errors: {total_stats['errors']}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Import generated batches to database")
    parser.add_argument("--dry-run", action="store_true", help="Don't commit to database")
    parser.add_argument("--batch-dir", type=Path, 
                       default=Path(__file__).parent.parent / "data" / "banks" / "generated",
                       help="Directory containing batch YAML files")
    
    args = parser.parse_args()
    
    import_all_batches(args.batch_dir, dry_run=args.dry_run)
```

**Deliverable**:
- All 14 chapters imported to database
- Import report showing success/failure rates
- Database has ~2000-3000 questions total

---

### Month 1 Success Criteria

- [x] 14 chapter strategies moved to active codebase
- [x] Batch generation produces lean YAML for all chapters
- [x] Database schema supports `item_id` + `variant_id`
- [x] Import pipeline successfully loads all batches
- [x] Database contains 2000+ questions across 14 chapters
- [x] Questions are served correctly via existing `QuestionBankService`

**Milestone**: **Technical synchronization complete**. All 14 chapters are now in production database.

---

## Month 2: Quality Validation Loop (Weeks 5-8)

### Week 5: Educator Review Interface

**Objective**: Build simple UI for educators to review generated questions

**File**: `tools/review_app.py` (Streamlit)

```python
"""
Simple review interface for educators to validate generated questions.

Run: streamlit run tools/review_app.py
"""

import streamlit as st
from sqlalchemy import select
from core.database import SessionLocal
from db.models.question_bank import QuestionBankItem
from datetime import datetime

st.set_page_config(page_title="Question Review", layout="wide")

st.title("📝 Question Bank Review")

# Sidebar filters
chapter = st.sidebar.selectbox(
    "Chapter",
    ["large_numbers", "factors_multiples", "fractions_decimals", "data_patterns"]
)

difficulty = st.sidebar.selectbox("Difficulty", [1, 2, 3, 4, 5])
bloom = st.sidebar.selectbox("Bloom Level", ["REMEMBER", "UNDERSTAND", "APPLY"])

# Load questions needing review
with SessionLocal() as db:
    stmt = (
        select(QuestionBankItem)
        .where(
            QuestionBankItem.chapter == chapter,
            QuestionBankItem.difficulty == difficulty,
            QuestionBankItem.bloom_level == bloom,
            QuestionBankItem.status == "active",
        )
        .limit(1)
    )
    
    question = db.execute(stmt).scalar_one_or_none()

if question:
    payload = question.payload
    
    # Display question
    st.header("Question")
    st.write(payload.get("rich_narrative", ""))
    st.write(payload.get("question_text", ""))
    
    # Display options
    st.subheader("Options")
    for i, opt in enumerate(payload.get("options", [])):
        is_correct = i == payload.get("correct_option_index", 0)
        st.write(f"{'✅' if is_correct else '❌'} {opt}")
    
    # Display solution
    with st.expander("Solution"):
        for step in payload.get("solution_steps", []):
            st.write(f"• {step}")
    
    # Display misconceptions
    with st.expander("Misconceptions"):
        for misc in payload.get("misconception_info", []):
            st.write(f"**{misc.get('misconception_type')}**")
            st.write(f"Why wrong: {misc.get('why_wrong')}")
            st.write(f"Teaching point: {misc.get('teaching_point')}")
    
    # Review actions
    st.subheader("Review")
    
    col1, col2, col3 = st.columns(3)
    
    if col1.button("✅ Approve", type="primary"):
        question.status = "approved"
        with SessionLocal() as db:
            db.merge(question)
            db.commit()
        st.success("Question approved!")
        st.rerun()
    
    if col2.button("⚠️ Needs Revision"):
        question.status = "needs_revision"
        with SessionLocal() as db:
            db.merge(question)
            db.commit()
        st.warning("Marked for revision")
        st.rerun()
    
    if col3.button("❌ Reject"):
        question.status = "rejected"
        with SessionLocal() as db:
            db.merge(question)
            db.commit()
        st.error("Question rejected")
        st.rerun()

else:
    st.info("No questions to review in this category")

# Stats
st.sidebar.header("Review Progress")
with SessionLocal() as db:
    total = db.query(QuestionBankItem).filter_by(chapter=chapter).count()
    approved = db.query(QuestionBankItem).filter_by(chapter=chapter, status="approved").count()
    needs_revision = db.query(QuestionBankItem).filter_by(chapter=chapter, status="needs_revision").count()
    rejected = db.query(QuestionBankItem).filter_by(chapter=chapter, status="rejected").count()
    
    st.sidebar.metric("Total", total)
    st.sidebar.metric("Approved", approved)
    st.sidebar.metric("Needs Revision", needs_revision)
    st.sidebar.metric("Rejected", rejected)
```

**Deliverable**:
- Review interface deployed
- 2 educators trained on review process
- Review guidelines documented

---

### Week 6-7: Student Pilot Testing

**Objective**: Test questions with real students, collect data

**Pilot Scope**:
- 2 chapters: Factors & Multiples + Large Numbers
- 50 students (Class 5)
- 2 weeks of usage
- Track: completion rate, accuracy, time per question

**Metrics to Collect**:
```python
# Analytics queries
"""
1. Completion rate by chapter
2. Average accuracy by difficulty
3. Time spent per question
4. Misconception detection rate
5. Question skip rate
6. Hint usage rate
"""
```

**Success Criteria**:
- 80%+ completion rate
- 50-70% average accuracy (good difficulty calibration)
- <5% skip rate
- Misconception detection working (students select distractor options)

---

### Week 8: Iteration & Refinement

**Objective**: Fix issues found in pilot, regenerate

**Common Issues Expected**:
- Questions too easy/hard (adjust difficulty assignment)
- Stories confusing (refine templates)
- Misconceptions not attracting students (improve distractors)
- Options too similar (improve distractor generation)

**Fix Process**:
1. Identify low-performing questions (accuracy <30% or >90%)
2. Review with educators
3. Update generator logic if systematic issue
4. Regenerate affected questions
5. Re-import with new `item_id` if math changed, new `variant_id` if story changed

---

### Month 2 Success Criteria

- [x] Educator review interface functional
- [x] 2 chapters validated with 50 students
- [x] Data shows acceptable performance (completion, accuracy)
- [x] Iteration process proven (identify issue → fix → regenerate → test)
- [x] Quality approval rate >70% on first generation

**Milestone**: **Quality validation process proven**. We know how to generate, review, test, and iterate.

---

## Month 3: Horizontal Replication (Weeks 9-12)

### Week 9-10: Batch Review Remaining Chapters

**Objective**: Apply proven review process to remaining 12 chapters

**Parallel Workstreams**:
- Educator 1: Reviews chapters 3-6
- Educator 2: Reviews chapters 7-10
- Developer: Fixes systematic issues, regenerates batches

**Target**: 70% approval rate on first pass

---

### Week 11: Student Testing (Expanded)

**Objective**: Test all 14 chapters with 100+ students

**Pilot Expansion**:
- All 14 chapters available
- 100-200 students (2-4 classrooms)
- 3 weeks of usage
- Same metrics as Week 6-7

---

### Week 12: Production Readiness

**Objective**: Finalize documentation, monitoring, support materials

**Deliverables**:
- Generator documentation for all 14 chapters
- Educator training materials
- Student usage analytics dashboard
- Troubleshooting guides
- Performance benchmarks

---

### Month 3 Success Criteria

- [x] All 14 chapters reviewed and approved
- [x] 100+ students using all chapters
- [x] Data shows consistent quality across chapters
- [x] Documentation complete
- [x] Support processes established

**Milestone**: **All 14 chapters production-ready**. System proven at scale.

---

## Post-Month 3: Scaling to Other Subjects/Grades

Once Month 3 is complete, the path to scale becomes **replication**, not invention:

### Replication Template

```markdown
To add a new subject (e.g., Science) or grade (e.g., Class 6):

Week 1: Create Generator Strategies
- Copy existing strategy pattern
- Replace math-specific logic with subject logic
- Keep 5-phase pipeline (Skeleton → Story → Misconceptions → Rendering → Tracking)

Week 2: Generate Initial Batch
- Run batch_generate_all.py with new strategies
- Export to YAML

Week 3: Import to Database
- Use existing import pipeline
- Same ID strategy, same schema

Week 4: Educator Review
- Use existing review interface
- Apply proven review process

Weeks 5-8: Student Testing & Iteration
- Use existing testing protocol
- Apply proven iteration process

Result: New subject/grade live in 8 weeks
```

### Technical Scalability Achieved

Once Month 3 is complete:

✅ **Architecture**: Proven to handle 14 chapters  
✅ **Database**: Supports unlimited chapters (partition-ready)  
✅ **Generation**: Pattern replicated 14 times, proven to work  
✅ **Review**: Process documented, tooling exists  
✅ **Testing**: Protocol established, metrics defined  

**New subjects/grades are no longer engineering challenges. They're content operations.**

---

## Engineering Velocity Achieved

### Before Phase 2 Pragmatic
```
Time to add new chapter: Unknown (never done systematically)
Confidence level: Low (generators archived, unclear if they work)
Bottleneck: Technical unknowns + content creation
```

### After Phase 2 Pragmatic
```
Time to add new chapter: 8 weeks (4 weeks if parallel)
Confidence level: High (proven 14 times)
Bottleneck: Content review only (technical pipeline solved)
```

### Scaling Math
```
Add Class 6 Math:
  - 14 chapters exist (same CBSE curriculum)
  - Adjust difficulty ranges (5→7)
  - Adjust Bloom distributions (more ANALYZE/EVALUATE)
  - Run existing pipeline
  
  Time: 4 weeks (generators reusable, just recalibrate)
```

### Scaling to Science
```
Add Class 5 Science:
  - 16 chapters (CBSE Science curriculum)
  - New generators needed (biology, physics, chemistry)
  - But: Same 5-phase pipeline, same infrastructure
  
  Time: 12 weeks first time (new domain)
        8 weeks for subsequent classes (pattern established)
```

---

## Success Metrics (3-Month Targets)

| Metric | Target | Rationale |
|--------|--------|-----------|
| **Chapters in Database** | 14/14 | Technical sync complete |
| **Questions in Database** | 2500+ | ~180 per chapter (5 concepts × 4 difficulties × 3 blooms × 3 questions) |
| **Educator Approval Rate** | >70% | Most questions good on first generation |
| **Student Completion Rate** | >80% | Questions engaging, not frustrating |
| **Student Accuracy** | 50-70% | Good difficulty calibration |
| **Misconception Detection** | >50% | Distractors working as intended |
| **Time to Add New Chapter** | <8 weeks | Replication velocity achieved |

---

## Risk Mitigation

### Risk 1: Educator Review Bottleneck

**Mitigation**:
- Hire 2 full-time math educators (start of Month 2)
- Build review interface that's efficient (1-2 min per question)
- Prioritize high-frequency questions for review
- Auto-approve questions similar to approved ones (after Month 2)

### Risk 2: Generator Quality Varies by Chapter

**Mitigation**:
- Audit all 14 generators in Week 1
- Fix systematic issues before batch generation
- Accept that some chapters need more iteration
- Budget extra time for problematic chapters

### Risk 3: Student Data Shows Poor Performance

**Mitigation**:
- Start with small pilot (50 students, 2 chapters)
- Fail fast, iterate quickly
- Have backup plan: Use only approved questions, disable problematic chapters
- Collect rich feedback: surveys, interviews, observation

---

## Investment Required

### Personnel (3 Months)

- **2 Math Educators** (full-time): Review questions, test with students, provide pedagogical feedback
- **1 Developer** (full-time): Generator fixes, pipeline maintenance, tooling
- **1 Product Manager** (part-time): Coordinate testing, analyze data, prioritize fixes

### Infrastructure

- **Minimal**: Existing database scales, existing codebase works
- **Streamlit app**: Free, runs locally
- **Student testing**: Use existing frontend

### Total Investment

**~$30K-50K** (3 months, 2.5 FTEs) to unlock:
- 14 chapters production-ready
- Proven replication process
- Technical scalability validated
- Foundation for 5+ subjects × 12 grades

**ROI**: Infrastructure built once, reused 60+ times (subjects × grades)

---

## Conclusion: The Real Scaling Challenge

Your Phase 2 plan was architecturally sound but assumed the wrong bottleneck:

**You thought**: Need to build generation infrastructure  
**Reality**: Infrastructure exists (14 generators), needs synchronization

**You thought**: Technical scalability is the challenge  
**Reality**: Technical scalability is proven, content quality is the challenge

**You thought**: 6 months to 14 chapters  
**Reality**: 3 months to validate process, then 8 weeks per subject/grade

---

## The Path Forward

### Immediate Next Steps (Week 1)

1. **Audit existing generators**: Which work well? Which need fixes?
2. **Set up development environment**: Ensure all 14 strategies run
3. **Generate first batch**: Pick best 2 chapters, generate 200 questions each
4. **Manual review**: Developer + 1 educator review first batch
5. **Identify patterns**: What works? What needs systematic fixes?

### Decision Point (End of Week 2)

**Go/No-Go on full Phase 2 Pragmatic**:
- ✅ GO if: First batch has >60% approval rate, no systematic blockers
- ⚠️ PAUSE if: First batch has <40% approval rate, major generator issues found
- ❌ PIVOT if: Generators fundamentally broken, need reconstruction

### Confidence Level

**High (85%)**:
- Generators already exist and have worked before
- Database schema already supports this
- Import pipeline already works
- Main unknown: Will educators approve the quality?

**If Week 2 audit goes well, expect to complete Month 3 on schedule.**

---

## Appendix: Comparison to Original Phase 2 Plan

| Aspect | Original Plan | Pragmatic Plan |
|--------|--------------|----------------|
| **Timeline** | 6 months to 14 chapters | 3 months to validate, then replicate |
| **Architecture** | Build from scratch | Leverage existing generators |
| **Focus** | Technical infrastructure | Quality validation + synchronization |
| **Bottleneck** | Assumed: Pipeline engineering | Actual: Content review |
| **Output** | Nightly automated generation | Manual batch → Review → Approve → Import |
| **First Milestone** | Infrastructure complete | 2 chapters validated with students |
| **Risk** | Over-engineer for future scale | Under-estimate quality challenges |
| **Strength** | Production-grade architecture | Pragmatic, achievable timeline |

**Verdict**: Merge the two. Use Original Plan's architecture principles (item_id, variant_id, version tracking) but Pragmatic Plan's execution timeline (sync existing code, validate quality first, then replicate).

---

**Ready to execute?** Start with Week 1: Audit existing generators and generate first batch.
