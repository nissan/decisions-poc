# Gemini Decisions API POC

**Subagent Routing Adviser:** can Gemini Decisions help select the provider, model and reasoning level for a planned task without accepting worse matches or using more of the budget than the work needs?

This repository contains the API research, experiment design and production plan. No application, live model results, or public demo yet.

- [API research](docs/research.md) — vendor contract, limits, and what we still need to measure.
- [Experiment protocol](docs/experiment.md) — input, rubric, routing policy, and paired evaluation.
- [Prompt and action log](docs/log.md) — public-safe decision trail.
- [Retrospective and release plan](docs/writeup.md) — evidence and publication gates.
- [Demo brief](demo/brief.md) and [scene manifest](demo/manifest.json) — replaceable narrated scenes.

GitHub Issues owns scope and readiness. Link working PRs and exact-head evidence to the issue. Draft scenarios are not owner acceptance. The adviser runs in shadow mode: it cannot spawn agents, change settings or allocate real budget. Only original synthetic tasks and simulated lane snapshots go to Google or into this repository; no private project material, account data, transcripts, credentials, or raw recordings.
