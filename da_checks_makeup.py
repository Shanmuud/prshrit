"""Recompute the 2025 makeup paper from visually transcribed exam inputs.

Prompt hashes freeze the inspected tables, constants and source-ambiguity notes.
They are not answer expectations: all numerical expectations are calculated below.
The only dependencies are Python's standard library.
"""
from collections import Counter
import hashlib
from itertools import combinations
import json
import math
from pathlib import Path
import re
import statistics as st

PROMPT_HASHES = {
    '1A': 'dd50aa9f2c867a0fc869855b36cd63ef5b933c9aed582e1bccb312ee6687f619',
    '1B': '40e87dd6351b199e4c6fa949531a1ddba566389918c207934c180d74a450d8b0',
    '2A': 'a6b3903cbb97b23a3a7d1c6af2335875403868275bcbc3bd6063a977819201bc',
    '2B': '15dac6529a2c88a05ba4b7820d58fd4d71be4e4800892da3c1fe51a162746809',
    '3A': 'a109f650f12c1776b14cd94a77ee9a543b74217fbb80c8b31a4ef47da5f60a25',
    '3B': 'd2b301db107be37710c13ed8e492eaff2fc925770277cfb54e301bb0f16f27b8',
    '3C': 'ed2afb73bb81f1130b47037a425f9da03324f50299a7a90b4d70a0dfc3c1358b',
    '4A': 'cf7edbdd9aee0bc8379b9afa32dac0b4571a25bd0a3e4263f4aaa4992707e4e2',
    '4B': 'c4a2ea0e9c8f0ba3a8bb52ca7cc7314cccf80b75b5043b55c162d3659155a886',
    '4C': '1e94322c8eb27b721ae131b4a46482ea3031d6ea8687f5e14b0dbc3209a36778',
    '5A': '609e55793ab148721b264bf5c1203e29450fb97a1bb5b8517748ec46da689971',
    '5B': '3b78238be765555599ce930693fd36c71c43912133559a9732bfbe2512dd07d8',
    '5C': '4644def27b2a06c566b2b90c98f1908106c05f3eaef3b45d9d262738629e2cc3',
}


def _counts(transactions):
    items = sorted(set().union(*transactions))
    return {''.join(s): sum(set(s) <= t for t in transactions)
            for k in range(1, len(items) + 1) for s in combinations(items, k)}


def _numbers(text):
    return [float(x) for x in re.findall(r'-?\d+(?:\.\d+)?', text)]


def _same(actual, expected):
    if isinstance(expected, dict):
        return isinstance(actual, dict) and actual.keys() == expected.keys() and all(
            _same(actual[k], v) for k, v in expected.items())
    if isinstance(expected, list):
        return isinstance(actual, list) and len(actual) == len(expected) and all(
            _same(a, b) for a, b in zip(actual, expected))
    if isinstance(expected, (int, float)):
        return isinstance(actual, (int, float)) and math.isfinite(actual) and math.isclose(
            actual, expected, rel_tol=1e-9, abs_tol=0.000051)
    return actual == expected


def _support_answer(text):
    return {key: int(value) for key, value in re.findall(r'\b([A-Ea-e]+):(\d+)\b', text)}


