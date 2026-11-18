"""Smoke the OpenAI Decisions and sponsored Jev adapters on synthetic development cases."""
import argparse
import hashlib
import json
import os
from pathlib import Path
from time import perf_counter
from urllib.error import HTTPError
from urllib.request import Request, build_opener

from .decisions import MAX_RESPONSE, MIN_CLEAR, MIN_FIT, NoRedirect, _distribution, _probability, request_body
from .policy import eligibility, fixture, nonnegative_int, recommendation, review

PROVIDERS = {
    'openai': ('https://api.openai.com/v1/decisions', 'gpt-6-luna', 'OPENAI_API_KEY'),
    'jev': ('https://opencode.ai/inference/systemone/v1/systemone', 'jev-1.13-free', 'OPENCODE_API_KEY'),
}


def encode(provider, case, eligible, template):
    # The current-practice protocol excludes the old diagnostic's task-type hint.
    body = request_body(case, eligible, template)
    task = json.loads(body['input'])
    task.pop('type', None)
    shared = json.dumps(task, ensure_ascii=False)
    model = PROVIDERS[provider][1]
    questions = body['questions']
    if provider == 'jev':
        return {'model': model, 'state': shared, 'questions': questions}
    fit, clear, complexity = (questions[k] for k in ('lane_fit', 'task_clear', 'complexity'))
    clarity = clear['criteria']
    return {'model': model, 'input': shared, 'questions': [
        {'name': 'lane_fit', 'type': 'choice', 'instructions': fit['instructions'],
         'choices': [{'value': key, 'description': value} for key, value in fit['criteria'].items()]},
        {'name': 'task_clear', 'type': 'predicate',
         'instructions': f"{clear['instructions']} Yes: {clarity['true_description']} No: {clarity['false_description']}"},
        {'name': 'complexity', 'type': 'score', 'instructions': complexity['instructions'],
         'levels': [{'label': level, 'description': level} for level in complexity['criteria']]},
    ]}


def _pairs(rows, key):
    values = {}
    for row in rows:
        name = row[key]
        if name in values:
            raise ValueError(f'duplicate {key}')
        values[name] = row
    return values


def decode(provider, reply, eligible):
    is_openai = provider == 'openai'
    model = reply['model']
    if not isinstance(model, str) or not model.startswith('gpt-6-luna' if is_openai else 'jev-1.13'):
        raise ValueError('unexpected served model')
    answers = _pairs(reply['answers'], 'name') if is_openai else reply['answers']
    if answers.keys() != {'lane_fit', 'task_clear', 'complexity'}:
        raise ValueError('unexpected answers')
    fit, clear, complexity = (answers[k] for k in ('lane_fit', 'task_clear', 'complexity'))
    if (fit['type'], clear['type'], complexity['type']) != ('choice', 'predicate' if is_openai else 'noul', 'score'):
        raise ValueError('unexpected answer types')
    probabilities, level_probabilities = fit['probabilities'], complexity['probabilities']
    if is_openai:
        probabilities = {key: val['probability'] for key, val in _pairs(probabilities, 'value').items()}
        level_probabilities = {str(key): val['probability'] for key, val in _pairs(level_probabilities, 'value').items()}
    distribution = _distribution(probabilities, eligible.keys() | {'review'})
    _distribution(level_probabilities, {'0', '1', '2'})
    choice = fit['choice']
    chance = distribution[choice]
    if chance < max(distribution.values()):
        raise ValueError('choice is not a top option')
    positive = _probability(clear['probability' if is_openai else 'noul'])
    _probability(fit['confidence'])
    _probability(complexity['confidence'])
    score = complexity['score']
    if type(score) not in (int, float) or not 0 <= score <= 2:
        raise ValueError('invalid complexity score')
    usage = {key: reply['usage'][key] for key in ('input_tokens', 'output_tokens')}
    if not all(nonnegative_int(val) for val in usage.values()):
        raise ValueError('invalid token counts')
    categorical = choice if positive > 0.5 else 'review'
    if choice == 'review' or chance < MIN_FIT or positive < MIN_CLEAR:
        result = review('explicit review or shared probability thresholds not met')
    else:
        result = recommendation(eligible[choice], 'typed probabilities passed thresholds')
    return result | {'served_model': model, 'categorical': categorical, 'usage': usage, 'answers': answers}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('provider', choices=PROVIDERS)
    parser.add_argument('--case', default='D02')
    parser.add_argument('--confirmed-no-additional-spend', action='store_true', required=True)
    parser.add_argument('--json', required=True, type=Path, metavar='NEW_RECEIPT')
    args = parser.parse_args()
    url, requested, env = PROVIDERS[args.provider]
    key = os.environ.get(env, '').strip()
    if not key:
        parser.error(f'{env} is not configured')
    case = next((x for x in fixture('cases') if x['id'] == args.case and x['split'] == 'dev'), None)
    if case is None:
        parser.error('case must be in the public development split')
    eligible, _ = eligibility(case, fixture('lanes'))
    if not eligible or not case['outcome'].strip() or not case['acceptance'].strip():
        parser.error('case cannot reach a provider under local eligibility rules')
    packet = json.dumps(encode(args.provider, case, eligible, fixture('questions'))).encode()
    request = Request(url, packet,
                      {'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'}, method='POST')
    with args.json.open('x', encoding='utf-8') as output:
        start = perf_counter()
        try:
            with build_opener(NoRedirect()).open(request, timeout=20) as response:
                wire = response.read(MAX_RESPONSE + 1)
            if len(wire) > MAX_RESPONSE:
                raise ValueError('oversized reply')
            result = decode(args.provider, json.loads(wire), eligible)
        except HTTPError as error:
            error.close()
            result = {'status': 'provider-error', 'reason': f'HTTP {error.code}'}
        except OSError:
            result = {'status': 'provider-error', 'reason': 'connection or timeout'}
        except (ValueError, KeyError, TypeError, AttributeError):
            result = {'status': 'provider-error', 'reason': 'invalid or unexpected typed response'}
        elapsed = round((perf_counter() - start) * 1000, 3)
        receipt = result | {'case': args.case, 'provider': args.provider, 'requested_model': requested,
                            'request_sha256': hashlib.sha256(packet).hexdigest(), 'elapsed_ms': elapsed}
        json.dump(receipt, output, indent=2)
        output.write('\n')
    print(f"{args.provider} {args.case}: {result['status']} ({result['reason']}); development smoke only")
    return int(result['status'] == 'provider-error')


if __name__ == '__main__':
    raise SystemExit(main())
