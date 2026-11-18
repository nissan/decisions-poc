"""Use the typed Decisions endpoint without dispatch capability."""
from copy import deepcopy
import json
import math
import time
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener

from .policy import nonnegative_int, recommendation, review

MODEL = 'gemini-decision-1'
URL = 'https://generativelanguage.googleapis.com/v1beta/decisions'
MAX_RESPONSE = 256 * 1024
MIN_FIT = 0.80
MIN_CLEAR = 0.75


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # A redirect must not forward the API key to a different origin.
        return None


def request_body(case, eligible, template):
    questions = deepcopy(template)
    ordered = sorted(eligible.values(), key=lambda lane: (lane.cost, lane.id))
    for rank, lane in enumerate(ordered, 1):
        questions['lane_fit']['criteria'][lane.id] = lane.description(rank)
    task = {key: case[key] for key in ('type', 'outcome', 'acceptance', 'tools', 'min_effort') if key in case}
    return {'model': MODEL, 'input': json.dumps(task, ensure_ascii=False), 'questions': questions}


def _probability(value):
    if type(value) not in (float, int) or not 0 <= value <= 1:
        raise ValueError('invalid probability')
    return value


def _near(left, right, tolerance=0.011):
    if not math.isclose(left, right, rel_tol=0, abs_tol=tolerance):
        raise ValueError('inconsistent response values')


def _distribution(values, expected):
    if not isinstance(values, dict) or values.keys() != expected:
        raise ValueError('unexpected probability options')
    for value in values.values():
        _probability(value)
    _near(sum(values.values()), 1.0, 0.0051 * len(expected))
    return values


def interpret(reply, eligible):
    answers = reply['answers']
    fit, clear, complexity = (answers[key] for key in ('lane_fit', 'task_clear', 'complexity'))
    if [a['type'] for a in (fit, clear, complexity)] != ['choice', 'noul', 'score']:
        raise ValueError('unexpected answer type')
    choice = fit['choice']
    probabilities = _distribution(fit['probabilities'], eligible.keys() | {'review'})
    confidence = _probability(fit['confidence'])
    if probabilities[choice] < max(probabilities.values()):
        raise ValueError('choice is not a top option')
    _near(confidence, probabilities[choice])
    positive = _probability(clear['noul'])
    if not 0.01 <= positive <= 0.99:
        raise ValueError('noul outside documented bounds')
    _near(_probability(clear['confidence']), max(positive, 1 - positive))
    levels = _distribution(complexity['probabilities'], {'0', '1', '2'})
    legend = complexity['legend']
    if not isinstance(legend, dict) or legend.keys() != levels.keys() or not all(isinstance(x, str) for x in legend.values()):
        raise ValueError('invalid score legend')
    score = complexity['score']
    if type(score) not in (float, int) or not 0 <= score <= 2:
        raise ValueError('score out of bounds')
    _near(score, sum(int(level) * p for level, p in levels.items()), 0.021)
    _near(_probability(complexity['confidence']), max(levels.values()))
    usage = reply['usage']
    input_tokens, output_tokens = usage['total_input_tokens'], usage['total_output_tokens']
    if not nonnegative_int(input_tokens) or type(output_tokens) is not int or output_tokens != 0:
        raise ValueError('invalid Decisions usage')
    if choice == 'review':
        result = review('model selected review')
    elif min(confidence, probabilities[choice]) < MIN_FIT:
        result = review('low lane-fit confidence')
    elif positive < MIN_CLEAR:
        result = review('insufficient evidence of task clarity')
    else:
        result = recommendation(eligible[choice], 'typed answer passed thresholds')
    return result | {
        'answers': {
            'lane_fit': {'choice': choice, 'confidence': confidence, 'probabilities': probabilities},
            'task_clear': {'p_yes': positive, 'confidence': clear['confidence']},
            'complexity': {'score': score, 'probabilities': levels, 'legend': legend, 'confidence': complexity['confidence']},
        },
        'usage': {'input_tokens': input_tokens, 'output_tokens': output_tokens},
    }


def _round_trip(body, api_key):
    request = Request(URL, json.dumps(body, ensure_ascii=False).encode('utf-8'),
                      {'x-goog-api-key': api_key, 'Content-Type': 'application/json'}, method='POST')
    with build_opener(NoRedirect()).open(request, timeout=20) as response:
        wire = response.read(MAX_RESPONSE + 1)
    if len(wire) > MAX_RESPONSE:
        raise ValueError('response exceeds size limit')
    return json.loads(wire)


def advise(case, eligible, template, api_key, *, round_trip=_round_trip):
    if not eligible:
        return review('no eligible lane') | {'request_attempted': False}
    if not case['outcome'].strip() or not case['acceptance'].strip():
        return review('missing outcome or acceptance') | {'request_attempted': False}
    if not api_key:
        return {'status': 'not-run', 'reason': 'no Gemini credential supplied', 'request_attempted': False}
    start = time.perf_counter()
    try:
        result = interpret(round_trip(request_body(case, eligible, template), api_key), eligible)
    except HTTPError as error:
        error.close()
        result = {'status': 'provider-error', 'reason': f'HTTP {error.code}'}
    except (OSError, URLError):
        result = {'status': 'provider-error', 'reason': 'connection or timeout'}
    except (ValueError, KeyError, TypeError, AttributeError):
        result = {'status': 'provider-error', 'reason': 'malformed Decisions reply'}
    return result | {'request_attempted': True, 'elapsed_ms': round((time.perf_counter() - start) * 1000, 3)}
