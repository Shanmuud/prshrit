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

## Update: CSS 2103 Data Analytics and the module map

If you already merged the question map, **re-copy `site/features/question-map/` over your copy. No page changes are
needed.** Your existing two lines already render CSS 2103 through `getSubjectTags`.

What changed inside the folder:
- `data/css-2103.json` holds the 30 questions from the two CSS 2103 end-sem papers (Regular Nov/Dec 2025 and
  Makeup Dec 2025/Jan 2026). Each is tagged with a module and a topic. No answers are included.
- `get-subject-tags.ts` registers `"CSS 2103"`.
- `types.ts` gains optional fields only: `module`, `method`, `approach`, `text_html`, and a top-level `modules` list.
  `difficulty`, `reason` and `leetcode` are now optional because CSS 2103 has no difficulty tags. Existing data is
  still valid.
- `question-map.tsx`:
  - When the questions carry a `module`, the topic map becomes a module map. There is one bar per module, labelled
    "Module N · title" with its question count.
  - Clicking a bar shows only that module's questions. Clicking it again, or the **All modules** chip, clears it.
  - Each card shows its topic as a chip, and has a **Reveal test** button. It is a hint that shows `method`, with
    `approach` below in smaller text, and stays hidden until pressed.
  - Markdown pipe tables in the question text render as tables.
  - When a subject has no difficulty tags, the bars are single-colour and the difficulty chips are hidden.
  - CSS 2101 renders exactly as before.

Paste this to Claude Code in your repo:

> Update the "question map" feature from `<path-to>/qp-tagger/site/features/question-map/`. Replace this repo's copy of
> that folder with it, keeping the files unchanged (fix the import alias only if this repo doesn't use `@/`). Don't
> change the subject page or anything else. Then run the type check and lint. Open the CSS 2101 subject page and
> confirm it looks the same as before. Open the CSS 2103 subject page and confirm all of these:
> - "How often each module is asked" shows five module bars;
> - clicking a bar filters to that module;
> - Reveal test shows the method;
> - it works in light and dark mode.

## What's inside
| File | What it does |
|---|---|
| `question-map.tsx` | Client component: topic frequency bars (filter), difficulty chips, question cards with LeetCode links. When questions have modules, it shows a module map (click a module to practise it) and a Reveal test hint on each card. |
| `get-subject-tags.ts` | `getSubjectTags(code)`: returns the tag data for a subject code, or null |
| `types.ts` | Data types (schema 1) |
| `data/*.json` | Tagged questions per subject (`css-2101.json`, `css-2103.json`) |
| `index.ts` | Public exports |
