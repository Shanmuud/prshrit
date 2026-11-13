"""Inline data/papers.json + data/tagged.json into web/template.html -> web/index.html."""
import json, pathlib, sys

root = pathlib.Path(__file__).parent
papers = json.loads((root / "data/papers.json").read_text(encoding="utf-8"))
questions = json.loads((root / "data/tagged.json").read_text(encoding="utf-8"))
data = {
    "subject": sys.argv[1] if len(sys.argv) > 1 else "Data Structures",
    "subject_short": "DS Question Map",
    "eyebrow": "MIT Manipal · CSE · Sem 3 · CSS 2101",
    "papers": papers,
    "questions": questions,
}
blob = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
html = (root / "web/template.html").read_text(encoding="utf-8").replace("/*DATA*/", blob)
(root / "web/index.html").write_text(html, encoding="utf-8")
print(f"web/index.html: {len(papers)} papers, {len(questions)} questions")
