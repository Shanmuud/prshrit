#!/usr/bin/env python3
"""Pull the question text out of an answer-key PDF (question, solution and marks in one table).

The line parser in extract.py can't read these: each question's label sits beside the
solution, not the question. This sends the layout text to `claude -p` and asks for the
questions alone, as the same rows extract.py writes. Usage:
    extract_key.py <papers.json> <paper_id> <questions.json>   (appends/replaces that paper's rows)
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from extract import layout_lines

ROOT = Path(__file__).resolve().parent

PROMPT = """Below is the layout text of an exam answer key. Each question has a label (1A, 1B, ... 5C),
its marks, a course outcome (CO) number and a competency level (1-6), the question text, then "Sol:"
and a solution, sometimes followed by "Evaluation Scheme". The label often sits on a line in the
middle of the solution rather than beside the question.

Return ONLY a JSON array, one object per question, in order:
{"qno": "1A", "text": "<the question exactly as set, without the solution or evaluation scheme>",
 "marks": <int>, "co": "CO<n>"}
Keep sub-parts (i), ii)) and any code or data the question supplies. Do not include any solution text.

---
"""


def main(papers_path: str, paper_id: str, out_path: str) -> int:
    paper = next(p for p in json.loads(Path(papers_path).read_text(encoding="utf-8")) if p["id"] == paper_id)
    text = "\n".join(layout_lines(ROOT / paper["file"]))
    proc = subprocess.run(["claude", "-p", "--output-format", "text"], input=PROMPT + text,
                          capture_output=True, text=True, encoding="utf-8", cwd=ROOT)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr or proc.stdout)
    raw = proc.stdout
    rows = json.loads(raw[raw.find("["): raw.rfind("]") + 1])
    out = Path(out_path)
    existing = [q for q in json.loads(out.read_text(encoding="utf-8")) if q["paper_id"] != paper_id] if out.exists() else []
    for r in rows:
        existing.append({"id": f"{paper_id}-{r['qno']}", "paper_id": paper_id, "qno": r["qno"], "text": r["text"].strip(),
                         "marks": r.get("marks"), "co": r.get("co"), "cognitive_level": None, "from_key": True})
    out.write_text(json.dumps(existing, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"{paper['code']} {paper.get('date')}: {len(rows)} questions from the answer key")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(*sys.argv[1:]))
