"""Import lean YAML question bank directly into Postgres.

Usage:
  cd backend
  ./venv/bin/python3 -m tools.import_lean_bank --yaml data/large_numbers_lean.yaml --chapter large_numbers

This script handles the flat lean YAML format directly without going through QuestionBank.
"""

from __future__ import annotations

import argparse
import json
import uuid
from pathlib import Path
from typing import Dict, Any, List

import yaml
from sqlalchemy import select

from core.database import SessionLocal
from db.models.question_bank import QuestionBankItem


def _normalize_bloom_level(raw: str) -> str:
    if not raw:
        return "UNDERSTAND"
    return str(raw).strip().upper()


def _load_concept_map() -> dict:
    """Load curated concept taxonomy mapping."""
    path = Path(__file__).resolve().parents[1] / "data" / "concept_map.yaml"
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _map_concept_to_id(*, chapter: str, concept_label: str) -> str:
    """Map human concept label to curated concept_id."""
    concept_label = str(concept_label or "").strip()
    if not concept_label:
        return "unknown"

    concept_map = _load_concept_map()
    subject_map = (concept_map or {}).get("math", {})
    chapter_map = (subject_map or {}).get(str(chapter), {})

    concept_id = (chapter_map or {}).get(concept_label)
    if not concept_id:
        # Fallback: use concept label directly
        return concept_label
    return str(concept_id).strip()


def _option_id_from_index(i: int) -> str:
    # 0->A, 1->B, 2->C, 3->D (and beyond if ever needed)
    try:
        return chr(ord("A") + int(i))
    except Exception:
        return str(i)


def _normalize_misconception_info(
    *,
    misconception_info: object,
    options: list[str],
) -> list[dict]:
    """Normalize misconception_info to include stable option identifiers.

    Current detection in several places historically matched by raw option string.
    We instead attach:
      - option_index: int
      - option_id: "A"|"B"|"C"|"D"

    We preserve existing fields (type/value/why_wrong/teaching_point/etc.).
    """
    if not isinstance(misconception_info, list):
        return []

    out: list[dict] = []
    normalized_options = [str(o) for o in (options or [])]

    for entry in misconception_info:
        if not isinstance(entry, dict):
            # Unknown entry shape: skip rather than corrupting payload
            continue

        value = entry.get("value")
        # Try to resolve index by matching string value
        option_index = None
        if value is not None:
            v_str = str(value)
            for i, opt in enumerate(normalized_options):
                if str(opt) == v_str:
                    option_index = i
                    break

        # Allow explicit option_index/option_id from YAML if present
        if option_index is None and entry.get("option_index") is not None:
            try:
                option_index = int(entry.get("option_index"))
            except Exception:
                option_index = None

        option_id = entry.get("option_id")
        if not option_id and option_index is not None:
            option_id = _option_id_from_index(option_index)

        normalized = dict(entry)
        if option_index is not None:
            normalized["option_index"] = option_index
        if option_id is not None:
            normalized["option_id"] = str(option_id)

        out.append(normalized)

    return out


