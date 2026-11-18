import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

from adviser.__main__ import assess, evaluate, summarize
from adviser.decisions import advise
from adviser.policy import baseline, eligibility, fixture

CATALOG = fixture('lanes')
QUESTIONS = fixture('questions')
CASES = {case['id']: case for case in fixture('cases')}


def typed_reply(body, choice='craft', positive=0.95, fit=0.92):
    options = body['questions']['lane_fit']['criteria']
    return {'answers': {
        'lane_fit': {'type': 'choice', 'choice': choice, 'confidence': fit,
                     'probabilities': {key: fit if key == choice else (1-fit)/(len(options)-1) for key in options}},
        'task_clear': {'type': 'noul', 'noul': positive, 'confidence': max(positive, 1-positive)},
        'complexity': {'type': 'score', 'score': 0.98, 'confidence': 0.90,
                       'probabilities': {'0': 0.06, '1': 0.90, '2': 0.04},
                       'legend': {'0': 'mechanical', '1': 'bounded', '2': 'complex'}},
    }, 'usage': {'total_input_tokens': 234, 'total_output_tokens': 0}}


class AdviserTests(unittest.TestCase):
    def eligible(self, case_id):
        case = CASES[case_id]
        return case, eligibility(case, CATALOG)[0]

    def test_tool_and_reasoning_floor_applies_to_both_arms(self):
        case, lanes = self.eligible('H11')
        self.assertEqual(set(lanes), {'atlas-high'})
        self.assertEqual(baseline(case, lanes)['reasoning'], 'high')

    def test_unknown_capacity_and_budget_do_not_send_a_request(self):
        def unexpected(*_):
            self.fail('sent a request without eligibility')
        for case_id in ('D07', 'D12', 'H07', 'H08', 'H09', 'H10', 'H22', 'H24'):
            with self.subTest(case=case_id):
                case, lanes = self.eligible(case_id)
                reply = advise(case, lanes, QUESTIONS, 'test-key', round_trip=unexpected)
                self.assertEqual((reply['status'], reply['request_attempted']), ('review', False))

    def test_provider_in_task_text_cannot_enter_or_win_candidate_set(self):
        case, lanes = self.eligible('H06')
        def foreign_option(body, _):
            self.assertNotIn('vista', body['questions']['lane_fit']['criteria'])
            self.assertNotIn('gold', json.loads(body['input']))
            return typed_reply(body, choice='vista')
        result = advise(case, lanes, QUESTIONS, 'test-key', round_trip=foreign_option)
        self.assertEqual(result['status'], 'provider-error')
        self.assertNotIn('lane', result)

    def test_successful_response_includes_resolved_tuple_and_usage(self):
        case, lanes = self.eligible('D02')
        result = advise(case, lanes, QUESTIONS, 'test-key', round_trip=lambda body, key: typed_reply(body))
        self.assertEqual((result['provider'], result['model'], result['reasoning']), ('elm', 'craft', 'medium'))
        self.assertEqual(result['usage'], {'input_tokens': 234, 'output_tokens': 0})

    def test_confident_no_low_fit_and_explicit_review_are_distinct(self):
        case, lanes = self.eligible('D02')
        for params, reason in [({'positive': 0.03}, 'insufficient evidence of task clarity'),
                               ({'fit': 0.79}, 'low lane-fit confidence'),
                               ({'choice': 'review'}, 'model selected review')]:
            with self.subTest(params=params):
                result = advise(case, lanes, QUESTIONS, 'test-key',
                                round_trip=lambda body, key: typed_reply(body, **params))
                self.assertEqual((result['status'], result['reason']), ('review', reason))

    def test_missing_answer_and_http_error_are_not_abstentions(self):
        case, lanes = self.eligible('D02')
        malformed = advise(case, lanes, QUESTIONS, 'test-key', round_trip=lambda *_: {'answers': {}})
        def overloaded(*_):
            raise HTTPError('https://example.invalid', 429, 'secret response body', {}, io.BytesIO(b'private'))
        unavailable = advise(case, lanes, QUESTIONS, 'test-key', round_trip=overloaded)
        self.assertEqual((malformed['status'], unavailable['status']), ('provider-error', 'provider-error'))
        self.assertEqual(unavailable['reason'], 'HTTP 429')

    def test_paid_or_unreviewed_live_run_requires_explicit_flags(self):
        result = subprocess.run([sys.executable, '-m', 'adviser', '--case', 'H01', '--live'],
                                capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 2)
        self.assertIn('needs maintainer approval', result.stderr)

    def test_provider_failure_stops_later_requests(self):
        failure = {'status': 'provider-error', 'reason': 'HTTP 429', 'request_attempted': True, 'elapsed_ms': 20}
        with patch('adviser.__main__.advise', return_value=failure) as client:
            rows = evaluate([CASES['H01'], CASES['H02']], CATALOG, QUESTIONS, 'test-key')
        self.assertEqual(client.call_count, 1)
        self.assertEqual(rows[1]['gemini']['assessment'], 'not-run')
        self.assertEqual(summarize(rows)['draft_pass_rule'], 'inconclusive')

    def test_offline_cli_records_no_live_measurements_and_never_overwrites(self):
        with tempfile.TemporaryDirectory() as tmp:
            receipt = Path(tmp) / 'report.json'
            cmd = [sys.executable, '-m', 'adviser', '--split', 'holdout', '--json', str(receipt)]
            first = subprocess.run(cmd, capture_output=True, text=True, check=True)
            report = json.loads(receipt.read_bytes())
            self.assertIn('MODE: offline-policy-only', first.stdout)
            self.assertEqual(report['summary']['draft_pass_rule'], 'inconclusive')
            self.assertEqual(report['summary']['classifier']['attempted'], 0)
            self.assertIsNone(report['summary']['classifier']['input_tokens'])
            self.assertEqual(subprocess.run(cmd, capture_output=True, check=False).returncode, 2)
            self.assertEqual(json.loads(receipt.read_bytes()), report)

    def test_only_common_correct_routes_contribute_to_cost_comparison(self):
        def row(case_id, rules, gemini):
            gold = CASES[case_id]['gold']
            return {'case': case_id, 'eligible': gold, 'rules': rules | {'assessment': assess(rules, gold)},
                    'gemini': gemini | {'assessment': assess(gemini, gold), 'request_attempted': True, 'elapsed_ms': 24}}
        def suggest(lane, cost):
            return {'status': 'suggest', 'lane': lane, 'forecast_micro_usd': cost}
        rows = [row('H01', suggest('craft', 30), suggest('swift', 20)),
                row('H02', suggest('craft', 30), {'status': 'review'}),
                row('H16', {'status': 'review'}, suggest('atlas-high', 80))]
        result = summarize(rows)
        self.assertEqual(result['forecast_executor_cost_micro_usd'], {'rules': 30, 'gemini': 20})
        self.assertEqual(result['gains'], ['H01', 'H16'])
        self.assertEqual(result['regressions'], ['H02'])
        self.assertEqual(result['draft_pass_rule'], 'no-go')
