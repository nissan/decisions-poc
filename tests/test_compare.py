import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class CompareCLI(unittest.TestCase):
    def setUp(self):
        directory = self._directory()
        self.labels, self.baseline, self.receipt = (Path(directory) / name for name in ('labels', 'baseline', 'receipt'))
        self.cases = ('single-copy', 'scoped-edit')
        self.label_digest = self.write(self.labels, [
            {'case': case, 'eligible': {'light': 2, 'standard': 5}, 'acceptable': ['light', 'standard']}
            for case in self.cases
        ])
        self.baseline_digest = self.write(self.baseline, self.suggestions('standard'))
        self.envelope = {'arm': 'jev-1.13-free', 'label_sha256': self.label_digest,
                         'baseline_sha256': self.baseline_digest, 'rows': self.suggestions('light')}
        self.write(self.receipt, self.envelope)

    def _directory(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        return temp.name

    @staticmethod
    def write(path, value):
        content = json.dumps(value).encode()
        path.write_bytes(content)
        return hashlib.sha256(content).hexdigest()

    def suggestions(self, lane):
        return [{'case': case, 'status': 'suggest', 'lane': lane} for case in self.cases]

    def score(self, *, locked=True):
        args = [sys.executable, '-m', 'adviser.compare', '--labels', str(self.labels),
                '--label-digest', self.label_digest, '--baseline', str(self.baseline),
                '--comparator', str(self.receipt)]
        if locked:
            args += ['--baseline-digest', self.baseline_digest, '--arm', self.envelope['arm']]
        return subprocess.run(args, capture_output=True, text=True)

    def test_locked_pair_scores_and_preserves_the_baseline_digest(self):
        result = self.score()
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report['draft_verdict'], 'pass')
        self.assertEqual(report['input_sha256']['baseline'], self.baseline_digest)
        self.assertEqual(report['matched_acceptable_forecast'], {
            'cases': 2, 'current_practice_micro_usd': 10, 'comparator_micro_usd': 4,
        })

    def test_bare_arrays_cannot_score_without_a_baseline_lock(self):
        self.write(self.receipt, self.envelope['rows'])
        result = self.score(locked=False)
        self.assertEqual(result.returncode, 2)
        self.assertFalse(result.stdout)

    def test_changing_baseline_after_commitment_cannot_produce_a_verdict(self):
        self.write(self.baseline, self.suggestions('light'))
        result = self.score()
        self.assertEqual(result.returncode, 2)
        self.assertIn('baseline file does not match the precommitted digest', result.stderr)
        self.assertFalse(result.stdout)

    def test_receipt_from_another_arm_or_seal_is_rejected(self):
        for key in ('arm', 'label_sha256', 'baseline_sha256'):
            with self.subTest(field=key):
                self.write(self.receipt, self.envelope | {key: 'different'})
                result = self.score()
                self.assertEqual(result.returncode, 2)
                self.assertIn('comparator receipt does not match', result.stderr)
                self.assertFalse(result.stdout)
