#!/usr/bin/env python3
"""Tag questions with topic, difficulty, and LeetCode refs via claude -p + RUBRIC.md."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
DEFAULT_RUBRIC = ROOT / "RUBRIC.md"

FALLBACK_RUBRIC = """# Data Structures tagging rubric (fallback until RUBRIC.md exists)

Tag each exam question with:
- **topic**: one of Linked List, Doubly Linked List, Stack, Queue, Trees, BST, AVL, Graph, Sparse Matrix, General DS, C Programming
- **subtopic**: short phrase (e.g. "AVL deletion rotations", "queue in array")
- **difficulty**: Easy | Medium | Hard (LeetCode-style, for a sophomore DS course)
- **leetcode**: 0–2 similar problems as objects `{ "id": number, "title": string, "slug": string }` (empty array if none fit)
- **reason**: one sentence why

Output **only** a JSON array. Each element must include `id` (question id from input) plus the fields above.
"""


def load_rubric(path: Path) -> str:
    if path.is_file():
        return path.read_text(encoding="utf-8")
    return FALLBACK_RUBRIC


def load_questions(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_papers(path: Path) -> dict[str, dict]:
    papers = json.loads(path.read_text(encoding="utf-8"))
    return {p["id"]: p for p in papers}


def group_by_paper(questions: list[dict]) -> dict[str, list[dict]]:
    groups: dict[str, list[dict]] = {}
    for q in questions:
        groups.setdefault(q["paper_id"], []).append(q)
    for pid in groups:
        groups[pid].sort(key=lambda x: (int(re.match(r"(\d+)", x["qno"]).group(1)), x["qno"]))
    return groups


def extract_json_array(text: str) -> list[dict]:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1:
        raise ValueError("No JSON array in model output")
    return json.loads(text[start : end + 1])


REQUIRED_TAG_FIELDS = ("topic", "subtopic", "difficulty", "leetcode", "reason")
VALID_DIFFICULTY = {"Easy", "Medium", "Hard"}


def validate_tags(tags: list[dict], expected_ids: set[str]) -> list[dict]:
    seen: set[str] = set()
    out: list[dict] = []
    for row in tags:
        qid = row.get("id")
        if not qid or qid not in expected_ids:
            continue
        if qid in seen:
            continue
        if row.get("difficulty") not in VALID_DIFFICULTY:
            raise ValueError(f"Invalid difficulty for {qid}: {row.get('difficulty')}")
        if not isinstance(row.get("leetcode"), list):
            raise ValueError(f"leetcode must be a list for {qid}")
        for f in REQUIRED_TAG_FIELDS:
            if f not in row:
                raise ValueError(f"Missing field {f} for {qid}")
        seen.add(qid)
        out.append(row)
    missing = expected_ids - seen
    if missing:
        raise ValueError(f"Model omitted question ids: {sorted(missing)}")
    return out


def run_claude(prompt: str, rubric: str) -> str:
    full_prompt = f"{rubric}\n\n---\n\n{prompt}"
    # Prompt goes over stdin: Windows caps argv near 32K chars, and UTF-8 keeps symbols intact.
    proc = subprocess.run(
        ["claude", "-p", "--output-format", "text"],
        input=full_prompt,
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=ROOT,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or "claude -p failed")
    return proc.stdout


def build_paper_prompt(paper: dict, questions: list[dict]) -> str:
    payload = [
        {
            "id": q["id"],
            "qno": q["qno"],
            "marks": q["marks"],
            "co": q.get("co"),
            "text": q["text"],
        }
        for q in questions
    ]
    return (
        f"Paper: {paper.get('code')} · {paper.get('date')} · {paper.get('exam_type')}\n"
        f"Subject: {paper.get('title')}\n\n"
        f"Tag every question below. Return a JSON array with one object per question id.\n\n"
        f"{json.dumps(payload, indent=2)}"
    )


def merge_tagged(questions: list[dict], tag_rows: list[dict]) -> list[dict]:
    by_id = {r["id"]: r for r in tag_rows}
    merged: list[dict] = []
    for q in questions:
        row = dict(q)
        t = by_id[q["id"]]
        for k in REQUIRED_TAG_FIELDS:
            row[k] = t[k]
        merged.append(row)
    return merged


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--questions",
        default=str(DATA_DIR / "questions.json"),
    )
    parser.add_argument(
        "--papers",
        default=str(DATA_DIR / "papers.json"),
    )
    parser.add_argument(
        "--rubric",
        default=str(DEFAULT_RUBRIC),
    )
    parser.add_argument(
        "-o",
        "--output",
        default=str(DATA_DIR / "tagged.json"),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print batch sizes only; do not call claude",
    )
    args = parser.parse_args(argv)

    rubric = load_rubric(Path(args.rubric))
    questions = load_questions(Path(args.questions))
    papers = load_papers(Path(args.papers))
    groups = group_by_paper(questions)

    if args.dry_run:
        for pid, qs in groups.items():
            print(f"{pid}: {len(qs)} questions")
        return 0

    all_tags: list[dict] = []
    for paper_id, qs in groups.items():
        paper = papers.get(paper_id, {"id": paper_id})
        prompt = build_paper_prompt(paper, qs)
        for attempt in (1, 2):
            try:
                raw = run_claude(prompt, rubric)
                tags = validate_tags(extract_json_array(raw), {q["id"] for q in qs})
                break
            except (ValueError, RuntimeError) as e:
                if attempt == 2:
                    raise
                print(f"Retrying {paper_id}: {e}")
        all_tags.extend(tags)
        print(f"Tagged {len(tags)} questions for paper {paper_id}")

    tagged = merge_tagged(questions, all_tags)
    out = Path(args.output)
    out.write_text(json.dumps(tagged, indent=2), encoding="utf-8")
    print(f"Wrote {len(tagged)} tagged questions to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
