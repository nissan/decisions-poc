import json
import subprocess
import sys
import unittest

from adviser.classic import decide, parse_claude, parse_codex, parse_openrouter, prompt_and_schema
from adviser.policy import eligibility, fixture

CASE = next(c for c in fixture('cases') if c['id'] == 'D02')
ELIGIBLE, _ = eligibility(CASE, fixture('lanes'))


class ClassicControls(unittest.TestCase):
    def test_prompt_hides_labels_and_type_and_schema_only_offers_eligible_lanes(self):
        prompt, schema = prompt_and_schema(CASE, ELIGIBLE, fixture('questions'))
        self.assertNotIn('"gold"', prompt)
        self.assertNotIn('"type": "fix"', prompt)
        self.assertEqual(set(schema['properties']['lane_fit']['enum']), ELIGIBLE.keys() | {'review'})

    def test_claude_reply_maps_to_resolved_tuple(self):
        reply = {'structured_output': {'lane_fit': 'craft', 'task_clear': True, 'complexity': 1},
                 'modelUsage': {'claude-haiku-5-5': {}}, 'usage': {'input_tokens': 900, 'output_tokens': 40},
                 'total_cost_usd': 0.001}
        answer, served, usage = parse_claude(json.dumps(reply), 'claude-haiku')
        result = decide(answer, ELIGIBLE, served, usage)
        self.assertEqual((result['status'], result['provider'], result['reasoning']), ('suggest', 'elm', 'medium'))
        self.assertEqual(result['served_model'], 'claude-haiku-5-5')

    def test_wrong_served_claude_model_or_refusal_is_a_provider_error(self):
        for reply in ({'structured_output': {}, 'modelUsage': {'claude-opus-5-5': {}}, 'usage': {}},
                      {'modelUsage': {'claude-haiku-5-5': {}}, 'usage': {'input_tokens': 1, 'output_tokens': 1}}):
            with self.subTest(reply=reply), self.assertRaises((ValueError, KeyError)):
                parse_claude(json.dumps(reply), 'claude-haiku')

    def test_codex_negative_clarity_reviews_and_ineligible_lane_is_rejected(self):
        events = [{'type': 'item.completed', 'item': {'type': 'agent_message',
                   'text': json.dumps({'lane_fit': 'craft', 'task_clear': False, 'complexity': 0})}},
                  {'type': 'turn.completed', 'usage': {'input_tokens': 10, 'cached_input_tokens': 0,
                                                       'output_tokens': 5, 'reasoning_output_tokens': 3}}]
        answer, served, usage = parse_codex('\n'.join(map(json.dumps, events)))
        self.assertEqual(decide(answer, ELIGIBLE, served, usage)['status'], 'review')
        with self.assertRaises(ValueError):
            decide(answer | {'lane_fit': 'vista', 'task_clear': True}, ELIGIBLE, served, usage)

    def test_openrouter_rejects_paid_substitution(self):
        reply = {'model': 'liquid/lfm-3-1.7b', 'usage': {'prompt_tokens': 5, 'completion_tokens': 5, 'cost': 0},
                 'choices': [{'message': {'content': json.dumps({'lane_fit': 'review', 'task_clear': True,
                                                                  'complexity': 2})}}]}
        answer, served, usage = parse_openrouter(json.dumps(reply), 'liquid/lfm-3-1.7b')
        self.assertEqual(decide(answer, ELIGIBLE, served, usage)['status'], 'review')
        with self.assertRaises(ValueError):
            parse_openrouter(json.dumps(reply | {'usage': reply['usage'] | {'cost': 0.0002}}), 'liquid/lfm-3-1.7b')

    def test_live_run_requires_explicit_included_usage_confirmation(self):
        result = subprocess.run([sys.executable, '-m', 'adviser.classic', 'claude-haiku-low', '--json', 'unused.json'],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn('--confirmed-included-usage', result.stderr)
