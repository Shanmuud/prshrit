# CSS 2103 question-map pipeline

The final A4 scope ships only the 30 real paper questions in
`site/features/question-map/data/css-2103.json`, using schema 1. Each question has
its exam metadata, module, topic, subtopic, method and short approach. There are
no answer, explanation, difficulty, reason, LeetCode or practice-test fields.
The existing CSS 2103 registry entry loads this file. No new site packages or
page mount are required.

## Rebuild and check

```powershell
python da_build.py
python da_build.py --check
python da_test_pipeline.py
```

These final export commands use only Python's standard library and the checked-in
curated inputs. The build checks that the shared `data/papers.json`,
`data/questions.json` and CSS 2101 site JSON remain byte-identical to `main`.

To refresh the original paper downloads and extraction, install the root-only
requirements and use an isolated manifest:

```powershell
python -m pip install -r da_requirements.txt
python scrape.py 'https://paper.shrit.in/browse/Year%202/Semester%203/CSE/subject/CSS%202103' --output data/da/papers-manifest.json
python da_extract_papers.py
```

The DA wrapper calls the existing extractor, applies image/table transcriptions
from `data/overrides.json`, and reconciles repeated headings at PDF page breaks.
Both PDFs were visually checked: each contains 15 questions and 50 marks.
Downloads are ignored under `data/pdfs/`; PDF hashes and page counts appear in
`.artifacts/da-module-tests/paper-sources.json`.

## Editable sources

- `papers/2025-reg.json` and `papers/2025-makeup.json` retain the verified question
  text and module/topic mapping. Earlier answer-writing work remains here for
  future use but the exporter never copies its answer fields into the site.
- `methods-regular.json` and `methods-makeup.json` hold the method, approach and
  subtopic tags. Approaches give procedural hints, never computed final results.
- `modules/m1.json` through `m5.json` retain the course catalog and earlier
  practice work locally. Only module number/title are exported.
- `da_export.py` is the final export implementation; `da_build.py` invokes it.
  `da_test_export.py` holds final-scope regression probes.

`RUBRIC.md` in this folder documents module mapping and method-hint rules.
Regular Q5A has missing smoothing constants, and regular Q2C has inconsistent
MAE/RMSE values. These and other source ambiguities are flagged in the relevant
method hints rather than resolved by inventing inputs.

The superseded renderer/checker scripts remain root-only authoring tools. Final
question-map output uses plain text and needs no Markdown or MathML runtime.
Nothing regenerates the deleted module-tests feature. Frontend owns site build,
lint, preview and UI verification; the backend does not run Next builds.

Final evidence: `.artifacts/da-module-tests/final-export.json` and
`final-probes.json`. Earlier numerical and renderer reports describe superseded
scope and are not the final acceptance report.
