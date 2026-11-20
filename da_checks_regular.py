"""Recompute numerical solutions to the visually transcribed 2025 regular paper.

All input data are read from displayed prompts. Incomplete source questions are
checked only to the extent that their printed inputs determine an answer.
"""
import itertools
import json
import math
import re
import statistics
from collections import Counter
from pathlib import Path

NUM = r'[-+]?\d+(?:\.\d+)?'
NUMERICAL = {'1A', '1B', '2A', '2B', '3A', '3B', '3C', '4A', '4B', '5A', '5B', '5C'}

def nums(text):
    return [float(x) for x in re.findall(NUM, text)]

def value(text, label):
    match = re.search(re.escape(label) + r'\s*=\s*(' + NUM + ')', text, re.I)
    if not match:
        raise ValueError(f'Missing answer/input label {label!r}')
    return float(match.group(1))

def tables(text):
    blocks, block = [], []
    for line in text.splitlines() + ['']:
        if line.startswith('|'):
            block.append([cell.strip() for cell in line.strip('|').split('|')])
        elif block:
            blocks.append(block[2:])
            block = []
    return blocks

def close(expected, actual):
    if isinstance(expected, dict):
        return isinstance(actual, dict) and expected.keys() == actual.keys() and all(close(v, actual[k]) for k, v in expected.items())
    if isinstance(expected, (list, tuple)):
        return isinstance(actual, (list, tuple)) and len(expected) == len(actual) and all(close(a, b) for a, b in zip(expected, actual))
    if isinstance(expected, bool):
        return expected is actual
    if isinstance(expected, (int, float)):
        return isinstance(actual, (int, float)) and math.isclose(expected, actual, rel_tol=0, abs_tol=0.0000006)
    return expected == actual

def item_counts(transactions, size):
    items = sorted(set.union(*transactions))
    return {tuple(c): sum(set(c) <= t for t in transactions) for c in itertools.combinations(items, size)}

