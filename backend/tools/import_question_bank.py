"""Import YAML question bank into Postgres (Option A).

Usage (example):
  python -m tools.import_question_bank --yaml backend/data/class5_chapter5_bank.yaml

Notes:
- This is intended to be run by a developer/admin, not on the student request path.
- Idempotency: based on YAML 'id' key; repeated imports update payload.
"""

from __future__ import annotations

import argparse
import json
import uuid
from pathlib import Path

from sqlalchemy import select

from core.database import SessionLocal
from db.models.question_bank import QuestionBankItem
from services.question_bank_loader import QuestionBank, QuestionConstructor
import yaml


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
    """Map human concept label to curated concept_id.

    Raises ValueError if mapping is missing (we don't want silent drift).
    """
    concept_label = str(concept_label or "").strip()
    if not concept_label:
        raise ValueError("Missing concept label in YAML item")

    concept_map = _load_concept_map()
    subject_map = (concept_map or {}).get("math", {})
    chapter_map = (subject_map or {}).get(str(chapter), {})

    concept_id = (chapter_map or {}).get(concept_label)
    if not concept_id:
        raise ValueError(
            f"No concept_id mapping for chapter='{chapter}' concept='{concept_label}'. "
            f"Add it to backend/data/concept_map.yaml"
        )
    return str(concept_id).strip()


def _infer_concept(question_data: dict, *, chapter: str) -> str:
    # Prefer explicit concept field; map human label -> curated concept_id.
    concept_label = question_data.get("concept")
    if concept_label:
        return _map_concept_to_id(chapter=chapter, concept_label=str(concept_label))
    raise ValueError("Missing concept label in YAML item (required for curated taxonomy)")


def _build_payload(question, raw_data: dict = None) -> dict:
    """Build payload close to what SessionAdapter expects today.
    
    Args:
        question: QuestionConstructor object
        raw_data: Original YAML dict (for rich_content access)
    """
    raw_data = raw_data or {}
    
    # Extract rich_content from raw YAML data (K.C. Nag enriched content)
    rich_content = raw_data.get("rich_content") or {}
    
    # Prioritize rich_content fields over template placeholders
    # rich_content has the actual story/HTML content, while question object may have unfilled {n} placeholders
    rich_narrative = rich_content.get("story_problem") or getattr(question, "rich_narrative", None)
    rich_html_content = rich_content.get("html_content") or getattr(question, "rich_html_content", None)
    
    # Visual hints: prefer rich_content.visual_hint, then question.visual_hints, then solution_steps
    visual_hint_from_rich = rich_content.get("visual_hint")
    visual_hints_from_question = getattr(question, "visual_hints", None)
    solution_steps = getattr(question, "solution_steps", None) or []
    
    if visual_hint_from_rich:
        visual_hints = [visual_hint_from_rich] + solution_steps[:2] if solution_steps else [visual_hint_from_rich]
    elif visual_hints_from_question:
        visual_hints = visual_hints_from_question
    else:
        visual_hints = solution_steps[:3] if solution_steps else None
    
    return {
        "topic": getattr(question, "topic", None),
        "question_text": getattr(question, "question_text", None),
        "question_context": rich_content.get("concept_bridge"),  # Use concept_bridge as context
        "options": [str(o) for o in getattr(question, "options", [])],
        "correct_option_index": int(getattr(question, "correct_option_index", 0) or 0),
        "solution_steps": solution_steps,
        "answer": getattr(question, "answer", None),
        "bloom_level": getattr(getattr(question, "bloom_info", None), "bloom_level", None)
        or getattr(question, "bloom_level", None)
        or None,
        "distractor_info": getattr(question, "distractor_info", None),
        "trap_info": getattr(question, "trap_info", None),
        # Misconception info from batch-generated questions (maps option value → misconception type)
        "misconception_info": raw_data.get("misconception_info"),
        # Rich fields - prioritize enriched content over templates
        "rich_narrative": rich_narrative,
        "rich_html_content": rich_html_content,
        "visual_hints": visual_hints,
        # New K.C. Nag rich content structure (full nested object)
        "rich_content": {
            "story_character": rich_content.get("story_character"),
            "story_setting": rich_content.get("story_setting"),
            "story_problem": rich_content.get("story_problem"),
            "story_action": rich_content.get("story_action"),
            "real_world_relevance": rich_content.get("real_world_relevance"),
            "visual_hint": rich_content.get("visual_hint"),
            "visual_type": rich_content.get("visual_type"),
            "html_content": rich_content.get("html_content"),
            "latex_expression": rich_content.get("latex_expression"),
            "concept_bridge": rich_content.get("concept_bridge"),
            "extension_question": rich_content.get("extension_question"),
            "theme": rich_content.get("theme"),
        } if rich_content else None,
        # allow future schema evolution
        "schema_version": 2,
    }


def import_yaml_bank(yaml_path: Path, chapter: str) -> int:
    bank = QuestionBank(str(yaml_path))

    inserted_or_updated = 0

    with SessionLocal() as db:
        for q_data in bank.get_all_questions():
            try:
                yaml_id = q_data.get("id")
                if not yaml_id:
                    continue

                q_obj = QuestionConstructor.construct_from_yaml(q_data)
                payload = _build_payload(q_obj, raw_data=q_data)

                bloom_level = _normalize_bloom_level(q_data.get("bloom_level"))
                difficulty = int(q_data.get("difficulty", 1) or 1)
                concept = _infer_concept(q_data, chapter=chapter)

                # Keep the original label in payload for UI/debugging if needed
                payload["concept_label"] = str(q_data.get("concept") or "").strip() or None
                payload["concept_id"] = concept

                # Use yaml_id as a stable UUID namespace input to keep ids stable across imports.
                stable_uuid = str(uuid.uuid5(uuid.NAMESPACE_URL, f"qbank:{chapter}:{yaml_id}"))

                existing = db.execute(
                    select(QuestionBankItem).where(QuestionBankItem.id == stable_uuid)
                ).scalar_one_or_none()

                # Extract template_id if present (for batch-generated questions)
                template_id = q_data.get("template_id") or payload.get("template_id")

                if existing:
                    existing.chapter = chapter
                    existing.concept = concept
                    existing.difficulty = difficulty
                    existing.bloom_level = bloom_level
                    existing.source = "yaml"
                    existing.payload = json.loads(json.dumps(payload, default=str))
                    existing.active = True
                    existing.template_id = template_id
                else:
                    item = QuestionBankItem(
                        id=stable_uuid,
                        chapter=chapter,
                        concept=concept,
                        difficulty=difficulty,
                        bloom_level=bloom_level,
                        source="yaml",
                        payload=json.loads(json.dumps(payload, default=str)),
                        active=True,
                        template_id=template_id,
                    )
                    db.add(item)

                inserted_or_updated += 1
            except Exception as e:
                # If anything fails, the transaction can become "aborted" in Postgres.
                # Roll back and continue so a single bad item doesn't poison the whole import.
                try:
                    db.rollback()
                except Exception:
                    pass
                print(f"Skipped YAML id={q_data.get('id')} due to error: {e}")
                continue

        try:
            db.commit()
        except Exception:
            try:
                db.rollback()
            except Exception:
                pass
            raise

    return inserted_or_updated


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--yaml", required=True, help="Path to YAML question bank")
    parser.add_argument(
        "--chapter",
        default="class5_chapter5",
        help="Canonical chapter key used by SessionAdapter/question bank",
    )
    args = parser.parse_args()

    count = import_yaml_bank(Path(args.yaml), chapter=args.chapter)
    print(f"Imported/updated {count} questions into question_bank_items")


if __name__ == "__main__":
    main()
