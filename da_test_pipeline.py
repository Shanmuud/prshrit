"""Regression probes for DA validation and numerical-answer rejection."""
import copy
import json
from pathlib import Path
from da_build import ROOT, validate

def archived_main():
    data = json.loads((ROOT / 'site/features/module-tests/data/da.json').read_text(encoding='utf-8'))
    sources = {r['file']: r['pages'] for r in json.loads((ROOT / 'data/da/extracted/sources.json').read_text(encoding='utf-8'))}
    validate(data, sources)
    # Numerical rejection must not accidentally pass merely because HTML is stale.
    for question in [q for m in data['modules'] for t in m['tests'] for q in t['questions']] + [q for p in data['papers'] for q in p['questions']]:
        for key in ('prompt_html', 'answer_html', 'explanation_html', 'options_html'):
            question.pop(key, None)
    results = []

    def rejected(label, mutate):
        damaged = copy.deepcopy(data)
        mutate(damaged)
        try:
            validate(damaged, sources)
        except (ValueError, AssertionError):
            results.append({'case': label, 'passed': True})
        else:
            raise AssertionError(f'Invalid data accepted: {label}')

    rejected('missing module', lambda d: d['modules'].pop())
    rejected('too few questions', lambda d: d['modules'][0]['tests'][0]['questions'].__delitem__(slice(0, 4)))
    rejected('empty explanation', lambda d: d['modules'][0]['tests'][0]['questions'][0].update(explanation=''))
    rejected('unknown topic', lambda d: d['modules'][0]['tests'][0]['questions'][0].update(topic='Not in course'))
    rejected('out of range citation', lambda d: d['modules'][0]['tests'][0]['questions'][0].update(source='Module 1- Introduction to Data Analytics.pptx slide 999'))
    rejected('missing numerical check', lambda d: d['modules'][0]['tests'][0]['questions'][0].update(type='numerical', answer='17'))
    rejected('MCQ answer absent from options', lambda d: d['modules'][0]['tests'][0]['questions'][1].update(answer='None of the above'))
    rejected('missing paper', lambda d: d['papers'].pop())
    rejected('missing paper question', lambda d: d['papers'][0]['questions'].pop())
    rejected('wrong paper marks', lambda d: d['papers'][0]['questions'][0].update(marks=99))
    rejected('unknown paper module', lambda d: d['papers'][0]['questions'][0].update(module='m6'))
    rejected('wrong paper PDF path', lambda d: d['papers'][0].update(pdf_path='/not-authoritative.pdf'))
    rejected('unsafe rendered HTML', lambda d: d['modules'][0]['tests'][0]['questions'][0].update(prompt_html='<script>alert(1)</script>', answer_html='', explanation_html='', options_html=[]))
    for mi, module in enumerate(data['modules']):
        for ti, test in enumerate(module['tests']):
            for qi, q in enumerate(test['questions']):
                if q['type'] == 'numerical':
                    rejected('wrong answer ' + q['id'], lambda d, mi=mi, ti=ti, qi=qi: d['modules'][mi]['tests'][ti]['questions'][qi].update(answer='987654321'))
    for pi, paper in enumerate(data['papers']):
        for qi, q in enumerate(paper['questions']):
            if q['type'] == 'numerical':
                rejected('wrong answer ' + q['id'], lambda d, pi=pi, qi=qi: d['papers'][pi]['questions'][qi].update(answer='987654321'))
    report = {'baseline': 'passed', 'rejected_invalid_cases': len(results), 'cases': results}
    output = ROOT / '.artifacts/da-module-tests/pipeline-probes.json'
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(f'PASS: baseline and {len(results)} invalid-data rejection cases')

if __name__ == '__main__':
    from da_test_export import main
    main()