def evaluate(number, q):
    p, a = q['prompt'], q['answer']
    if number == '1A':
        transactions = [set(row[1].split(', ')) for row in tables(p)[0]]
        threshold = int(value(p, 'min support count'))
        singles = {c[0]: n for c, n in item_counts(transactions, 1).items()}
        l1 = {k for k, n in singles.items() if n >= threshold}
        pairs = {'+'.join(c): n for c, n in item_counts(transactions, 2).items() if set(c) <= l1}
        pair_counts = item_counts(transactions, 2)
        l2 = {c: n for c, n in pair_counts.items() if n >= threshold}
        triples = {c: n for c, n in item_counts(transactions, 3).items() if all(tuple(pair) in l2 for pair in itertools.combinations(c, 2))}
        rules = {}
        for c, count in l2.items():
            for x, y in (c, c[::-1]):
                if count / singles[x] >= value(p, 'min_conf') / 100:
                    rules[f'{x} → {y}'] = [count / len(transactions) * 100, count / singles[x] * 100]
        new_threshold = float(re.search(r'min_sup changes to (\d+)', p).group(1))
        expected = {'singles': singles, 'pairs': pairs, 'rules': rules,
                    'empty_c3': not triples, 'none_drop': all(n >= new_threshold for n in list(l2.values()) + [singles[k] for k in l1])}
        actual_singles = {}
        for item in singles:
            actual_singles[item] = float(re.search(r'(?<![+\w])' + item + r' = (' + NUM + ')', a).group(1))
        actual = {'singles': actual_singles, 'pairs': {k: value(a, k) for k in pairs},
                  'rules': {row[0]: [float(row[1]), float(row[2])] for row in tables(a)[0]},
                  'empty_c3': 'C3 and L3 are empty' in a,
                  'none_drop': 'no previously frequent itemset drops' in a}
        return expected, actual
    if number == '1B':
        claimed = float(re.search(r'accuracy rate of (' + NUM + ')%', p).group(1))
        mean = float(re.search(r'average accuracy of (' + NUM + ')%', p).group(1))
        n = float(re.search(r'sample of (\d+) test kits', p).group(1))
        sigma = float(re.search(r'standard deviation of (' + NUM + ')', p).group(1))
        z_prop = ((mean - claimed) / 100) / (sigma / math.sqrt(n))
        z_pct = (mean - claimed) / (sigma / math.sqrt(n))
        expected = {'z': [z_prop, z_pct], 'unit_caveat': True, 'fail_reject_proportion': abs(z_prop) < 1.96}
        actual = {'z': [float(v) for v in re.findall(r'z = (' + NUM + ')', a)],
                  'unit_caveat': 'percentage points' in a and 'does not specify' in a,
                  'fail_reject_proportion': 'Fail to reject' in a}
        return expected, actual
    if number == '2A':
        rows = tables(p)[0]
        observed = [[float(row[1]), float(row[2])] for row in rows[:-1]]
        rt = list(map(sum, observed)); ct = list(map(sum, zip(*observed))); n = sum(rt)
        chi = sum((o-rt[i]*ct[j]/n)**2/(rt[i]*ct[j]/n) for i, row in enumerate(observed) for j,o in enumerate(row))
        expected = [chi, (len(rt)-1)*(len(ct)-1), observed[0][0]/rt[0]*100, observed[1][0]/rt[1]*100]
        actual = [value(a, k) for k in ('Pearson chi-square', 'df', 'Vaccinated attack rate', 'unvaccinated attack rate')]
        return expected, actual
    if number == '2B':
        txs = [re.findall(r'[A-F]', s) for s in re.findall(r': \{([A-F, ]+)\}', p)]
        multiplier = int(re.search(r'order\(x\) × (\d+)', p).group(1))
        modulus = int(re.search(r'\\bmod (\d+)', p).group(1))
        threshold = int(re.search(r'minimum support is (\d+)', p).group(1))
        buckets = {str(i): Counter() for i in range(modulus)}
        for tx in txs:
            for x,y in itertools.combinations(sorted(tx), 2):
                h = ((ord(x)-ord('A')+1)*multiplier + ord(y)-ord('A')+1) % modulus
                buckets[str(h)][x+y] += 1
        expected = {'buckets': {k: {'count': sum(v.values()), 'contents': dict(v)} for k,v in buckets.items()},
                    'pruned': [int(k) for k,v in buckets.items() if sum(v.values()) < threshold]}
        actual = {'buckets': {row[0]: {'count': float(row[1]), 'contents': {k:int(v) for k,v in re.findall(r'([A-F]{2}) × (\d+)', row[2])}} for row in tables(a)[0]},
                  'pruned': nums(re.search(r'Prune buckets ([^.]+)', a).group(1))}
        return expected, actual
    if number == '3A':
        x = nums(p.split('data:', 1)[1].split('ii.', 1)[0])
        n = len(x); mean = statistics.mean(x); sd = statistics.stdev(x); pop = statistics.pstdev(x)
        moment = sum((v-mean)**3 for v in x)/n/pop**3
        adjusted = n/((n-1)*(n-2))*sum(((v-mean)/sd)**3 for v in x)
        groups = [list(map(float, col)) for col in zip(*tables(p)[0])]
        means = list(map(statistics.mean, groups)); total = sum(map(len, groups)); grand = statistics.mean([v for g in groups for v in g])
        ssb = sum(len(g)*(m-grand)**2 for g,m in zip(groups, means))
        ssw = sum(sum((v-m)**2 for v in g) for g,m in zip(groups, means))
        df1 = len(groups)-1; df2 = total-len(groups)
        expected = [sd, adjusted, pop, moment, (ssb/df1)/(ssw/df2), df1, df2] + means
        actual = [value(a,k) for k in ('Sample SD', 'Adjusted Fisher-Pearson sample skewness', 'population SD', 'moment skewness', 'F', 'numerator df', 'denominator df', 'A', 'B', 'C')]
        return expected, actual
    if number == '3B':
        n = float(re.search(r'contains (\d+) transactions', p).group(1))
        both = float(re.search(r'(\d+) transactions include both', p).group(1))
        pen = float(re.search(r'(\d+) transactions include \{Pen\}', p).group(1))
        return [both/n*100,both/pen*100], [value(a,'Support'),value(a,'confidence')]
    if number == '3C':
        values = nums(p.split('weeks:',1)[1].split('.',1)[0])
        window = int(re.search(r'the (\d+)-week Simple',p).group(1))
        return [statistics.mean(values[-window:])], [value(a,'SMA forecast for week 6')]
    if number == '4A':
        rows = tables(p)[0]
        txs = {int(row[0]): set(row[1].split(', ')) for row in rows}
        items = sorted(set.union(*txs.values()))
        threshold = int(re.search(r'minimum support of (\d+)', p).group(1))
        expected = {}
        for size in range(1,len(items)+1):
            for combo in itertools.combinations(items,size):
                tids = sorted(tid for tid,tx in txs.items() if set(combo)<=tx)
                if len(tids)>=threshold:
                    expected[''.join(combo)] = {'tids':tids,'count':len(tids)}
        actual = {row[0]: {'tids':nums(row[1]),'count':float(row[2])} for table in tables(a) for row in table}
        return expected,actual
    if number == '4B':
        sales = [float(row[1]) for row in tables(p)[0]]
        alpha = value(p,'α')
        initial = float(re.search(r'forecast for Month 1 is ('+NUM+')',p).group(1))
        forecast = [initial]
        for sale in sales:
            forecast.append(alpha*sale+(1-alpha)*forecast[-1])
        errors = [abs(sales[i]-forecast[i]) for i in range(1,len(sales))]
        expected = {'forecasts':{str(i+1):v for i,v in enumerate(forecast) if i>0},'mae':statistics.mean(errors)}
        actual = {'forecasts':{row[0]:float(row[1]) for row in tables(a)[0]},'mae':value(a,'MAE for months 2–5')}
        return expected,actual
    if number == '5A':
        y = [float(row[2]) for row in tables(p)[0]]
        def holt(alpha,beta):
            level,trend=y[0],y[1]-y[0]
            for observation in y[1:]:
                previous=level
                level=alpha*observation+(1-alpha)*(level+trend)
                trend=beta*(level-previous)+(1-beta)*trend
            return level+2*trend
        missing = not re.search(r'(?:α|β|alpha|beta)\s*=\s*\d',p)
        expected = {'initial':[y[0],y[1]-y[0]],'underdetermined':missing and not math.isclose(holt(.2,.1),holt(.8,.5))}
        actual = {'initial':[value(a,'Initial level'),value(a,'initial trend')],
                  'underdetermined':'not uniquely determined' in a and 'omits both smoothing constants' in a and 'F7 = L5 + 2T5' in a}
        return expected,actual
    if number == '5B':
        n = float(re.search(r'analysed ([\d,]+) customer',p).group(1).replace(',',''))
        ca,cb,cab = [float(row[1]) for row in tables(p)[0]]
        return [cab*n/(ca*cb),.5*(cab/ca+cab/cb),cab/math.sqrt(ca*cb)], [value(a,k) for k in ('Lift','Kulc','cosine')]
    if number == '5C':
        x = nums(re.search(r'\[([^]]+)\]',p).group(1))
        k = int(re.search(r'with (\d+) bins',p).group(1))
        x.sort();width=(max(x)-min(x))/k
        ew=[[v for v in x if min(x)+i*width<=v and (v<min(x)+(i+1)*width or i==k-1)] for i in range(k)]
        ef=[x[i*len(x)//k:(i+1)*len(x)//k] for i in range(k)]
        expected={'width':width,'equal_width':[[vs,len(vs)] for vs in ew],'equal_frequency':[[vs,len(vs)] for vs in ef]}
        first,second=tables(a)
        actual={'width':value(a,'Equal-width bin width'),'equal_width':[[nums(r[1]),float(r[2])] for r in first],
                'equal_frequency':[[nums(r[1]),float(r[2])] for r in second]}
        return expected,actual
    raise ValueError(f'No numerical computation for {number}')

def verify(questions):
    found={qid.removeprefix('2025-reg-') for qid,q in questions.items() if qid.startswith('2025-reg-') and q['type']=='numerical'}
    if found != NUMERICAL:
        raise ValueError(f'Regular-paper numerical coverage mismatch: {found ^ NUMERICAL}')
    results=[]
    for number in sorted(NUMERICAL):
        qid='2025-reg-'+number
        expected,actual=evaluate(number,questions[qid])
        results.append({'id':qid,'expected':expected,'actual':actual,'passed':close(expected,actual)})
    return results

if __name__=='__main__':
    root=Path(__file__).resolve().parent
    paper=json.loads((root/'data/da/papers/2025-reg.json').read_text(encoding='utf-8'))
    results=verify({q['id']:q for q in paper['questions']})
    print(json.dumps(results,ensure_ascii=False,indent=2))
    if not all(row['passed'] for row in results):
        raise SystemExit('Regular-paper numerical verification failed')
