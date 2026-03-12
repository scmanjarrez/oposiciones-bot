#!/usr/bin/env python3
"""
Preprocess quiz_correct.json into static JSON files for the webapp.

Generates:
  webapp/public/data/meta.json           — blocks, topics, years with question counts
  webapp/public/data/blocks/{block}.json — questions grouped by block (a1..b4)
  webapp/public/data/years/{year}.json   — questions grouped by exam year
"""

import json
import os
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).parent.parent
DATA_FILE = ROOT / "data" / "quiz_correct.json"
OUTPUT_DIR = ROOT / "webapp" / "public" / "data"

BLOCKS = ["A1", "A2", "A3", "A4", "B1", "B2", "B3", "B4"]
GENERAL_TOPICS = set(
    str(i) for i in range(1, 29)
)  # topics 1-28 are "generales"

BLOCK_NAMES = {
    "A1": "Bloque A1 — Organización del Estado",
    "A2": "Bloque A2 — Administración General del Estado",
    "A3": "Bloque A3 — Unión Europea",
    "A4": "Bloque A4 — Régimen jurídico",
    "B1": "Bloque B1 — Tecnologías de la Información",
    "B2": "Bloque B2 — Desarrollo de Sistemas",
    "B3": "Bloque B3 — Sistemas y Comunicaciones",
    "B4": "Bloque B4 — Seguridad y Auditoría",
}

STATUS_ORDER = ["VIGENTE", "DESFASADA", "DEROGADA", "ERRÓNEA"]


def load_questions():
    print(f"Loading {DATA_FILE}…")
    with open(DATA_FILE, encoding="utf-8") as f:
        raw = json.load(f)
    # raw can be a dict (id → question) or a list
    if isinstance(raw, dict):
        questions = list(raw.values())
    else:
        questions = raw
    print(f"  Loaded {len(questions)} questions")
    return questions


def slugify_block(block: str) -> str:
    return block.lower()  # "A1" → "a1"


def main():
    questions = load_questions()

    # Index by block
    by_block: dict[str, list] = defaultdict(list)
    # Index by year
    by_year: dict[str, list] = defaultdict(list)
    # Collect topics per block
    topics_per_block: dict[str, set] = defaultdict(set)

    for q in questions:
        block = q.get("block", "").upper()
        year = q.get("year", "")
        topic = str(q.get("topic", ""))

        if block in BLOCKS:
            by_block[block].append(q)
            if topic:
                topics_per_block[block].add(topic)

        if year:
            by_year[year].append(q)

    # ------------------------------------------------------------------
    # Write block files
    # ------------------------------------------------------------------
    blocks_dir = OUTPUT_DIR / "blocks"
    blocks_dir.mkdir(parents=True, exist_ok=True)

    blocks_meta = []
    for block in BLOCKS:
        qs = by_block[block]
        slug = slugify_block(block)

        # Sort questions: VIGENTE first, then by topic, then by year
        qs_sorted = sorted(
            qs,
            key=lambda q: (
                STATUS_ORDER.index(q.get("status", "VIGENTE"))
                if q.get("status") in STATUS_ORDER
                else 99,
                int(q.get("topic", 0))
                if str(q.get("topic", "")).isdigit()
                else 0,
                q.get("year", ""),
            ),
        )

        out_path = blocks_dir / f"{slug}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(qs_sorted, f, ensure_ascii=False, separators=(",", ":"))
        print(f"  Wrote {out_path.name} ({len(qs_sorted)} questions)")

        # Topic metadata for this block
        topics_in_block = sorted(
            topics_per_block[block],
            key=lambda t: int(t) if t.isdigit() else 0,
        )
        topics_meta = []
        for t in topics_in_block:
            topic_qs = [q for q in qs if str(q.get("topic", "")) == t]
            count_by_status = {
                s: sum(1 for q in topic_qs if q.get("status") == s)
                for s in STATUS_ORDER
            }
            topics_meta.append(
                {
                    "id": t,
                    "isGeneral": t in GENERAL_TOPICS,
                    "count": len(topic_qs),
                    "countByStatus": count_by_status,
                }
            )

        count_by_status_block = {
            s: sum(1 for q in qs_sorted if q.get("status") == s)
            for s in STATUS_ORDER
        }
        blocks_meta.append(
            {
                "id": block,
                "slug": slug,
                "name": BLOCK_NAMES.get(block, block),
                "count": len(qs_sorted),
                "countByStatus": count_by_status_block,
                "topics": topics_meta,
            }
        )

    # ------------------------------------------------------------------
    # Write year files
    # ------------------------------------------------------------------
    years_dir = OUTPUT_DIR / "years"
    years_dir.mkdir(parents=True, exist_ok=True)

    years_meta = []
    for year in sorted(by_year.keys()):
        qs = by_year[year]
        qs_sorted = sorted(
            qs,
            key=lambda q: (
                q.get("block", ""),
                int(q.get("topic", 0))
                if str(q.get("topic", "")).isdigit()
                else 0,
            ),
        )
        out_path = years_dir / f"{year}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(qs_sorted, f, ensure_ascii=False, separators=(",", ":"))
        print(f"  Wrote {out_path.name} ({len(qs_sorted)} questions)")
        count_by_status_year = {
            s: sum(1 for q in qs_sorted if q.get("status") == s)
            for s in STATUS_ORDER
        }
        years_meta.append(
            {
                "id": year,
                "count": len(qs_sorted),
                "countByStatus": count_by_status_year,
            }
        )

    # ------------------------------------------------------------------
    # Write meta.json
    # ------------------------------------------------------------------
    meta = {
        "blocks": blocks_meta,
        "years": years_meta,
        "totals": {
            "questions": len(questions),
            "generalTopics": len(GENERAL_TOPICS),
            "examGeneralCount": 30,
            "examSpecificCount": 100,
            "examPassScore": 45.5,
            "examDurationSeconds": 7200,
        },
    }
    meta_path = OUTPUT_DIR / "meta.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f"  Wrote {meta_path}")

    print("\nDone! Generated files in:", OUTPUT_DIR)


if __name__ == "__main__":
    main()
