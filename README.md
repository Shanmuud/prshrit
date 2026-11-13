# qp-tagger

Tags every question in MIT Manipal past papers (from [paper.shrit.in](https://paper.shrit.in)) with a
**topic** (Stack, Queue, Singly LL, Doubly LL, Trees, Graphs, ...), a **LeetCode-style difficulty**
(Easy / Medium / Hard, an estimate of the exam task, not an official rating) and **similar LeetCode problems**.

First subject: Data Structures, CSS 2101 (and old code CSE 2122): 3 papers, 45 questions.

## For the site author: how to merge

This repo never needs your site's code. It only produces a data file keyed by the PDF paths your
site already serves, plus one optional React component.

**Option A: just the data (2 minutes)**
1. Copy `export/css-2101.json` into your repo (e.g. `data/tags/css-2101.json`).
2. Each paper has `pdf_path` (e.g. `/authoritative/MIT 2021-26/.../CSS-2101-Data Structures.pdf`),
   the same path behind your "Open" links. Join on that and render however you like.
   Types are in `integration/types.ts`.

**Option B: data + ready-made component**
1. Copy `integration/TopicMap.tsx` and `integration/types.ts` into your components folder.
2. On the subject page:
   ```tsx
   import TopicMap from "@/components/TopicMap";
   import tags from "@/data/tags/css-2101.json";
   <TopicMap data={tags} />
   ```
   React only, no other dependencies, inline styles (no CSS clashes). It's a client component.

**Option C: keep it in sync**
`git subtree add --prefix=vendor/qp-tagger <this-repo-url> main --squash`, then later
`git subtree pull ...` to get new subjects. Your history stays yours; nothing flows back.

## Pipeline (to add more subjects)

```
python scrape.py "<subject page url>"   # PDFs -> data/pdfs/, data/papers.json
python extract.py                       # -> data/questions.json  (pypdf layout mode)
python tag.py                           # -> data/tagged.json     (claude -p + RUBRIC.md)
python export.py "CSS 2101"             # -> export/css-2101.json (merge-ready)
python build_page.py                    # -> web/index.html       (standalone preview page)
```

- Questions that are images in the PDF are typed in by hand in `data/overrides.json`.
- `RUBRIC.md` holds the topic taxonomy, difficulty rules and the LeetCode catalogue the tagger may use.

## What's not in this repo
The PDFs themselves (`data/pdfs/`) are not committed. They belong to the archive; `scrape.py` re-downloads them.
