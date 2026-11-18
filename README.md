# Gemini Decisions API POC

**Subagent Routing Adviser:** can Gemini Decisions help select the provider, model and reasoning level for a planned task without accepting worse matches or using more of the budget than the work needs?

This repository contains a runnable shadow adviser and a synthetic paired evaluation. The offline mode runs the rule baseline and eligibility checks without credentials. It does not fabricate Gemini answers. See [checks](docs/CHECKS.md) for the evidence required before claiming live results.

```sh
python3 -m adviser --case D02
python3 -m adviser --split holdout
python3 -m unittest discover -s tests -v
```

For a live smoke, use only a key you know is on the Gemini free tier. Supply `GEMINI_API_KEY` locally outside Git and shell history, then run:

```sh
mkdir -p runs
python3 -m adviser --case D02 --live --json runs/smoke-D02.json
```

After maintainer review of the synthetic labels and pass rule, use `--split holdout --live --reviewed-holdout --json runs/holdout.json`. Each receipt contains source/fixture hashes and per-case decisions; do not recycle output filenames. A service failure stops further requests and makes the comparison inconclusive. The flags acknowledge review and free-tier access; the CLI cannot read an account's billing tier.

- [API research](docs/research.md) — vendor contract, limits, and what we still need to measure.
- [Experiment protocol](docs/experiment.md) — input, rubric, routing policy, and paired evaluation.
- [Prompt and action log](docs/log.md) — public-safe decision trail.
- [Retrospective and release plan](docs/writeup.md) — evidence and publication gates.
- [Demo brief](demo/brief.md) and [scene manifest](demo/manifest.json) — replaceable narrated scenes.

[Issue #1](https://github.com/nissan/gemini-decisions-poc/issues/1) owns scope and readiness. Link working PRs and exact-head evidence there. Draft scenarios are not owner acceptance. The adviser runs in shadow mode: it cannot spawn agents, change settings or allocate real budget. Only original synthetic tasks and simulated lane snapshots go to Google or into this repository; no private project material, account data, transcripts, credentials, or raw recordings.
