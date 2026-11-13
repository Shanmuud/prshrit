"""Write the merge-ready data file: export/<subject>.json.

Questions are keyed by the PDF path the site already serves (/authoritative/...pdf),
so the site can join tags to its own paper records without sharing any of its code.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parent
KEEP = ("qno", "text", "marks", "co", "cognitive_level",
        "topic", "subtopic", "difficulty", "leetcode", "reason")


def reflow(text: str) -> str:
    """Join PDF hard-wraps; keep breaks before list items (i., ii), a), -, •), code and blank lines."""
    out: list[str] = []
    for line in text.split("\n"):
        prev = out[-1] if out else ""
        starts_item = re.match(r"^\s*(\(?[ivx]+[.)]|\(?[a-z][.)]|\d+[.)]|[-•*]|struct |void |int |char |bool |\{|\})", line, re.I)
        code_like = re.search(r"[;{}]\s*$", prev)
        if prev and line and not starts_item and not code_like and not prev.endswith((":", ".", "?")):
            out[-1] = prev + " " + line.strip()
        else:
            out.append(line)
    return "\n".join(out)


def main(subject: str = "CSS 2101") -> int:
    papers = json.loads((ROOT / "data/papers.json").read_text(encoding="utf-8"))
    tagged = json.loads((ROOT / "data/tagged.json").read_text(encoding="utf-8"))
    out = {"schema": 1, "subject": subject, "papers": []}
    for p in papers:
        qs = [{k: (reflow(q[k]) if k == "text" else q.get(k)) for k in KEEP} for q in tagged if q["paper_id"] == p["id"]]
        out["papers"].append({
            "pdf_path": unquote(urlparse(p["url"]).path),
            "code": p["code"], "date": p.get("date"), "exam_type": p.get("exam_type"),
            "questions": qs,
        })
    name = subject.lower().replace(" ", "-") + ".json"
    blob = json.dumps(out, indent=2, ensure_ascii=False)
    for dest in (ROOT / "export" / name, ROOT / "site/features/question-map/data" / name):
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(blob, encoding="utf-8")
        print(f"{dest.relative_to(ROOT)}: {sum(len(p['questions']) for p in out['papers'])} questions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(*sys.argv[1:]))
