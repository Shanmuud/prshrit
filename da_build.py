"""Validate curated DA questions against extracted sources and build the UI JSON."""
import argparse
import hashlib
import importlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / 'data/da/archive-rendered.json'
HTML_FIELDS = {'prompt_html', 'answer_html', 'explanation_html', 'options_html'}

def require(condition, message):
    if not condition:
        raise ValueError(message)

def validate(data, sources):
    require(set(data) == {'subject', 'modules', 'papers'}, 'Unexpected subject fields')
    require(len(data['papers']) == 2, 'Both past papers are required')
    require(data['subject'] == 'Data Analytics', 'Wrong subject')
    require([m['number'] for m in data['modules']] == list(range(1, 6)), 'Need modules 1-5 in order')
    questions, counts, refs = {}, [], set()
    for module in data['modules']:
        mid = module['id']
        require(set(module) == {'id', 'number', 'title', 'topics', 'tests'}, f'{mid}: module fields')
        require(mid == f"m{module['number']}", f'{mid}: invalid module ID')
        require(isinstance(module['title'], str) and module['title'].strip(), f'{mid}: title')
        topics = module['topics']
        require(isinstance(topics, list) and topics and all(isinstance(t, str) and t.strip() for t in topics), f'{mid}: topics')
        require(len(set(topics)) == len(topics), f'{mid}: duplicate topics')
        require(len(module['tests']) >= 2, f'{mid}: need two tests')
        if module['number'] > 1:
            require(any(t['kind'] == 'numerical' for t in module['tests']), f'{mid}: need numerical test')
        used_topics = set()
        for ti, test in enumerate(module['tests'], 1):
            tid = f'{mid}-t{ti}'
            require(set(test) == {'id', 'title', 'kind', 'questions'}, f'{tid}: test fields')
            require(test['id'] == tid and test['title'].strip(), f'{tid}: test ID/title')
            require(test['kind'] in {'concept', 'numerical', 'mixed'}, f'{tid}: kind')
            require(8 <= len(test['questions']) <= 15, f'{tid}: need 8-15 questions')
            for qi, question in enumerate(test['questions'], 1):
                qid = f'{tid}-q{qi}'
                fields = {'id', 'type', 'prompt', 'answer', 'explanation', 'difficulty', 'topic', 'source'}
                require(set(question) - HTML_FIELDS == fields | ({'options'} if question['type'] == 'mcq' else set()), f'{qid}: question fields')
                require(question['id'] == qid and qid not in questions, f'{qid}: invalid/duplicate ID')
                require(question['type'] in {'mcq', 'short', 'numerical', 'long'}, f'{qid}: type')
                require(question['difficulty'] in {'easy', 'medium', 'hard'}, f'{qid}: difficulty')
                for key in fields:
                    require(isinstance(question[key], str) and question[key].strip(), f'{qid}: empty {key}')
                require(question['topic'] in topics, f'{qid}: unknown topic')
                used_topics.add(question['topic'])
                if question['type'] == 'mcq':
                    options = question['options']
                    require(isinstance(options, list) and len(options) >= 2 and all(isinstance(o, str) and o.strip() for o in options), f'{qid}: options')
                    require(len(set(options)) == len(options) and options.count(question['answer']) == 1, f'{qid}: answer must match one unique option')
                matches = []
                for name, pages in sources.items():
                    pattern = re.escape(name) + r'\s+(?:slides?|PDF page|page|p\.)\s*(\d+)'
                    for match in re.finditer(pattern, question['source'], re.I):
                        number = int(match.group(1))
                        require(1 <= number <= len(pages), f'{qid}: source page out of range')
                        matches.append(name)
                        refs.add(name)
                require(matches, f'{qid}: source must name an extracted file and slide/page')
                questions[qid] = question
            if test['kind'] == 'numerical':
                require(all(q['type'] == 'numerical' for q in test['questions']), f'{tid}: numerical test includes non-numerical questions')
        require(used_topics == set(topics), f'{mid}: unused topic labels')
        counts.append({'module': mid, 'tests': len(module['tests']), 'questions': sum(len(t['questions']) for t in module['tests'])})
    for name in ['Module 3 - part_A.pptx', 'Module 3 Hypothesis testing.pptx']:
        require(name in refs, f'Missing module 3 source: {name}')
    results = []
    for name in ['da_checks_m12', 'da_checks_m3', 'da_checks_m45']:
        results.extend(importlib.import_module(name).verify(questions))
    paper_counts = []
    if data.get('papers'):
        from urllib.parse import urlparse
        from pypdf import PdfReader
        manifest = json.loads((ROOT / 'data/da/papers-manifest.json').read_text(encoding='utf-8'))
        extracted = json.loads((ROOT / 'data/da/papers-extracted.json').read_text(encoding='utf-8'))
        require([p['id'] for p in data['papers']] == ['2025-reg', '2025-makeup'], 'Expected regular and makeup papers in order')
        by_module = {m['id']: m for m in data['modules']}
        for paper in data['papers']:
            require(set(paper) == {'id', 'title', 'pdf_path', 'questions'}, f'{paper["id"]}: paper fields')
            require(isinstance(paper['title'], str) and paper['title'].strip(), 'Missing paper title')
            matched = [m for m in manifest if urlparse(m['url']).path == paper['pdf_path']]
            require(len(matched) == 1, f'{paper["id"]}: unknown authoritative PDF path')
            original = matched[0]
            required_questions = [q for q in extracted if q['paper_id'] == original['id']]
            require([q['number'] for q in paper['questions']] == [q['qno'] for q in required_questions], f'{paper["id"]}: paper coverage/order mismatch')
            require(len(required_questions) == 15, f'{paper["id"]}: expected 15 questions')
            page_count = len(PdfReader(ROOT / original['file']).pages)
            for question, original_q in zip(paper['questions'], required_questions):
                qid = question['id']
                fields = {'id', 'type', 'prompt', 'answer', 'explanation', 'difficulty', 'topic', 'source', 'number', 'marks', 'module'}
                require(set(question) - HTML_FIELDS == fields | ({'options'} if question['type'] == 'mcq' else set()), f'{qid}: paper question fields')
                require(qid == f'{paper["id"]}-{question["number"]}' and qid not in questions, f'{qid}: paper ID')
                require(question['type'] in {'mcq', 'short', 'numerical', 'long'}, f'{qid}: type')
                require(question['difficulty'] in {'easy', 'medium', 'hard'}, f'{qid}: difficulty')
                for key in fields - {'marks'}:
                    require(isinstance(question[key], str) and question[key].strip(), f'{qid}: empty {key}')
                require(question['marks'] == original_q['marks'], f'{qid}: wrong marks')
                if original_q.get('from_image'):
                    require(question['prompt'] == original_q['text'], f'{qid}: prompt differs from verified transcription')
                require(question['module'] in by_module, f'{qid}: unknown module')
                require(question['topic'] in by_module[question['module']]['topics'], f'{qid}: unknown module topic')
                pages = re.findall(r'PDF page\s+(\d+)', question['source'])
                require(pages and all(1 <= int(p) <= page_count for p in pages), f'{qid}: paper page reference')
                require(Path(original['file']).name in question['source'] and question['number'] in question['source'], f'{qid}: paper provenance')
                if question['type'] == 'mcq':
                    opts = question['options']
                    require(len(set(opts)) == len(opts) and opts.count(question['answer']) == 1, f'{qid}: MCQ answer')
                questions[qid] = question
            require(sum(q['marks'] for q in paper['questions']) == 50, f'{paper["id"]}: total marks')
            paper_counts.append({'paper': paper['id'], 'questions': len(paper['questions']), 'marks': 50})
        for name in ['da_checks_regular', 'da_checks_makeup']:
            results.extend(importlib.import_module(name).verify(questions))
    numerical = {qid for qid, q in questions.items() if q['type'] == 'numerical'}
    checked = {r['id'] for r in results}
    require(numerical <= checked, f'Unchecked numerical questions: {sorted(numerical - checked)}')
    require(checked <= questions.keys(), 'Verification references unknown question')
    require(all(r['passed'] for r in results), f'Numerical verification failed: {[r for r in results if not r["passed"]]}')
    for qid, question in questions.items():
        if HTML_FIELDS & question.keys():
            from da_render import render_question
            require(HTML_FIELDS <= question.keys(), f'{qid}: incomplete rendered fields')
            expected = render_question(question)
            require(all(question[key] == expected[key] for key in HTML_FIELDS), f'{qid}: stale or unsafe rendered HTML')
    return {'modules': counts, 'papers': paper_counts, 'question_count': len(questions), 'numerical_count': len(numerical), 'numerical_checks': results}

