# Decisions POC

**Subagent Routing Adviser:** can a typed decisions API select the provider, model and reasoning level for a planned task without accepting worse matches or overprovisioning the work?

This repository contains the API research, experiment design and production plan. No application, live model results, or public demo yet.

- [API research](docs/research.md) — vendor contract, limits, and what we still need to measure.
- [Experiment protocol](docs/experiment.md) — input, rubric, routing policy, and paired evaluation.
- [Prompt and action log](docs/log.md) — public-safe decision trail.
- [Retrospective and release plan](docs/writeup.md) — evidence and publication gates.
- [Demo brief](demo/brief.md) and [scene manifest](demo/manifest.json) — replaceable narrated scenes.

[Issue #1](https://github.com/nissan/decisions-poc/issues/1) owns scope and readiness. Link working PRs and exact-head evidence there. Draft scenarios are not owner acceptance. The adviser runs in shadow mode: it cannot spawn agents, change settings or allocate real budget. Only original synthetic cases and simulated lane snapshots go to providers; no private project material, account data, transcripts, credentials, or raw recordings.
