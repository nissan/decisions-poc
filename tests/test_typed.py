import json
import unittest

from adviser.policy import eligibility, fixture
from adviser.typed_smoke import decode, encode

CASE = next(c for c in fixture('cases') if c['id'] == 'D02')
ELIGIBLE, _ = eligibility(CASE, fixture('lanes'))


def openai_reply(lane='craft', lane_p=0.85, clear_p=0.9, model='gpt-6-luna-2026-10-22'):
    rest = (1 - lane_p) / (len(ELIGIBLE))
    choices = [{'value': k, 'probability': lane_p if k == lane else rest} for k in [*ELIGIBLE, 'review']]
    return {'model': model, 'usage': {'input_tokens': 412, 'output_tokens': 0}, 'answers': [
        {'name': 'lane_fit', 'type': 'choice', 'choice': lane, 'confidence': lane_p, 'probabilities': choices},
        {'name': 'task_clear', 'type': 'predicate', 'probability': clear_p},
        {'name': 'complexity', 'type': 'score', 'score': 1.0, 'confidence': 0.6,
         'probabilities': [{'value': i, 'probability': p} for i, p in enumerate((0.2, 0.6, 0.2))]}]}


class OpenAIDecisions(unittest.TestCase):
    def test_request_hides_labels_and_offers_only_eligible_lanes(self):
        body = encode('openai', CASE, ELIGIBLE, fixture('questions'))
        self.assertNotIn('gold', json.loads(body['input']))
        choices = {c['value'] for c in body['questions'][0]['choices']}
        self.assertEqual(choices, ELIGIBLE.keys() | {'review'})

    def test_confident_clear_answer_suggests_the_resolved_tuple(self):
        result = decode('openai', openai_reply(), ELIGIBLE)
        self.assertEqual((result['status'], result['provider'], result['reasoning']), ('suggest', 'elm', 'medium'))

    def test_low_lane_probability_or_negative_clarity_reviews(self):
        for reply in (openai_reply(lane_p=0.6), openai_reply(clear_p=0.3)):
            self.assertEqual(decode('openai', reply, ELIGIBLE)['status'], 'review')

    def test_substituted_model_or_unknown_lane_is_rejected(self):
        with self.assertRaises(ValueError):
            decode('openai', openai_reply(model='gpt-5.6-luna'), ELIGIBLE)
        with self.assertRaises((ValueError, KeyError)):
            decode('openai', openai_reply(lane='vista'), ELIGIBLE)
