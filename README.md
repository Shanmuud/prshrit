# qp-tagger

Tags every question in MIT Manipal past papers (from [paper.shrit.in](https://paper.shrit.in)) with a
**topic** (Stack, Queue, Singly LL, Doubly LL, Trees, Graphs, ...), a **LeetCode-style difficulty**
(Easy / Medium / Hard, an estimate of the exam task, not an official rating) and **similar LeetCode problems**.

First subject: Data Structures, CSS 2101 (and old code CSE 2122): 3 papers, 45 questions.

## Preview it

```
cd site
npm install
npm run dev
```
Open http://localhost:3000. It shows the CSS 2101 subject page with the question map under the paper list.

## For the site author: merging

The feature is one self-contained folder, `site/features/question-map/`, written for the same stack as
paper.shrit.in (Next.js App Router, Tailwind, shadcn tokens). Copy it in and add two lines to the
subject page. **`MERGE.md` has a ready-to-paste prompt for Claude Code.** Your site's code never
needs to come into this repo.

## Pipeline (to add more subjects)

```
python scrape.py "<subject page url>"   # PDFs -> data/pdfs/, data/papers.json
python extract.py                       # -> data/questions.json  (pypdf layout mode)
python tag.py                           # -> data/tagged.json     (claude -p + RUBRIC.md)
python export.py "CSS 2101"             # -> site/features/question-map/data/ + export/
python build_page.py                    # -> web/index.html       (standalone preview page)
```

- Questions that are images in the PDF are typed in by hand in `data/overrides.json`.
- `RUBRIC.md` holds the topic taxonomy, difficulty rules and the LeetCode catalogue the tagger may use.

## What's not in this repo
The PDFs themselves (`data/pdfs/`) are not committed. They belong to the archive; `scrape.py` re-downloads them.