def _build_payload(q_data: Dict[str, Any]) -> dict:
    """Build payload from lean question data."""
    rich_content = q_data.get("rich_content") or {}

    # Map options to find correct index
    options = q_data.get("options", [])
    correct_answer = q_data.get("correct_answer", "")
    correct_index = 0
    for i, opt in enumerate(options):
        if str(opt) == str(correct_answer):
            correct_index = i
            break

    # Extract misconception info and normalize it with stable option ids
    raw_misconception_info = q_data.get("misconception_info") or []
    misconception_info = _normalize_misconception_info(
        misconception_info=raw_misconception_info,
        options=[str(o) for o in options],
    )

    solution_steps = q_data.get("solution_steps", [])
    visual_hint = rich_content.get("visual_hint", "")

    # Stable ids for downstream matching (no string comparisons needed)
    option_ids = [_option_id_from_index(i) for i in range(len(options or []))]

    return {
        "question_text": q_data.get("question", ""),
        "question_context": None,
        "options": [str(o) for o in options],
        "option_ids": option_ids,
        "correct_option_index": correct_index,
        "correct_option_id": _option_id_from_index(correct_index),
        "solution_steps": solution_steps,
        "answer": correct_answer,
        "bloom_level": q_data.get("bloom_level", "UNDERSTAND"),
        "misconception_info": misconception_info,
        # Rich fields - check both top-level and nested locations
        "rich_narrative": rich_content.get("story_problem", ""),
        "rich_html_content": q_data.get("rich_html_content", rich_content.get("html_content", "")),
        "visual_hints": q_data.get("visual_hints") or ([visual_hint] + solution_steps[:2] if visual_hint else solution_steps[:3]),
        # Simplified rich_content (only what's used)
        "rich_content": rich_content if rich_content else None,
        "concept_label": q_data.get("concept", ""),
        "yaml_id": q_data.get("id", ""),  # Store original YAML ID for reference
        "schema_version": 4,  # Lean format version (option ids + index-based misconception tags)
    }


def import_lean_yaml(yaml_path: Path, chapter: str) -> int:
    """Import lean YAML file to database."""
    
    with open(yaml_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    questions = data.get("questions", [])
    if not isinstance(questions, list):
        raise ValueError("Lean YAML must have 'questions' as a flat list")
    
    inserted_or_updated = 0
    errors = []
    
    with SessionLocal() as db:
        for q_data in questions:
            try:
                yaml_id = q_data.get("id")
                if not yaml_id:
                    continue
                
                payload = _build_payload(q_data)
                
                bloom_level = _normalize_bloom_level(q_data.get("bloom_level"))
                difficulty = int(q_data.get("difficulty", 1) or 1)
                concept_label = q_data.get("concept", "")
                concept_id = _map_concept_to_id(chapter=chapter, concept_label=concept_label)
                
                payload["concept_id"] = concept_id
                
                # Check if exists by looking in payload for yaml_id
                # Use a deterministic UUID based on yaml_id for idempotency
                deterministic_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, yaml_id))
                
                stmt = select(QuestionBankItem).where(QuestionBankItem.id == deterministic_uuid)
                existing = db.execute(stmt).scalar_one_or_none()
                
                if existing:
                    # Update
                    existing.chapter = chapter
                    existing.concept = concept_id
                    existing.bloom_level = bloom_level
                    existing.difficulty = difficulty
                    existing.payload = payload
                else:
                    # Insert
                    item = QuestionBankItem(
                        id=deterministic_uuid,
                        chapter=chapter,
                        concept=concept_id,
                        bloom_level=bloom_level,
                        difficulty=difficulty,
                        payload=payload,
                        source="yaml",
                    )
                    db.add(item)
                
                inserted_or_updated += 1
                
            except Exception as e:
                errors.append(f"Error on {q_data.get('id', 'unknown')}: {e}")
        
        db.commit()
    
    if errors:
        print(f"⚠️  {len(errors)} errors:")
        for err in errors[:5]:
            print(f"   - {err}")
        if len(errors) > 5:
            print(f"   ... and {len(errors) - 5} more")
    
    return inserted_or_updated


def main():
    parser = argparse.ArgumentParser(description="Import lean YAML to database")
    parser.add_argument("--yaml", required=True, help="Path to lean YAML file")
    parser.add_argument("--chapter", required=True, help="Chapter key (e.g., large_numbers)")
    args = parser.parse_args()
    
    yaml_path = Path(args.yaml)
    if not yaml_path.exists():
        print(f"❌ File not found: {yaml_path}")
        return
    
    print(f"📄 Importing: {yaml_path}")
    count = import_lean_yaml(yaml_path, chapter=args.chapter)
    print(f"✅ Imported {count} questions to chapter '{args.chapter}'")


if __name__ == "__main__":
    main()
