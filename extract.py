"""Extract questions from downloaded papers -> data/questions.json.

Uses pypdf's layout mode, which keeps each question label (1A), its text and its
marks "(5)" on the same visual line. The default mode scrambles the order on
these MAHE papers. Questions that are images in the PDF are filled from
data/overrides.json ({question_id: text}).
(Cursor's first version, which used the default mode, is kept in extract_cursor_v1.py.)
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"

LABEL = re.compile(r"^\s*([1-9][A-Z])\)\s*(.*)$")
MARKS_END = re.compile(r"\s*\((\d{1,2})\)\s*$")
CO_LINE = re.compile(r'Course Outcome:\s*"?(CO\d)"?\s*/\s*Cognitive Level:\s*"?([A-Za-z]+)"?')
NOISE = [
    re.compile(r"about:srcdoc"),
    re.compile(r"^\s*\d+\s+of\s+\d+\s*$"),
    re.compile(r"^\s*(CSE|CSS)[ _]\d{4}\s*$"),
    re.compile(r"^\s*Page #\d+\s*$"),
    re.compile(r"^\s*\d+ of \d+\s+\d{2}-\d{2}-\d{4}"),
]
END = re.compile(r"-+\s*End\s*-+", re.I)


def layout_lines(path: Path) -> list[str]:
    reader = PdfReader(str(path))
    lines: list[str] = []
    for page in reader.pages:
        lines.extend(page.extract_text(extraction_mode="layout").splitlines())
    return lines


def is_noise(line: str) -> bool:
    return any(p.search(line) for p in NOISE)


def tidy(line: str) -> str:
    return re.sub(r"[ \t]{2,}", " ", line).strip()


def extract_questions(path: Path) -> list[dict]:
    questions: list[dict] = []
    cur: dict | None = None

    def flush() -> None:
        if cur is None:
            return
        body = "\n".join(cur["lines"]).strip()
        body = re.sub(r"\n{3,}", "\n\n", body)
        questions.append({"qno": cur["qno"], "text": body, "marks": cur["marks"],
                          "co": cur["co"], "cognitive_level": cur["level"]})

    for raw in layout_lines(path):
        if END.search(raw):
            break  # CO / cognitive-level summary tables follow
        if is_noise(raw):
            continue
        m = LABEL.match(raw)
        if m:
            flush()
            cur = {"qno": m.group(1), "lines": [], "marks": None, "co": None, "level": None}
            raw = m.group(2)
        if cur is None:
            continue  # paper header before 1A
        co = CO_LINE.search(raw)
        if co:
            cur["co"], cur["level"] = co.group(1), co.group(2)
            continue
        mk = MARKS_END.search(raw)
        if mk and cur["marks"] is None:
            cur["marks"] = int(mk.group(1))
            raw = raw[: mk.start()]
        line = tidy(raw)
        if line or (cur["lines"] and cur["lines"][-1]):
            cur["lines"].append(line)
    flush()
    return questions


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--papers", default=str(DATA_DIR / "papers.json"))
    ap.add_argument("--overrides", default=str(DATA_DIR / "overrides.json"))
    ap.add_argument("-o", "--output", default=str(DATA_DIR / "questions.json"))
    args = ap.parse_args(argv)

    papers = json.loads(Path(args.papers).read_text(encoding="utf-8"))
    ov_path = Path(args.overrides)
    overrides = json.loads(ov_path.read_text(encoding="utf-8")) if ov_path.exists() else {}

    out: list[dict] = []
    for paper in papers:
        qs = extract_questions(ROOT / paper["file"])
        for q in qs:
            qid = f"{paper['id']}-{q['qno']}"
            if qid in overrides:
                q["text"] = overrides[qid]
                q["from_image"] = True
            out.append({"id": qid, "paper_id": paper["id"], **q})
        empty = [q["qno"] for q in qs if len(q["text"]) < 25 and not q.get("from_image")]
        print(f"{paper['code']} {paper.get('date')}: {len(qs)} questions"
              + (f"  (short/empty, check: {empty})" if empty else ""))

    Path(args.output).write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {len(out)} questions -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
