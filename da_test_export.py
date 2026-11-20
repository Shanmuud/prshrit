"""Check final A4 schema, preservation, and rejection of excluded content."""
import copy
import json
from da_export import ROOT, OUTPUT, build, validate

def main():
    data = json.loads(OUTPUT.read_text(encoding='utf-8'))
    validate(data)
    assert data == build(), 'Output differs from curated sources'
    cases = []
    def rejects(name, change):
        bad = copy.deepcopy(data)
        change(bad)
        try:
            validate(bad)
        except (ValueError, AssertionError):
            cases.append({'case': name, 'passed': True})
        else:
            raise AssertionError(f'Accepted {name}')
    for key in ['answer', 'explanation', 'difficulty', 'reason', 'leetcode', 'options']:
        rejects('prohibited ' + key, lambda d, key=key: d['papers'][0]['questions'][0].update({key:'excluded'}))
    rejects('missing paper', lambda d: d['papers'].pop())
    rejects('missing question', lambda d: d['papers'][0]['questions'].pop())
    rejects('wrong marks', lambda d: d['papers'][0]['questions'][0].update(marks=99))
    rejects('unknown module', lambda d: d['papers'][0]['questions'][0].update(module=6))
    rejects('missing method', lambda d: d['papers'][0]['questions'][0].update(method=''))
    rejects('computed answer in approach', lambda d: d['papers'][0]['questions'][0].update(approach='The result = 123.'))
    rejects('practice content', lambda d: d.update(tests=[]))
    rejects('missing Holt caveat', lambda d: d['papers'][0]['questions'][12].update(approach='Update the level and trend.'))
    rejects('missing metric caveat', lambda d: d['papers'][0]['questions'][5].update(approach='Compare forecast errors.'))
    report = {'baseline': 'passed', 'invalid_cases_rejected': len(cases), 'cases': cases}
    (ROOT / '.artifacts/da-module-tests/final-probes.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(f'PASS final schema, exact export, and {len(cases)} invalid-data probes')

if __name__ == '__main__':
    main()
