"""Recompute every Module 1/2 numerical answer from its displayed prompt."""
import itertools
import json
import math
import re
import statistics
from pathlib import Path

NUMBER = r'[-+]?\d+(?:\.\d+)?'

def numbers(text):
    return [float(x) for x in re.findall(r'(?<![A-Za-z0-9])' + NUMBER, text)]

def field(prompt, pattern):
    match = re.search(pattern, prompt)
    if not match:
        raise ValueError(f'Missing numerical input matching {pattern!r}')
    return float(match.group(1))

def arrays(prompt):
    return [numbers(x) for x in re.findall(r'\[([^]]+)\]', prompt)]

def compute(index, p):
    if index in (1, 2, 3):
        values = numbers(p.split(':', 1)[1].split('.', 1)[0])
        if index == 1:
            return [statistics.mean(values), statistics.median(values), statistics.mode(values)]
        if index == 2:
            return [statistics.variance(values), statistics.stdev(values)]
        values.sort()
        middle = len(values) // 2
        q1 = statistics.median(values[:middle])
        q3 = statistics.median(values[middle + 1:])
        return [q1, statistics.median(values), q3, q3 - q1]
    if index == 4:
        x = field(p, r'score is (' + NUMBER + ')')
        mean = field(p, r'mean is (' + NUMBER + ')')
        sd = field(p, r'deviation is (' + NUMBER + ')')
        return [(x - mean) / sd]
    if index == 5:
        n = field(p, r'n = (' + NUMBER + ')')
        mean = field(p, r'mean = (' + NUMBER + ')')
        sd = field(p, r'known to be (' + NUMBER + ')')
        z = field(p, r'z = (' + NUMBER + ')')
        margin = z * sd / math.sqrt(n)
        return [mean - margin, mean + margin]
    if index == 6:
        x = field(p, r'x = (' + NUMBER + ')')
        (low, high), (new_low, new_high) = arrays(p)
        return [new_low + (x - low) * (new_high - new_low) / (high - low)]
    if index == 7:
        values = numbers(p.split(':', 1)[1].split('.', 1)[0])
        bins = [numbers(x) for x in re.findall(r'\[([^)]*)\)', p)]
        return [sum(lo <= value < hi for value in values) for lo, hi in bins]
    if index in (8, 9, 15):
        x, y = arrays(p)
        if index == 9:
            products = [(x[i] - x[j]) * (y[i] - y[j]) for i, j in itertools.combinations(range(len(x)), 2)]
            c = sum(v > 0 for v in products)
            d = sum(v < 0 for v in products)
            return [c, d, (c - d) / len(products)]
        mx, my = statistics.mean(x), statistics.mean(y)
        cross = sum((a - mx) * (b - my) for a, b in zip(x, y))
        if index == 15:
            return [cross / (len(x) - 1)]
        return [cross / math.sqrt(sum((a - mx)**2 for a in x) * sum((b - my)**2 for b in y))]
    if index == 10:
        n = field(p, r'n = (' + NUMBER + ')')
        mean = field(p, r'sample mean = (' + NUMBER + ')')
        sd = field(p, r'sample SD = (' + NUMBER + ')')
        null = field(p, r'null mean = (' + NUMBER + ')')
        return [(mean - null) / (sd / math.sqrt(n)), n - 1]
    if index == 11:
        n = field(p, r'n1 = n2 = (' + NUMBER + ')')
        match = re.search(r'means (' + NUMBER + r') and (' + NUMBER + ')', p)
        means = list(map(float, match.groups()))
        match = re.search(r'SDs (' + NUMBER + r') and (' + NUMBER + ')', p)
        s1, s2 = map(float, match.groups())
        pooled = ((n - 1) * s1**2 + (n - 1) * s2**2) / (2*n - 2)
        return [(means[0] - means[1]) / math.sqrt(pooled * 2/n), 2*n - 2]
    if index == 12:
        pairs = []
        for label in ('means', 'sample SDs', 'sample sizes'):
            match = re.search(label + r' (' + NUMBER + r') and (' + NUMBER + ')', p)
            pairs.append(tuple(map(float, match.groups())))
        (m1, m2), (s1, s2), (n1, n2) = pairs
        return [(m1 - m2) / math.sqrt(s1*s1/n1 + s2*s2/n2)]
    if index == 13:
        groups = arrays(p)
        values = [v for group in groups for v in group]
        grand = statistics.mean(values)
        between = sum(len(group) * (statistics.mean(group) - grand)**2 for group in groups)
        within = sum(sum((v - statistics.mean(group))**2 for v in group) for group in groups)
        df1, df2 = len(groups) - 1, len(values) - len(groups)
        return [(between / df1) / (within / df2), df1, df2]
    if index == 14:
        rows = arrays(p)
        row_totals = list(map(sum, rows))
        column_totals = list(map(sum, zip(*rows)))
        total = sum(row_totals)
        chi = 0
        for i, row in enumerate(rows):
            for j, observed in enumerate(row):
                expected = row_totals[i] * column_totals[j] / total
                chi += (observed - expected)**2 / expected
        return [chi, (len(rows) - 1) * (len(rows[0]) - 1)]
    raise ValueError(f'No computation for question {index}')

def verify(questions):
    expected_ids = {f'm2-t3-q{i}' for i in range(1, 16)}
    numerical_ids = {qid for qid, q in questions.items() if qid.startswith(('m1-', 'm2-')) and q['type'] == 'numerical'}
    if numerical_ids != expected_ids:
        raise ValueError(f'Numerical coverage mismatch: {numerical_ids ^ expected_ids}')
    results = []
    for i in range(1, 16):
        qid = f'm2-t3-q{i}'
        q = questions[qid]
        expected = compute(i, q['prompt'])
        actual = numbers(q['answer'])
        passed = len(expected) == len(actual) and all(math.isclose(a, b, rel_tol=0, abs_tol=0.000051) for a, b in zip(expected, actual))
        results.append({'id': qid, 'expected': expected, 'actual': actual, 'passed': passed})
    return results

if __name__ == '__main__':
    root = Path(__file__).resolve().parent
    modules = [json.loads((root / f'data/da/modules/m{i}.json').read_text(encoding='utf-8')) for i in (1, 2)]
    questions = {q['id']: q for m in modules for t in m['tests'] for q in t['questions']}
    result = verify(questions)
    print(json.dumps(result, indent=2))
    if not all(row['passed'] for row in result):
        raise SystemExit('Numerical answer mismatch')
