"""Policy and cost projections. Neither arm can change eligibility."""
from dataclasses import dataclass
import json
from pathlib import Path

FIXTURES = Path(__file__).resolve().parent.parent / 'fixtures'
TIERS = ('cheap', 'mid', 'high', 'frontier')
EFFORTS = ('low', 'medium', 'high')
BASELINE = {'side': ('cheap', 'low'), 'fix': ('mid', 'medium'),
            'analysis': ('high', 'medium'), 'frontier': ('frontier', 'high')}
FAMILY_CAP = 5


def fixture(name):
    return json.loads((FIXTURES / f'{name}.json').read_text(encoding='utf-8'))


@dataclass(frozen=True)
class Lane:
    id: str
    provider: str
    model: str
    effort: str
    tier: str
    tools: tuple[str, ...]
    cost: int

    def description(self, rank):
        return (f'{self.provider}/{self.model}, reasoning {self.effort}, {self.tier} tier, '
                f'tools {", ".join(self.tools)}, cost rank {rank}.')


def nonnegative_int(value):
    return type(value) is int and value >= 0


def eligibility(case, catalog):
    default = catalog['default']
    snapshot = default | case.get('snapshot', {})
    budget, approved = snapshot['budget_micro_usd'], snapshot['approved']
    if not nonnegative_int(budget):
        return {}, {'policy': 'unknown budget'}
    if not isinstance(approved, list):
        return {}, {'policy': 'unknown allowlist'}
    aliases, entries = catalog['aliases'], catalog['lanes']
    allowed = {aliases.get(key, key) for key in approved}
    if unknown := allowed - entries.keys():
        return {}, {'policy': f'unresolved approved lane: {", ".join(sorted(unknown))}'}
    families = default['families'] | snapshot['families']
    required_tools = set(case['tools'])
    min_effort = EFFORTS.index(case.get('min_effort', 'low'))
    eligible, excluded = {}, {}
    for key, lane in entries.items():
        provider = lane['provider']
        family = families.get(provider, {})
        quota, active = family.get('quota_tokens'), family.get('active')
        tokens = (2500, 700, lane['reasoning_tokens'])
        cost = sum(count * rate for count, rate in zip(tokens, lane['rates'], strict=True))
        # Reserve at 150% of projected usage; all values are nonnegative integers.
        reserve_cost = (3 * cost + 1) // 2
        reserve_tokens = (3 * sum(tokens) + 1) // 2
        if key not in allowed:
            reason = 'not approved'
        elif not required_tools.issubset(lane['tools']) or EFFORTS.index(lane['effort']) < min_effort:
            reason = 'missing required tools or reasoning level'
        elif not nonnegative_int(quota) or not nonnegative_int(active):
            reason = 'unknown admission'
        elif quota < reserve_tokens:
            reason = 'insufficient quota'
        elif active >= FAMILY_CAP:
            reason = 'provider family at capacity'
        elif budget < reserve_cost:
            reason = 'insufficient budget'
        else:
            eligible[key] = Lane(key, provider, lane['model'], lane['effort'], lane['tier'], tuple(lane['tools']), cost)
            continue
        excluded[key] = reason
    return eligible, excluded


def recommendation(lane, reason):
    return {'status': 'suggest', 'lane': lane.id, 'provider': lane.provider, 'model': lane.model,
            'reasoning': lane.effort, 'forecast_micro_usd': lane.cost, 'reason': reason}


def review(reason):
    return {'status': 'review', 'reason': reason}


def baseline(case, eligible):
    if not eligible:
        return review('no eligible lane')
    if not case['outcome'].strip() or not case['acceptance'].strip():
        return review('missing outcome or acceptance')
    tier, effort = BASELINE[case['type']]
    matches = [lane for lane in eligible.values()
               if TIERS.index(lane.tier) >= TIERS.index(tier)
               and EFFORTS.index(lane.effort) >= EFFORTS.index(effort)]
    if not matches:
        return review('no eligible lane meets the rule floor')
    return recommendation(min(matches, key=lambda lane: (lane.cost, lane.id)), f'rule floor: {tier}/{effort}')
