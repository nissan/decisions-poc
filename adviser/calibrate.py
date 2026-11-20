"""Choose per-API thresholds on calibration receipts: zero wrong lanes, then most correct decisions."""
import argparse
import json
from pathlib import Path


def signals(row):
    """Return (top lane, P(lane), P(clear)) from a typed receipt row, or None when no model was asked."""
    answers = row.get('answers')
    if not answers:
        return None
    if isinstance(answers, list):  # OpenAI Decisions
        answers = {a['name']: a for a in answers}
    fit, clear = answers['lane_fit'], answers['task_clear']
    probs = fit['probabilities']
    if isinstance(probs, list):
        probs = {p['value']: p['probability'] for p in probs}
    p_clear = clear.get('p_yes', clear.get('noul', clear.get('probability')))
    return fit['choice'], probs[fit['choice']], p_clear


def decide(sig, fit, clear):
    if sig is None:
        return 'review'
    lane, p_lane, p_clear = sig
    return lane if lane != 'review' and p_lane >= fit and p_clear >= clear else 'review'


def outcome(decision, acceptable):
    if decision == 'review':
        return 'correct' if 'review' in acceptable else 'avoidable-review'
    return 'correct' if decision in acceptable else 'wrong'


def calibrate(cases):
    grid = [round(0.30 + 0.05 * i, 2) for i in range(14)]
    best = None
    for fit in grid:
        for clear in grid:
            tally = {'correct': 0, 'wrong': 0, 'avoidable-review': 0}
            for sig, acceptable in cases:
                tally[outcome(decide(sig, fit, clear), acceptable)] += 1
            key = (tally['wrong'] == 0, tally['correct'], fit, clear)
            if best is None or key > best[0]:
                best = (key, {'min_fit': fit, 'min_clear': clear, **tally})
    return best[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pair', nargs=2, action='append', metavar=('RECEIPT', 'LABELS'), required=True,
                        help='receipt JSON and labels JSON ({case: acceptable list}) for one calibration slice')
    args = parser.parse_args()
    cases = []
    for receipt, labels in args.pair:
        rows = json.loads(Path(receipt).read_text())['rows']
        gold = json.loads(Path(labels).read_text())
        cases += [(signals(r), gold[r['case']]) for r in rows]
    print(json.dumps(calibrate(cases) | {'cases': len(cases)}))


if __name__ == '__main__':
    main()
