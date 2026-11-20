"""Recompute every Module 3 numerical answer using only the standard library."""
import json
import math
import re
import statistics as st
from pathlib import Path


def verify(questions):
    cases = {}
    def add(qid, inputs, expected):
        cases[qid] = (inputs, expected)

    add('m3-t2-q1', ['10, 20, 30', 'mean'], [st.mean([10, 20, 30])])
    data = [2, 4, 6, 8, 10, 12]
    add('m3-t2-q2', ['2, 4, 6, 8, 10, 12', 'two equal-frequency'],
        [st.mean(data[i // 3 * 3:i // 3 * 3 + 3]) for i in range(6)])
    add('m3-t2-q3', ['minimum 20', 'maximum 100', 'value 50'], [(50-20)/(100-20)])
    add('m3-t2-q4', ['mean 60', 'standard deviation 8', 'value 72'], [(72-60)/8])
    data = [-12, 320, 80]
    j = 0
    while max(abs(x) for x in data) / 10**j >= 1:
        j += 1
    add('m3-t2-q5', ['-12, 320, 80'], [j] + [x/10**j for x in data])
    add('m3-t2-q6', ['minimum 5', 'maximum 45', '4 bins'], [(45-5)/4])
    x, y = [1, 2, 3], [2, 4, 6]
    cov = sum((a-st.mean(x))*(b-st.mean(y)) for a, b in zip(x, y))/len(x)
    corr = cov/(st.pstdev(x)*st.pstdev(y))
    add('m3-t2-q7', ['(1,2), (2,4), (3,6)', 'population'], [cov, corr])
    add('m3-t2-q8', ['eigenvalues 9, 3, 2, 1', 'first two'], [100*(9+3)/(9+3+2+1)])
    add('m3-t4-q1', ['mean 54', 'null mean 50', 'standard deviation 12', 'size 36'], [(54-50)/(12/math.sqrt(36))])
    add('m3-t4-q2', ['mean 21', 'standard deviation 4', 'size 16', 'null mean 19'], [(21-19)/(4/math.sqrt(16)), 16-1])
    differences = [2, 4, 4, 6]
    add('m3-t4-q3', ['2, 4, 4, 6', 'null mean difference is zero'], [st.mean(differences)/(st.stdev(differences)/math.sqrt(len(differences))), len(differences)-1])
    add('m3-t4-q4', ['means 105 and 100', 'standard deviations 12 and 9', 'sizes 36 and 36'], [(105-100)/math.sqrt(12**2/36+9**2/36)])
    pooled = ((10-1)*4**2+(10-1)*4**2)/(10+10-2)
    add('m3-t4-q5', ['means 18 and 14', 'standard deviations 4 and 4', 'sizes 10 and 10'], [(18-14)/math.sqrt(pooled*(1/10+1/10)), 10+10-2])
    a, b = 9**2/9, 8**2/16
    add('m3-t4-q6', ['means 30 and 24', 'standard deviations 9 and 8', 'sizes 9 and 16'], [(30-24)/math.sqrt(a+b), (a+b)**2/(a*a/8+b*b/15)])
    add('m3-t4-q7', ['0.18'], [1-0.18])
    cells = [[4, 6], [8, 10], [6, 8], [10, 12]]
    sse = sum(sum((x-st.mean(cell))**2 for x in cell) for cell in cells)
    df = 2*2*(2-1)
    add('m3-t4-q8', ['[4,6], [8,10], [6,8], [10,12]'], [sse, df, sse/df])
    observed = [30, 20, 25, 25]
    expected = [sum(observed)/4]*4
    add('m3-t4-q9', ['30, 20, 25, 25', 'equal category probabilities'],
        [sum((o-e)**2/e for o, e in zip(observed, expected)), 4-1])
    add('m3-t4-q10', ['Z statistic is 2', 'two-sided'],
        [2*(1-st.NormalDist().cdf(2))])

    numerical = {qid for qid, q in questions.items() if qid.startswith('m3-') and q['type'] == 'numerical'}
    if numerical != set(cases):
        raise AssertionError(f'Module 3 numerical coverage mismatch: {numerical ^ set(cases)}')
    results = []
    for qid, (inputs, expected) in cases.items():
        q = questions[qid]
        if not all(token in q['prompt'] for token in inputs):
            raise AssertionError(f'{qid}: question inputs changed; update independent calculation')
        actual = [float(v) for v in re.findall(r'(?<![A-Za-z])[-+]?\d+(?:\.\d+)?', q['answer'])]
        passed = len(actual) == len(expected) and all(math.isclose(a, e, abs_tol=0.000051) for a, e in zip(actual, expected))
        results.append({'id': qid, 'expected': expected, 'actual': actual, 'passed': passed})
    return results


if __name__ == '__main__':
    module = json.loads((Path(__file__).parent / 'data/da/modules/m3.json').read_text(encoding='utf-8'))
    questions = {q['id']: q for t in module['tests'] for q in t['questions']}
    results = verify(questions)
    print(json.dumps(results, indent=2))
    if not all(row['passed'] for row in results):
        raise SystemExit(1)
