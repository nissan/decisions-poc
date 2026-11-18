"""Run the shadow adviser on versioned synthetic fixtures only."""
import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
from statistics import median

from .decisions import MODEL, advise
from .policy import FIXTURES, baseline, eligibility, fixture


def assess(result, gold):
    status = result['status']
    if status == 'suggest':
        return 'acceptable' if result['lane'] in gold else 'wrong-suggestion'
    if status == 'review':
        return 'necessary-review' if 'review' in gold else 'avoidable-review'
    return status


def summarize(rows):
    arms = {name: dict(Counter(row[name]['assessment'] for row in rows))
            for name in ('rules', 'gemini')}
    paired = []
    gains, regressions, violations = [], [], []
    complete = True
    for row in rows:
        rules, gemini = row['rules'], row['gemini']
        r, g = rules['assessment'], gemini['assessment']
        if g in ('not-run', 'provider-error'):
            complete = False
            continue
        if gemini['status'] == 'suggest' and gemini['lane'] not in row['eligible']:
            violations.append(row['case'])
        if r in ('acceptable', 'necessary-review') and g not in ('acceptable', 'necessary-review'):
            regressions.append(row['case'])
        if r == 'avoidable-review' and g == 'acceptable':
            gains.append(row['case'])
        if r == g == 'acceptable':
            paired.append((rules['forecast_micro_usd'], gemini['forecast_micro_usd']))
            if paired[-1][1] < paired[-1][0]:
                gains.append(row['case'])
    attempted = [row['gemini'] for row in rows if row['gemini']['request_attempted']]
    metered = [arm['usage'] for arm in attempted if 'usage' in arm]
    costs = {name: sum(pair[index] for pair in paired) for index, name in enumerate(('rules', 'gemini'))}
    return {
        'cases': len(rows), 'arms': arms, 'gains': gains, 'regressions': regressions,
        'policy_violations': violations,
        'draft_pass_rule': ('inconclusive' if not complete or not attempted else
                            'pass' if not regressions and not violations and len(gains) >= 2 else 'no-go'),
        'common_correct_routes': len(paired),
        'forecast_executor_cost_micro_usd': costs if paired else None,
        'forecast_sensitivity_micro_usd': {k: [v // 2, (3 * v + 1) // 2] for k, v in costs.items()} if paired else None,
        'classifier': {
            'attempted': len(attempted), 'metered': len(metered),
            'median_reply_ms': median(arm['elapsed_ms'] for arm in attempted) if attempted else None,
            'input_tokens': sum(usage['input_tokens'] for usage in metered) if metered else None,
            'output_tokens': sum(usage['output_tokens'] for usage in metered) if metered else None,
        },
    }


def evaluate(cases, catalog, questions, api_key=None):
    rows = []
    stopped = False
    for case in cases:
        eligible, excluded = eligibility(case, catalog)
        rules = baseline(case, eligible)
        if stopped:
            gemini = {'status': 'not-run', 'reason': 'stopped after provider failure', 'request_attempted': False}
        else:
            gemini = advise(case, eligible, questions, api_key)
            stopped = gemini['status'] == 'provider-error'
        gold = case['gold']
        rows.append({'case': case['id'], 'gold': gold, 'eligible': sorted(eligible), 'excluded': excluded,
                     'rules': rules | {'assessment': assess(rules, gold)},
                     'gemini': gemini | {'assessment': assess(gemini, gold)}})
    return rows


def provenance():
    files = [*Path(__file__).parent.glob('*.py'), *FIXTURES.glob('*.json')]
    return {f'{path.parent.name}/{path.name}': hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(files)}


def compact(report):
    counts = report['summary']
    lines = [f"MODE: {report['mode']}   CASES: {counts['cases']}   RESULT: {counts['draft_pass_rule']}"]
    for row in report['cases']:
        arms = [row['rules'], row['gemini']]
        sides = [f"{arm['status']}:{arm['lane']}" if 'lane' in arm else f"{arm['status']} ({arm['reason']})"
                 for arm in arms]
        lines.append(f"{row['case']} | RULES: {sides[0]} | GEMINI: {sides[1]}")
        if len(report['cases']) == 1:
            for lane, reason in row['excluded'].items():
                lines.append(f'  {lane}: {reason}')
            details = {key: arms[1][key] for key in ('answers', 'usage', 'elapsed_ms') if key in arms[1]}
            if details:
                lines.append(json.dumps(details, ensure_ascii=False, indent=2))
    lines.append(f"Rules assessment: {counts['arms']['rules']}")
    lines.append(f"Gemini requests: {counts['classifier']['attempted']} ({counts['classifier']['metered']} metered)")
    return '\n'.join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument('--case', help='synthetic fixture ID')
    selection.add_argument('--split', choices=['dev', 'holdout'])
    parser.add_argument('--live', action='store_true', help='confirm configured key is for the free tier and send only synthetic fixtures')
    parser.add_argument('--reviewed-holdout', action='store_true', help='confirm maintainer has reviewed and frozen the protocol and labels')
    parser.add_argument('--json', type=Path, metavar='NEW_FILE', help='write full evidence to a new file; never overwrite')
    args = parser.parse_args(argv)
    cases = fixture('cases')
    selected = [case for case in cases if case['id'] == args.case or case['split'] == args.split]
    if not selected:
        parser.error('unknown fixture ID')
    if args.live and any(c['split'] == 'holdout' for c in selected) and not args.reviewed_holdout:
        parser.error('live holdout needs maintainer approval (--reviewed-holdout)')
    key = (os.environ.get('GEMINI_API_KEY') or '').strip() if args.live else None
    if args.live and not key:
        parser.error('live mode needs GEMINI_API_KEY set locally')
    if args.json and args.json.exists():
        parser.error('output already exists; choose a new file')
    rows = evaluate(selected, fixture('lanes'), fixture('questions'), key)
    result = {'mode': 'live-gemini' if args.live else 'offline-policy-only', 'model': MODEL,
              'source_sha256': provenance(), 'cases': rows, 'summary': summarize(rows)}
    if args.json:
        with args.json.open('x', encoding='utf-8') as out:
            json.dump(result, out, ensure_ascii=False, indent=2)
            out.write('\n')
    print(compact(result))
    if args.live and (any(row['gemini']['status'] == 'provider-error' for row in rows)
                      or not result['summary']['classifier']['attempted']):
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
