# Checks

The builder reviews the exact change; independent review is commissioned separately. The owner controls merge. Issue #1 remains Draft until the maintainer reads the scenarios and pass criteria.

With no hosted CI configured, the complete deterministic gate is:

```sh
python3 -m unittest discover -s tests -v
```

Python 3.10+; no SDK, API key, or child model needed. Paste the exact-head gate command and actual result into the PR. It covers eligibility, recommendation boundaries and evaluation semantics, not live model quality. The comparison also needs current Workbench baseline receipts, one live development smoke per configuration under verified no-additional-spend access, and maintainer-reviewed scenarios. Keep these evidence states separate.

For a locked comparison, run `python3 -m adviser.compare --labels LABELS --label-digest SHA256 --baseline BASELINE --comparator RECEIPTS`. Each file is a JSON array keyed by `case`. Label rows contain `acceptable` (lane IDs or `review`) and `eligible` (lane ID to executor forecast in microdollars). Receipt rows contain `status` (`suggest`, `review`, `provider-error`, or `not-run`) and `lane` on suggestions. Keep provider usage and raw receipts separately; the scoring command records all input digests and takes projected costs from sealed labels, not model output.
