# qp-tagger — spec (lead: Claude)

Goal: for MIT Manipal past papers on https://paper.shrit.in, show **which topic each question is on**
(Linked List, DLL, Stack, Queue, Trees, AVL, ...) and a **LeetCode-style difficulty** (Easy/Medium/Hard),
plus a similar LeetCode problem where one fits. First subject: Data Structures (CSS 2101 / old code CSE 2122).

## Source
- Subject page: https://paper.shrit.in/browse/Year%202/Semester%203/CSE/subject/CSS%202101
- Server-rendered Next.js HTML; PDF links are in the HTML as paths starting `/authoritative/...pdf`
  (prefix with https://paper.shrit.in). PDFs are text (pypdf extracts cleanly).
- Questions look like `1A)` ... text ... `(5)` marks ... `Course Outcome: "CO4" / Cognitive Level: "Analysis"`.

## Pipeline (Python 3.12, pypdf + requests already installed)
1. `scrape.py <subject-page-url>` -> downloads PDFs to `data/pdfs/`, writes `data/papers.json`
   `[{id, code, title, date, exam_type, url, file}]`
2. `extract.py` -> `data/questions.json`
   `[{id: "<paper_id>-1A", paper_id, qno: "1A", text, marks, co, cognitive_level}]`
   Keep text faithful (join broken lines, keep lists/keys). Marks often appear as `(5)` on a separate/odd line.
3. `tag.py` -> `data/tagged.json` = questions + `{topic, subtopic, difficulty, leetcode: [{id, title, slug}], reason}`
   Uses `claude -p` (non-interactive) with the rubric in `RUBRIC.md`, batched per paper, JSON output, validated.
4. Frontend `web/index.html` (lead builds): filter by topic/difficulty/paper, topic frequency counts.

## Rules for helpers
- Never ask the user anything. If blocked, pick the most reasonable default, note it, keep going, and report to the lead via `hc send`.
- Pre-authorized: pip install, running scripts, network fetches to paper.shrit.in.
- Stay in this folder. Don't start other agents.
