"""Score locked routing receipts against a separately sealed label file."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path


CORRECT = {'acceptable', 'necessary-review'}


def index(rows):
    result = {}
    for row in rows:
        case = row['case']
        if case in result:
            raise ValueError(f'duplicate receipt: {case}')
        result[case] = row
    return result


def classify(row, case):
    if row is None:
        return 'not-run'
    status = row['status']
    gold = case['acceptable']
    if status == 'suggest':
        lane = row['lane']
        if lane not in case['eligible']:
            return 'ineligible'
        if type(case['eligible'][lane]) is not int or case['eligible'][lane] < 0:
            raise ValueError('invalid executor forecast')
        return 'acceptable' if lane in gold else 'wrong-suggestion'
    if status == 'review':
        return 'necessary-review' if 'review' in gold else 'avoidable-review'
    if status in ('provider-error', 'not-run'):
        return status
    raise ValueError(f'unknown receipt status: {status}')


def compare(labels, baseline, comparator):
    gold, before, after = map(index, (labels, baseline, comparator))
    if not gold or (before.keys() | after.keys()) - gold.keys():
        raise ValueError('empty label set or receipt outside the sealed cohort')
    counts = {'current_practice': Counter(), 'comparator': Counter()}
    gains, regressions, violations, missing = [], [], [], []
    matched = baseline_cost = comparator_cost = 0
    for key, case in gold.items():
        left, right = before.get(key), after.get(key)
        b, c = classify(left, case), classify(right, case)
        counts['current_practice'][b] += 1
        counts['comparator'][c] += 1
        if c == 'ineligible':
            violations.append(key)
        if {b, c} & {'not-run', 'provider-error'}:
            missing.append(key)
            continue
        if b in CORRECT and c not in CORRECT:
            regressions.append(key)
        if b == 'avoidable-review' and c == 'acceptable':
            gains.append(key)
        if b == c == 'acceptable':
            old, new = (case['eligible'][row['lane']] for row in (left, right))
            matched += 1
            baseline_cost += old
            comparator_cost += new
            if new < old:
                gains.append(key)
    return {'cases': len(gold), 'counts': counts, 'gains': gains, 'regressions': regressions,
            'ineligible_suggestions': violations, 'incomplete_pairs': missing,
            'draft_verdict': ('inconclusive' if missing else 'no-go' if violations or regressions or len(gains) < 2 else 'pass'),
            'matched_acceptable_forecast': {'cases': matched, 'current_practice_micro_usd': baseline_cost,
                                            'comparator_micro_usd': comparator_cost} if matched else None}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--labels', type=Path, required=True)
    parser.add_argument('--label-digest', required=True)
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--comparator', type=Path, required=True)
    args = parser.parse_args()
    try:
        paths = (args.labels, args.baseline, args.comparator)
        data = [path.read_bytes() for path in paths]
        digests = [hashlib.sha256(item).hexdigest() for item in data]
        if digests[0] != args.label_digest:
            raise ValueError('label file does not match the sealed digest')
        result = compare(*(json.loads(item) for item in data))
    except (OSError, ValueError, TypeError, KeyError) as error:
        parser.error(str(error))
    print(json.dumps(result | {'input_sha256': dict(zip(('labels', 'baseline', 'comparator'), digests))}, indent=2))


if __name__ == '__main__':
    main()
