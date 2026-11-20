"""Export only the 30 CSS 2103 paper questions in question-map schema 1."""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / 'site/features/question-map/data/css-2103.json'
QFIELDS = {'qno', 'text', 'marks', 'co', 'cognitive_level', 'topic', 'subtopic', 'module', 'method', 'approach'}
ORDER = [f'{n}{p}' for n in range(1, 6) for p in 'ABC']

def load(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))

def require(condition, message):
    if not condition:
        raise ValueError(message)

def build():
    manifest = load('data/da/papers-manifest.json')
    extracted = load('data/da/papers-extracted.json')
    modules = [load(f'data/da/modules/m{i}.json') for i in range(1, 6)]
    output = {'schema': 1, 'subject': 'CSS 2103', 'modules': [{'number': m['number'], 'title': m['title']} for m in modules], 'papers': []}
    for kind, name in [('regular', '2025-reg'), ('makeup', '2025-makeup')]:
        curated = load(f'data/da/papers/{name}.json')
        methods = load(f'data/da/methods-{kind}.json')
        original = next(p for p in manifest if unquote(urlparse(p['url']).path) == unquote(curated['pdf_path']))
        records = {q['qno']: q for q in extracted if q['paper_id'] == original['id']}
        paper = {'pdf_path': unquote(curated['pdf_path']), 'code': 'CSS 2103', 'date': original['date'], 'exam_type': original['exam_type'], 'questions': []}
        for q in curated['questions']:
            meta = records[q['number']]
            method = methods[q['id']]
            paper['questions'].append({'qno': q['number'], 'text': plain_text(q['prompt']), 'marks': meta['marks'],
                                      'co': meta['co'], 'cognitive_level': meta['cognitive_level'],
                                      'topic': q['topic'], 'subtopic': method['subtopic'], 'module': int(q['module'][1:]),
                                      'method': method['method'], 'approach': method['approach']})
        output['papers'].append(paper)
    validate(output)
    return output

def plain_text(text):
    """The existing card displays plain text, so remove authoring-only LaTeX."""
    replacements = {'\\Rightarrow': '⇒', '\\rightarrow': '→', '\\alpha': 'α', '\\beta': 'β', '\\sigma': 'σ', '\\mu': 'μ', '\\bmod': 'mod', '\\times': '×', '\\geq': '≥', '\\leq': '≤', '\\{': '{', '\\}': '}'}
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = re.sub(r'\\operatorname\{([^{}]+)\}', r'\1', text)
    text = text.replace('$', '')
    return text

def validate(data):
    require(set(data) == {'schema', 'subject', 'modules', 'papers'}, 'Top-level schema mismatch')
    require(data['schema'] == 1 and data['subject'] == 'CSS 2103', 'Subject/schema mismatch')
    require([m['number'] for m in data['modules']] == list(range(1, 6)), 'Module catalog mismatch')
    require(len(data['papers']) == 2, 'Need both real papers')
    require([p['date'] for p in data['papers']] == ['2025-11-25', '2025-12-27'], 'Paper dates/order mismatch')
    for paper in data['papers']:
        require(set(paper) == {'pdf_path', 'code', 'date', 'exam_type', 'questions'}, 'Paper schema mismatch')
        require(paper['pdf_path'].startswith('/authoritative/') and paper['pdf_path'].endswith('.pdf'), 'Invalid PDF path')
        require(paper['code'] == 'CSS 2103', 'Wrong paper code')
        require([q['qno'] for q in paper['questions']] == ORDER, 'Question coverage/order mismatch')
        require(sum(q['marks'] for q in paper['questions']) == 50, 'Paper mark total mismatch')
        for q in paper['questions']:
            require(set(q) == QFIELDS, f'{q["qno"]}: prohibited or missing fields')
            require(q['module'] in range(1, 6), f'{q["qno"]}: module')
            require(q['marks'] == {'A': 5, 'B': 3, 'C': 2}[q['qno'][-1]], f'{q["qno"]}: marks')
            for key in ['text', 'topic', 'subtopic', 'method', 'approach']:
                require(isinstance(q[key], str) and q[key].strip(), f'{q["qno"]}: missing {key}')
            require('FIXTURE' not in json.dumps(q), 'Fixture content remains')
            require(not re.search(r'=\s*[-+]?\d+(?:\.\d+)?\s*(?:[.;]|$)', q['approach']), f'{q["qno"]}: approach contains a computed result')
            require(len(re.findall(r'[.!?](?:\s|$)', q['approach'])) <= 3, f'{q["qno"]}: approach too long')
    regular = {q['qno']: q for q in data['papers'][0]['questions']}
    require(any(word in regular['5A']['approach'].lower() for word in ['missing', 'omits']), 'Missing Holt parameter caveat')
    require('RMSE' in regular['2C']['approach'] and 'MAE' in regular['2C']['approach'], 'Missing error metric caveat')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    data = build()
    serialized = json.dumps(data, ensure_ascii=False, indent=2) + '\n'
    if args.check:
        require(OUTPUT.read_text(encoding='utf-8') == serialized, 'Generated question map differs; run python da_build.py')
    else:
        OUTPUT.write_text(serialized, encoding='utf-8')
    preserved = {}
    for name in ['data/papers.json', 'data/questions.json', 'site/features/question-map/data/css-2101.json']:
        baseline = subprocess.check_output(['git', 'show', 'main:' + name], creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        actual = (ROOT / name).read_bytes()
        require(actual == baseline, f'{name}: differs from main bytes')
        preserved[name] = hashlib.sha256(actual).hexdigest()
    report = {'schema': 1, 'subject': 'CSS 2103', 'papers': 2, 'questions': 30, 'marks_per_paper': 50,
              'data_sha256': hashlib.sha256(serialized.encode()).hexdigest(), 'preserved_main_files': preserved,
              'prohibited_fields_absent': True, 'practice_questions_shipped': 0}
    evidence = ROOT / '.artifacts/da-module-tests'
    evidence.mkdir(parents=True, exist_ok=True)
    (evidence / 'final-export.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))

if __name__ == '__main__':
    main()