def archived_main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Check existing UI JSON agrees with curated source')
    parser.add_argument('--evidence-dir', type=Path, default=ROOT / '.artifacts/da-module-tests')
    args = parser.parse_args()
    records = json.loads((ROOT / 'data/da/extracted/sources.json').read_text(encoding='utf-8'))
    sources = {r['file']: r['pages'] for r in records}
    data = {'subject': 'Data Analytics', 'modules': [json.loads((ROOT / f'data/da/modules/m{i}.json').read_text(encoding='utf-8')) for i in range(1, 6)]}
    paper_paths = [ROOT / f'data/da/papers/{name}.json' for name in ['2025-reg', '2025-makeup']]
    data['papers'] = [json.loads(p.read_text(encoding='utf-8')) for p in paper_paths]
    report = validate(data, sources)
    from da_render import render_question
    questions = [q for m in data['modules'] for t in m['tests'] for q in t['questions']]
    questions.extend(q for p in data['papers'] for q in p['questions'])
    for question in questions:
        question.update(render_question(question))
        require(HTML_FIELDS <= question.keys(), f'{question["id"]}: missing rendered fields')
        require(len(question['options_html']) == len(question.get('options', [])), f'{question["id"]}: rendered option count')
    serialized = json.dumps(data, ensure_ascii=False, indent=2) + '\n'
    if args.check:
        require(OUTPUT.read_text(encoding='utf-8') == serialized, 'UI JSON differs: run python da_build.py')
    else:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(serialized, encoding='utf-8')
    report['data_sha256'] = hashlib.sha256(serialized.encode()).hexdigest()
    report['sources'] = [{'file': r['file'], 'sha256': r['sha256'], 'pages': len(r['pages'])} for r in records]
    args.evidence_dir.mkdir(parents=True, exist_ok=True)
    (args.evidence_dir / 'verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in report.items() if k not in {'numerical_checks', 'sources'}}, indent=2))

if __name__ == '__main__':
    # A4 final scope: only the real-paper question map is shipped.
    from da_export import main
    main()