def verify(questions):
    ids = {qid for qid, q in questions.items()
           if qid.startswith('2025-makeup-') and q['type'] == 'numerical'}
    required = {f'2025-makeup-{number}' for number in PROMPT_HASHES}
    if ids != required:
        raise AssertionError(f'Makeup numerical coverage mismatch: {ids ^ required}')
    bank = {number: questions[f'2025-makeup-{number}'] for number in PROMPT_HASHES}
    for number, q in bank.items():
        if hashlib.sha256(q['prompt'].encode()).hexdigest() != PROMPT_HASHES[number]:
            raise AssertionError(f'{number}: inspected exam inputs changed; review computation')
    results = []
    def add(number, expected, actual):
        results.append({'id': f'2025-makeup-{number}', 'expected': expected,
                        'actual': actual, 'passed': _same(actual, expected)})

    counts = _counts([set(t) for t in ['abde', 'bce', 'abde', 'abce', 'abcde', 'bcd']])
    frequent = {s: n for s, n in counts.items() if n >= 3}
    rule_inputs = [('abd', 'e'), ('abe', 'd'), ('ade', 'b'), ('bde', 'a'), ('ab', 'de')]
    rules = {f'{a}>{b}': 100 * counts[''.join(sorted(set(a + b)))] / counts[a]
             for a, b in rule_inputs}
    rule_actual = {f'{a}>{b}': float(v) for a, b, v in re.findall(
        r'([a-e]+) → ([a-e]+):(\d+(?:\.\d+)?)%', bank['1A']['answer'])}
    add('1A', {'frequent': frequent, 'confidences': rules},
        {'frequent': _support_answer(bank['1A']['answer'].split('Five strong')[0]),
         'confidences': rule_actual})

    z = (.93 - .95) / (.04 / math.sqrt(50))
    answer = bank['1B']['answer']
    add('1B', {'z': z, 'reject': z < -1.645},
        {'z': _numbers(answer.split('$')[1])[0], 'reject': 'Reject the null hypothesis' in answer})

    cells = [[[8, 9], [9, 8], [6, 7], [10, 11]],
             [[7, 6], [8, 9], [5, 4], [9, 10]],
             [[10, 9], [11, 12], [8, 7], [12, 13]]]
    grand = st.mean(x for row in cells for cell in row for x in cell)
    rowmeans = [st.mean(x for cell in row for x in cell) for row in cells]
    colmeans = [st.mean(x for row in cells for x in row[j]) for j in range(4)]
    ss_var = 8 * sum((m - grand)**2 for m in rowmeans)
    ss_fert = 6 * sum((m - grand)**2 for m in colmeans)
    ss_error = sum((x - st.mean(cell))**2 for row in cells for cell in row for x in cell)
    ss_inter = 2 * sum((st.mean(cells[i][j]) - rowmeans[i] - colmeans[j] + grand)**2
                       for i in range(3) for j in range(4))
    f_var, f_fert = ss_var / 2 / (ss_error / 12), ss_fert / 3 / (ss_error / 12)
    anova_actual = {}
    for name, ss, df, ms, f in re.findall(
            r'\| (Variety|Fertilizer|Interaction|Within-cell error) \| ([\d.]+) \| (\d+) \| ([\d.]+) \| ([\d.]+|—) \|', bank['2A']['explanation']):
        anova_actual[name] = [float(ss), int(df), float(ms)] + ([] if f == '—' else [float(f)])
    add('2A', {'answer_F': [f_var, f_fert], 'table': {
        'Variety': [ss_var, 2, ss_var/2, f_var],
        'Fertilizer': [ss_fert, 3, ss_fert/3, f_fert],
        'Interaction': [ss_inter, 6, ss_inter/6, (ss_inter/6)/(ss_error/12)],
        'Within-cell error': [ss_error, 12, ss_error/12]}},
        {'answer_F': _numbers(bank['2A']['answer'].split('Both')[0]), 'table': anova_actual})

    transactions = [[1,2,3,6], [2,4,5], [1,3,4,6], [2,3,5,6], [1,2,4,5]]
    pairs = Counter(pair for t in transactions for pair in combinations(t, 2))
    buckets = [0] * 10
    for (x, y), n in pairs.items():
        buckets[(x * 11 + y) % 10] += n
    kept = sorted([list(pair) for pair in pairs if buckets[(pair[0]*11+pair[1])%10] >= 4])
    answer = bank['2B']['answer']
    add('2B', {'buckets': buckets, 'candidates': kept},
        {'buckets': _numbers(answer.split(':', 1)[1].split('.')[0]),
         'candidates': sorted([[int(a), int(b)] for a,b in re.findall(r'\{I(\d),I(\d)\}', answer)])})

    values = sorted([78,91,68,54,82,47,60,78,97,58,62,50,50,63,92,75,79,63,42,61])
    q1, med, q3 = st.median(values[:10]), st.median(values), st.median(values[10:])
    iqr = q3 - q1
    lower, upper = q1 - 1.5*iqr, q3 + 1.5*iqr
    rank1, rank2 = range(1,13), [1,2,4,3,6,5,8,7,10,9,12,11]
    rho = 1 - 6*sum((a-b)**2 for a,b in zip(rank1, rank2))/(12*(12**2-1))
    add('3A', [min(values),q1,med,q3,max(values),iqr,lower,upper,
               sum(x < lower or x > upper for x in values),rho], _numbers(bank['3A']['answer']))

    transactions = [set(s) for s in ['MBD','MB','MD','BD','MBD']]
    counts = _counts(transactions)
    pair_counts = [counts[s] for s in ['BM','DM','BD']]
    add('3B', [pair_counts[0], 100*pair_counts[0]/len(transactions)],
        _numbers(bank['3B']['answer']))
    # Verify the answer's universal pair statement and maximality from enumeration.
    if len(set(pair_counts)) != 1 or counts['BDM']/len(transactions) >= .6:
        raise AssertionError('3B pair/maximality premise failed')
    add('3C', [st.mean([95,120,130])], _numbers(bank['3C']['answer']))

    counts = _counts([set(t) for t in ['ABD','BCE','ABCE','BE']])
    add('4A', {s:n for s,n in counts.items() if n>=2}, _support_answer(bank['4A']['answer']))

    sales = [80,95,100,110,120]
    forecast = 80
    forecasts = []
    for actual in sales:
        forecast = .4*actual + .6*forecast
        forecasts.append(forecast)
    mae = st.mean(abs(y-f) for y,f in zip(sales[1:],forecasts[:-1]))
    add('4B', forecasts+[mae], _numbers(bank['4B']['answer']))
    add('4C', [(180/800)/((360/800)*(300/800)), (180/360+180/300)/2],
        _numbers(bank['4C']['answer']))

    level, trend = 100, 120-100
    levels, trends = [], []
    for value in [120,130]:
        new_level = .2*value+.8*(level+trend)
        trend = .4*(new_level-level)+.6*trend
        level = new_level
        levels.append(level)
        trends.append(trend)
    add('5A', [100,120-100,levels[0],trends[1],level+trend], _numbers(bank['5A']['answer']))

    counts = _counts([set(t) for t in ['ABC','ACD','BCE','ABCE','ABDE']])
    frequent = {s:n for s,n in counts.items() if n>=2}
    closed = sorted(s for s,n in frequent.items()
                    if not any(set(s)<set(t) and count==n for t,count in counts.items()))
    maximal = sorted(s for s in frequent if not any(set(s)<set(t) for t in frequent))
    answer = bank['5B']['answer']
    add('5B', {'frequent':frequent,'closed':closed,'maximal':maximal},
        {'frequent':_support_answer(answer),
         'closed':sorted(re.findall(r'\b[A-E]+\b', answer.split('Closed frequent:')[1].split('.')[0])),
         'maximal':sorted(re.findall(r'\b[A-E]+\b', answer.split('Maximal frequent:')[1].split('.')[0]))})

    values = [145,155,160,162,165,172,180,190,200,220,240,260]
    width = (max(values)-min(values))/3
    width_bins = [[],[],[]]
    for value in values:
        width_bins[min(2,int((value-min(values))/width))].append(value)
    freq_bins = [values[i:i+4] for i in range(0,len(values),4)]
    add('5C', [width]+[len(b) for b in width_bins]+[len(b) for b in freq_bins],
        _numbers(bank['5C']['answer']))
    return results


if __name__ == '__main__':
    path = Path(__file__).parent/'data/da/papers/2025-makeup.json'
    paper = json.loads(path.read_text(encoding='utf-8'))
    results = verify({q['id']:q for q in paper['questions']})
    print(json.dumps(results, indent=2))
    if not all(r['passed'] for r in results):
        raise SystemExit(1)
    print(f'PASS: {len(results)} makeup numerical questions recomputed')
