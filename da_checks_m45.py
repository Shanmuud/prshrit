"""Independently recompute the numeric answers in the module 4 and 5 bank.

Inputs below reproduce the original practice data stated in each prompt.
Answers are parsed from the supplied question objects, not regenerated or replaced.
Run directly to verify the two module files before integration.
"""
from itertools import combinations
import json
import math
from pathlib import Path
import re


def _itemsets(transactions):
    items = sorted(set().union(*transactions))
    return {frozenset(s): sum(set(s) <= t for t in transactions)
            for size in range(1, len(items) + 1)
            for s in combinations(items, size)}


def _expected():
    expected = {}
    def put(module, test, question, *values):
        expected[f'm{module}-t{test}-q{question}'] = list(values)

    total, a, b, both = 100, 40, 50, 30
    ab, ba = both / a, both / b
    put(4, 3, 1, 100 * both / total, 100 * ab)
    put(4, 3, 2, (both / total) / ((a / total) * (b / total)))
    put(4, 3, 3, min(ab, ba), max(ab, ba))
    put(4, 3, 4, (ab + ba) / 2)
    put(4, 3, 5, both / math.sqrt(a * b))
    put(4, 3, 6, abs(a - b) / (a + b - both))
    counts = _itemsets([set(x) for x in ['AB', 'AB', 'AC', 'ABC', 'BC']])
    put(4, 3, 7, *(sum(len(s) == size and count >= 3 for s, count in counts.items())
                   for size in [1, 2, 3]))
    put(4, 3, 8, len({1, 2, 4, 6} & {2, 3, 4, 6}))
    base = [(set('AB'), 2), (set('A'), 1), (set('B'), 1)]
    put(4, 3, 9, *(sum(weight for path, weight in base if set(s) <= path)
                   for s in ['A', 'B', 'AB']))
    counts = _itemsets([set('AB'), set('AB'), set('A')])
    frequent = {s: count for s, count in counts.items() if count >= 2}
    closed = [s for s, count in frequent.items()
              if not any(s < other and count == n for other, n in counts.items())]
    maximal = [s for s in frequent if not any(s < other for other in frequent)]
    put(4, 3, 10, len(closed), len(maximal))
    observed = [[30, 10], [20, 40]]
    rows = [sum(row) for row in observed]
    cols = [sum(row[c] for row in observed) for c in range(2)]
    n = sum(rows)
    chi = sum((observed[r][c] - rows[r] * cols[c] / n) ** 2 /
              (rows[r] * cols[c] / n) for r in range(2) for c in range(2))
    put(4, 3, 11, chi)
    enlarged = total + 100
    put(4, 3, 12, (both / enlarged) / ((a / enlarged) * (b / enlarged)),
        (ab + ba) / 2)

    series = [10, 12, 14, 18]
    put(5, 2, 1, sum(series[-3:]) / 3)
    put(5, 2, 2, sum(w * y for w, y in zip([.2, .3, .5], series[-3:])))
    put(5, 2, 3, .3 * 120 + .7 * 100)
    forecast = 20
    forecasts = []
    for actual in [20, 24, 22]:
        forecast = .5 * actual + .5 * forecast
        forecasts.append(forecast)
    put(5, 2, 4, *forecasts)
    actuals, forecasts = [100, 200], [90, 220]
    errors = [y - f for y, f in zip(actuals, forecasts)]
    mse = sum(e ** 2 for e in errors) / len(errors)
    put(5, 2, 5, sum(abs(e) for e in errors) / len(errors),
        100 * sum(abs(e) / y for e, y in zip(errors, actuals)) / len(errors),
        mse, math.sqrt(mse))
    old_level, old_trend, actual = 50, 4, 60
    level = .5 * actual + .5 * (old_level + old_trend)
    trend = .25 * (level - old_level) + .75 * old_trend
    put(5, 2, 6, level, trend, level + trend)
    put(5, 2, 7, 80 + 4 * 3)
    years = [[20, 30, 40, 10], [30, 40, 50, 20]]
    seasonal_means = [sum(values) / len(values) for values in zip(*years)]
    overall = sum(seasonal_means) / len(seasonal_means)
    put(5, 2, 8, *(mean / overall for mean in seasonal_means))
    put(5, 2, 9, (100 + 5) * 1.2)
    put(5, 2, 10, (500 - 10 * 20) * 1.2)
    forecast = 10 + 2 * 6
    put(5, 2, 11, forecast, 25 - forecast)
    old_level, old_trend, old_season, actual = 100, 5, 1.2, 132
    level = .5 * actual / old_season + .5 * (old_level + old_trend)
    trend = .5 * (level - old_level) + .5 * old_trend
    season = .5 * actual / level + .5 * old_season
    put(5, 2, 12, level, trend, season)

    series = [10, 13, 17, 22]
    differences = [b - a for a, b in zip(series, series[1:])]
    put(5, 3, 5, *differences)
    put(5, 3, 6, *(b - a for a, b in zip(differences, differences[1:])))
    series = [1, 2, 3, 4]
    mean = sum(series) / len(series)
    deviations = [y - mean for y in series]
    put(5, 3, 7, sum(a * b for a, b in zip(deviations, deviations[1:])) /
        sum(d ** 2 for d in deviations))
    put(5, 3, 8, 1.96 / math.sqrt(100))
    put(5, 3, 11, 5 + .8 * 20)
    put(5, 3, 12, 50 + .4 * -5)
    return expected


def verify(questions):
    expected = _expected()
    numerical = {qid for qid, q in questions.items()
                 if qid.startswith(('m4-', 'm5-')) and q['type'] == 'numerical'}
    if numerical != set(expected):
        raise AssertionError(f'Numerical coverage mismatch: {numerical ^ set(expected)}')
    records = []
    # Only the explicitly requested two-decimal forecast is allowed a cent's rounding.
    tolerances = {'m5-t2-q1': .005}
    for qid, values in expected.items():
        actual = [float(x) for x in re.findall(r'-?\d+(?:\.\d+)?', questions[qid]['answer'])]
        tolerance = tolerances.get(qid, .000051)
        passed = len(actual) == len(values) and all(
            math.isfinite(x) and abs(x - y) <= tolerance for x, y in zip(actual, values))
        records.append({'id': qid, 'expected': values, 'actual': actual, 'passed': passed})
    return records


if __name__ == '__main__':
    root = Path(__file__).resolve().parent
    questions = {}
    for name in ['m4', 'm5']:
        module = json.loads((root / f'data/da/modules/{name}.json').read_text(encoding='utf-8'))
        for test in module['tests']:
            for q in test['questions']:
                questions[q['id']] = q
    results = verify(questions)
    print(json.dumps(results, indent=2))
    if not all(row['passed'] for row in results):
        raise SystemExit(1)
    print(f'PASS: {len(results)} independently recomputed numerical questions')
