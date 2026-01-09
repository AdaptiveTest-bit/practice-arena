"""Seed concept_catalog from backend/data/concept_map.yaml.

Run:
  python -m tools.seed_concepts --chapter class5_chapter5 --grade 5 --subject math

Notes:
- Idempotent upsert.
- order_index is derived from the numeric suffix in concept_id (C001..).
"""

from __future__ import annotations

import argparse
import re

import yaml
from sqlalchemy import select

from core.database import SessionLocal
from db.models.concepts import ConceptCatalog


_CONCEPT_ID_RE = re.compile(r".*_C(\d{3})$")


def _load_map() -> dict:
    from pathlib import Path

    path = Path(__file__).resolve().parents[1] / "data" / "concept_map.yaml"
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _order_index_from_concept_id(concept_id: str) -> int:
    m = _CONCEPT_ID_RE.match(str(concept_id))
    if not m:
        return 0
    return int(m.group(1))


def seed(*, subject: str, chapter_key: str, grade_level: int) -> int:
    mapping = _load_map()
    chapter_map = (((mapping or {}).get(subject) or {}).get(chapter_key) or {})

    if not chapter_map:
        raise ValueError(f"No concepts found for subject={subject} chapter_key={chapter_key}")

    upserted = 0

    with SessionLocal() as db:
        for display_name, concept_id in chapter_map.items():
            concept_id = str(concept_id).strip()
            display_name = str(display_name).strip()
            order_index = _order_index_from_concept_id(concept_id)

            existing = db.execute(
                select(ConceptCatalog).where(ConceptCatalog.concept_id == concept_id)
            ).scalar_one_or_none()

            if existing:
                existing.subject = subject
                existing.grade_level = int(grade_level)
                existing.chapter_key = chapter_key
                existing.order_index = int(order_index)
                existing.display_name = display_name
                existing.active = True
            else:
                db.add(
                    ConceptCatalog(
                        concept_id=concept_id,
                        subject=subject,
                        grade_level=int(grade_level),
                        chapter_key=chapter_key,
                        order_index=int(order_index),
                        display_name=display_name,
                        description=None,
                        active=True,
                    )
                )
            upserted += 1

        db.commit()

    return upserted


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--subject", default="math")
    parser.add_argument("--chapter", dest="chapter_key", default="class5_chapter5")
    parser.add_argument("--grade", dest="grade_level", type=int, default=5)
    args = parser.parse_args()

    count = seed(subject=args.subject, chapter_key=args.chapter_key, grade_level=args.grade_level)
    print(f"Seeded/updated {count} concepts into concept_catalog")


if __name__ == "__main__":
    main()
