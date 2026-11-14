# qp-tagger: notes for Claude

This repo adds a **question map** to paper.shrit.in: every past-paper question tagged by topic,
LeetCode-style difficulty and similar LeetCode problems.

- If you're asked to **merge this into paper.shrit.in**, follow `MERGE.md` exactly. Copy only
  `site/features/question-map/`, add the two marked lines to the subject page, and change nothing else.
- To **preview** it: `cd site && npm install && npm run dev`.
- To **tag a new subject**, run the Python pipeline at the root: `scrape.py <subject-page-url>`, then
  `extract.py`, `tag.py` and `export.py "<CODE>" [data dir] [codes]`. Keep each subject in its own data folder
  (`-o data/<name>/papers.json` etc.; DS uses `data/`, PPS/PSUC use `data/programming/`), and use the subject's
  rubric (`RUBRIC.md` for DS, `RUBRIC-programming.md` for first-year C). Answer-key PDFs go through `extract_key.py`. Then register the new JSON in
  `site/features/question-map/get-subject-tags.ts`. Questions that are images in the PDF go in
  `data/overrides.json`. Tagging rules are in `RUBRIC.md`.
- Difficulty is an estimate of the exam task in LeetCode terms, not an official rating. LeetCode
  picks must come from the catalogue in the subject's rubric.
