# Decisions POC

**Subagent Routing Adviser:** can a typed decisions API select the provider, model and reasoning level for a planned task without accepting worse matches or overprovisioning the work?

This repository contains a runnable shadow adviser. Offline mode runs the static rules diagnostic and eligibility checks; it does not reproduce the current Workbench planning workflow or fabricate Gemini answers. See [checks](docs/CHECKS.md) for the evidence required before claiming live results.

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

The existing CLI can evaluate a Gemini-only holdout after maintainer review, but that is not the planned comparison. Freeze and capture the [current-practice baseline](docs/experiment.md#primary-baseline-current-workbench-planning-workflow) before running any comparator on holdout. Each CLI receipt contains source/fixture hashes and per-case decisions; do not recycle output filenames. The CLI cannot read an account's billing tier.

- [API research](docs/research.md) — vendor contract, limits, and what we still need to measure.
- [Comparison matrix](docs/providers.md) — three typed APIs, tiered Claude and Codex controls, and a pinned OpenRouter free candidate.
- [Experiment protocol](docs/experiment.md) — input, rubric, routing policy, and paired evaluation.
- [Prompt and action log](docs/log.md) — public-safe decision trail.
- [Retrospective and release plan](docs/writeup.md) — evidence and publication gates.
- [Offline retrospective](docs/retrospective.md) — baseline misses and why zero Gemini calls make the comparison inconclusive.
- [Demo brief](demo/brief.md) and [scene manifest](demo/manifest.json) — replaceable narrated scenes.

[Issue #1](https://github.com/nissan/decisions-poc/issues/1) owns scope and readiness. Link working PRs and exact-head evidence there. Draft scenarios are not owner acceptance. The adviser runs in shadow mode: it cannot spawn agents, change settings or allocate real budget. Only original synthetic cases and simulated lane snapshots go to providers; no private project material, account data, transcripts, credentials, or raw recordings.
