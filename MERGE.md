# Merging the question map into paper.shrit.in

Everything lives in one folder: `site/features/question-map/`. It has no dependencies beyond
React, Next.js (App Router) and Tailwind, and it styles itself with the shadcn tokens your site
already uses (`bg-background`, `bg-card`, `text-muted-foreground`, `border-border`, `text-primary`).
No CSS file, no new packages, and no changes to your layout, data layer or routes.

Preview it first: `cd site && npm install && npm run dev`, then open
http://localhost:3000/browse/Year%202/Semester%203/CSE/subject/CSS%202101

## Option 1: paste this to Claude Code in your repo

> Merge the "question map" feature from `<path-to>/qp-tagger/site/features/question-map/` into this repo.
> 1. Copy that whole folder to the place this repo keeps feature/UI modules (e.g. `components/question-map/`
>    or `features/question-map/`). Keep the files unchanged, except fix the import alias if this repo doesn't use `@/`.
> 2. In the subject page (the route that renders `/browse/.../subject/<code>`), import
>    `{ QuestionMap, getSubjectTags }` from that folder and, below the list of papers, render:
>    ```tsx
>    const tags = getSubjectTags(subjectCode); // e.g. "CSS 2101"; returns null for untagged subjects
>    {tags && <QuestionMap data={tags} />}
>    ```
>    `QuestionMap` is a client component; the page can stay a server component.
> 3. Check the Tailwind tokens it uses exist here (background, card, muted, muted-foreground, border,
>    primary, primary-foreground). Map them to this repo's names if they differ. Don't add new colors.
> 4. Run the type check and lint, then open the CSS 2101 subject page and confirm the map renders
>    in light and dark mode and that subjects without tags look unchanged.
> Don't modify anything else.

## Option 2: by hand
1. Copy `site/features/question-map/` into your repo.
2. Add the two lines from step 2 above to your subject page.

## Adding subjects later
Tag data comes from the Python pipeline at the repo root (`scrape.py` → `extract.py` → `tag.py` → `export.py`).
`export.py` writes `site/features/question-map/data/<code>.json`; register the file in
`get-subject-tags.ts`. Each paper in the data carries `pdf_path`, the same `/authoritative/...pdf`
path your site serves, if you'd rather join tags to your own paper records.

## What's inside
| File | What it does |
|---|---|
| `question-map.tsx` | Client component: topic frequency bars (filter), difficulty chips, question cards with LeetCode links |
| `get-subject-tags.ts` | `getSubjectTags(code)`: returns the tag data for a subject code, or null |
| `types.ts` | Data types (schema 1) |
| `data/*.json` | Tagged questions per subject |
| `index.ts` | Public exports |

## Per-paper analysis (end-sem papers only)
Each data file (`export/<code>.json`, mirrored in `site/features/question-map/data/`) covers end-sem
papers only. Every paper carries a `summary`: total questions and marks, questions and marks per topic
(most asked first), and the Easy/Medium/Hard split. Subjects: CSS 2101 Data Structures, CSS 1001 PPS,
CSE 1071 PSUC. How to show it on the site is up to you.
