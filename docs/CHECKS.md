# Checks

The builder reviews the exact change; independent review is commissioned separately. The owner controls merge. Issue #1 remains Draft until the maintainer reads the scenarios and pass criteria.

With no hosted CI configured, the complete deterministic gate is:

```sh
python3 -m unittest discover -s tests -v
```

Python 3.10+; no SDK, API key, or child model needed. Paste the exact-head gate command and actual result into the PR. It covers eligibility, recommendation boundaries and evaluation semantics, not live model quality. The comparison also needs current Workbench baseline receipts, one live development smoke per configuration under verified no-additional-spend access, and maintainer-reviewed scenarios. Keep these evidence states separate.

Score against the digests recorded in #3 and #4, not digests computed ad hoc from files at scoring time:

```sh
python3 -m adviser.compare --labels LABELS --label-digest LABEL_SHA256 \
  --baseline BASELINE --baseline-digest BASELINE_SHA256 --arm ARM --comparator RECEIPT
```

Labels and baseline are JSON arrays keyed by `case`. Label rows contain `acceptable` (lane IDs or `review`) and `eligible` (lane ID to executor forecast in microdollars). The comparator receipt is a JSON object with `arm`, `label_sha256`, `baseline_sha256`, and `rows`. Baseline and comparator rows contain `status` (`suggest`, `review`, `provider-error`, or `not-run`) and `lane` on suggestions. Use the frozen configuration ID for `arm`.

**Required evidence:** record the sealed label digest in #3 and the complete baseline digest in #4 before comparator holdout execution. Capture the comparator receipt and its provider/run evidence in #6 before unsealing. The CLI verifies byte identity and receipt bindings, not when a commitment was made or whether a provider produced the rows. Check the issue chronology and original run receipts before claiming any holdout result.

OpenAI Decisions and sponsored Jev development smoke: `python3 -m adviser.typed_smoke openai --confirmed-no-additional-spend --json runs/openai-D02.json` (or `jev` with a separate output path). The OpenAI arm requires a verified eligible `OPENAI_API_KEY`; the Jev arm requires a verified `OPENCODE_API_KEY` and pins `jev-1.13-free`. Do not use the flag until the credential's no-additional-spend route is verified. The tool has no holdout mode and no retries or automatic provider substitution.
