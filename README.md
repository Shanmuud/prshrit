# qp-tagger

Tags every question in MIT Manipal past papers (from [paper.shrit.in](https://paper.shrit.in)) with a
**topic** (Stack, Queue, Singly LL, Doubly LL, Trees, Graphs, ...), a **LeetCode-style difficulty**
(Easy / Medium / Hard, an estimate of the exam task, not an official rating) and **similar LeetCode problems**.

First subject: Data Structures, CSS 2101 (and old code CSE 2122): 3 papers, 45 questions.

## What it looks like

It sits on the subject page, under the existing list of papers.

**Topic map.** How often each topic is asked, split by difficulty. Click a topic to filter.

<table>
  <tr>
    <td><img src="docs/screenshots/01-overview-dark.png" alt="Subject page in dark mode: paper list, then topic bars split into Easy, Medium and Hard"></td>
    <td><img src="docs/screenshots/02-overview-light.png" alt="The same page in light mode"></td>
  </tr>
  <tr><td align="center">Dark (site default)</td><td align="center">Light</td></tr>
</table>

**Filter by topic, difficulty or paper.** Here only the Stack questions are shown.

<img src="docs/screenshots/03-filter-stack.png" alt="Stack filter applied: 5 of 45 questions, each with its subtopic, difficulty and marks">

**Open a question** to read the full text, why it got its difficulty, and similar LeetCode problems.

<img src="docs/screenshots/04-question-detail.png" alt="Question 3C expanded: full text, CO and cognitive level, the reason it is Medium, and a link to LeetCode 20 Valid Parentheses">

<table>
  <tr>
    <td width="300"><img src="docs/screenshots/05-mobile.png" alt="Phone layout: topic bars and filter chips wrap to fit"></td>
    <td><b>On phones</b> the topic bars and filter chips wrap to fit the screen.</td>
  </tr>
</table>

### CSS 2103 Data Analytics: the module map

CSS 2103 adds the 30 questions from its two end-sem papers (Regular Nov/Dec 2025 and Makeup Dec 2025/Jan 2026). Each
one is tagged with a course module and a topic. When a subject's questions carry modules, the topic map becomes a
**module map**: one bar per module, all five shown, each with its question count. This subject has no difficulty
tags, so the bars are single-colour and the difficulty chips are hidden.

<table>
  <tr>
    <td><img src="docs/screenshots/06-css2103-module-map-dark.png" alt="CSS 2103 subject page in dark mode: module map with five bars, the All modules chip, paper chips, and question cards grouped by module"></td>
    <td><img src="docs/screenshots/08-css2103-light.png" alt="The same module map and cards in light mode"></td>
  </tr>
  <tr><td align="center">Dark (site default)</td><td align="center">Light</td></tr>
</table>

**Practise one module.** Click a module's bar to see only that module's questions, opened and ready to try. Click the
bar again or **All modules** to clear the selection; the paper chips still filter. Each card shows its topic as a small
chip. **Reveal test** is a hint: it shows which test or technique to use, with the approach in smaller text. It is not
a worked answer and gives no final numbers. Tables in the question text render as real tables.

<img src="docs/screenshots/07-css2103-reveal-test.png" alt="Module 3 selected: 6 of 30 questions; question 1B open with Reveal test pressed, showing Two-tailed one-sample z-test and a short approach">

<table>
  <tr>
    <td width="300"><img src="docs/screenshots/09-css2103-mobile.png" alt="Phone layout at 390px: module bars, filter chips and cards with Reveal test buttons fit the screen"></td>
    <td><b>On phones</b> the module bars, chips and cards fit a 390px screen.</td>
  </tr>
</table>

## Add it to paper.shrit.in with Claude Code

Paste this into Claude Code from inside the site's repo:

```
Clone https://github.com/Shanmuud/prshrit into a temp folder and follow its MERGE.md to add the
question-map feature to this site. Copy only site/features/question-map/, add the two marked lines to
the subject page (/browse/.../subject/<code>), map any Tailwind token names that differ here, and
change nothing else. Then run typecheck + lint and confirm the CSS 2101 subject page shows the map
in light and dark mode, and that untagged subjects look unchanged.
```

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
subject page. **`MERGE.md` has a ready-to-paste prompt for Claude Code.** If you already merged it, re-copy the folder
to get CSS 2103 and its module map. No page changes are needed. Your site's code never
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
