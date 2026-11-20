# Prompt and action log

Append one entry per research decision, prompt/rubric change, test run, publication decision, or handoff. Write the request in public-safe paraphrase, state the action and observed result, cite stable evidence, and name the next decision. Keep exact API question text in versioned question files once implemented, not duplicated here. Commit related evidence and its entry together with an outcome-specific message. Raw agent transcripts, credentials, private issue references, and unpublished media stay out of Git and public issues.

## 01 — Research the endpoint before choosing a domain

**Prompt (paraphrased):** Investigate the new Decisions API, choose a small experiment relevant to current work, and make the build trace useful for a retrospective.

**Action and result:** Read Google's launch, model, API, rate-limit and pricing materials. Confirmed the documented typed response contract; no live request ran. Chose one shared request and three typed questions. Rejected a generative explanation feature: it would require a different model and confuse the comparison. [Research and sources](research.md).

## 02 — Use game QA intake, not release or gameplay automation

**Action and result:** Read upstream project status and considered release evidence screening, work intake, and game QA. Game QA was the initial candidate because it offered a clear pair of routes and a testable screenshot contribution; no application or fixtures were built. The owner proposed the Workbench model-selection use case before the first commit; see entry 04.

**Workflow:** Reopened the persisted kickoff record. Read the approved operating practice; an alternate local adapter candidate drifted, but the aligned artifact matched the installed instruction block and source policy. No settings changed. GitHub Issues is the work record; implementation uses a standalone native workspace and owner-reviewed scenarios.

**Next decision:** Validate the public-safe scenarios with the owner and confirm free-tier access before the first real model call.

## 03 — Make the demo evidence-led

**Prompt (paraphrased):** Preserve enough material for an honest retrospective, channel-specific posts and a narrated demo that can be revised scene by scene.

**Action and result:** Reused the scene-production approach from prior work, not its assets or private details. Planned real interaction footage, clearly labelled evidence cards, a visible failure or abstention, captions and replaceable local voice takes. [Demo brief](../demo/brief.md); [retrospective plan](writeup.md). Nothing recorded or posted.

## 04 — Pivot to task-to-model analysis

**Prompt (paraphrased):** Can Gemini Decisions assist Workbench's planning step that chooses a provider, model and reasoning level for each delegated task while making better use of available tokens and budget?

**Action and result:** Checked how the existing selector applies role defaults and how the fleet separates fit from authorization and admission. Chose a shadow adviser because structured planning packets and bounded lane choices fit the API directly. Replaced the game scenario with a paired rule-baseline comparison. Keep provider policy, capacity and cost checks in code. Measure model suggestions and simulated token economics separately; do not claim agent execution quality or real savings. [Revised protocol](experiment.md).

## 05 — Establish the public work record

**Action and result:** Pushed research, design, and the demo/publication plan as separate commits. Read the public default branch back without authentication at kickoff commit `bdae12dd27a46b6afc2452a14db656e8b90db709`. Read [GDP-001](https://github.com/nissan/decisions-poc/issues/1) back from GitHub and validated its Workbench contract structure; that is not evidence or approval of its scenarios. Checked relative links, the six-scene manifest (80 seconds planned), and ignore rules for local notes, credentials, and raw media.

**Next decision:** Review GDP-001's synthetic scenarios and pass rule; record a one-task free-tier smoke when access is available. No live model calls or media recording took place in this tranche.

## 06 — Implement the read-only comparison

**Prompt (paraphrased):** Carry the Workbench experiment through implementation, evidence, narrated demo, and publication.

**Action:** Used a standalone worktree from the public default head. Versioned the synthetic provider catalog, typed question map, and 12 development / 24 held-out task packets. Both comparison arms share the hard eligibility filter; Gemini receives neither account information nor gold labels. Offline output explicitly distinguishes requests not sent from policy review. Draft fixtures and pass criteria still need maintainer review.

## 07 — Run the offline gate and preserve the misses

**Observed:** At `c607b42835`, 10 deterministic checks passed. The rules suggested 15 acceptable lanes and two incorrect lanes; seven cases correctly went to review. The CLI made zero Gemini requests. `python3 -m adviser --case D02 --live` stopped locally with exit 2 because `GEMINI_API_KEY` was unset. No live model, usage or cost evidence was produced.

**Decision:** Do not tune out the baseline's two misses before the comparison. The [retrospective](retrospective.md) and [draft PR](https://github.com/nissan/decisions-poc/pull/2) record the negative cases and the live gate. Review collateral must say “offline,” not imply that the model was benchmarked.

## 08 — Expand to three decision models

**Prompt (paraphrased):** Find a no-additional-spend path for an OpenAI, Gemini and Jev comparison, and rename the project so it is no longer Gemini-specific.

**Action:** Renamed the public repository to `decisions-poc`. [Provider research](providers.md) distinguishes a native free tier, subscription-funded API credits, and a limited sponsored model version. The offline baseline stays frozen; compare the same synthetic packets and typed judgments through all three arms before making a head-to-head claim.

## 09 — Compare to the practice we actually want to improve

**Prompt (paraphrased):** Use ordinary Claude and Codex subscription models at more than one tier, plus an OpenRouter free model; make current task analysis and selection the baseline.

**Action:** Checked the approved role and effort policy, the local CLI output contracts, and the free structured-output catalog. [Revised the experiment](experiment.md) to capture the current Workbench planner's first decisions before running other arms on holdout. Demoted the offline rules result to a diagnostic control. Treat a subscription allowance as finite, and pin what was actually served. No inference ran in this tranche.

**Holdout correction:** The original draft holdout shipped with gold labels in the public fixture. Keep it for diagnostics; construct a fresh blind holdout with separate labels committed by digest before the first measured run.

## 10 — Begin the approved evaluation

The maintainer approved the draft design in conversation. One live Gemini development request (D02) returned all three typed answers with 513 input tokens and zero output tokens in 2.216 s on this workstation. The top lane was `craft` (0.656); clarity was 0.871, but the 0.80 lane threshold sent it to review. This is a successful API smoke, not a holdout verdict. The raw receipt stays local. No sealed holdout, current-practice baseline or other model arm ran.

## 11 — Continue autonomously within recorded gates

**Request (paraphrased):** Keep moving without routine approvals; check for stalled work every 15 minutes and default to the recommendation after three unanswered checks.

**Observed:** This host has no cron executable or active cron service. The installed Workbench recovery job is hourly and has its own enrolled streams; this POC is not one of them. No scheduler was changed and no autonomous check-in is active for this POC.

**Decision:** Use unattended defaults only for reversible, already-authorized choices. Consent, provider admission, spend, merge and publication gates do not expire. Reconcile leases, committed work and external receipts before any restart; never restart a merely quiet or owner-held run.

**Progress:** Added the OpenAI Decisions and sponsored Jev development adapters. Offline checks exercised request shape, confidence versus selected-option probability, negative clarity, usage and served-model mismatch. The existing 10 checks passed. No OpenAI or Jev inference was sent: verified no-additional-spend credentials are not configured.

## 12 — Require the precommitted baseline

The owner asked to resolve the merge finding. The scorer now requires a separately supplied baseline digest and rejects comparator receipts for another arm or seal. The GitHub evidence order still verifies precommitment: #3 seals labels, #4 records the baseline lock, then #6 records comparator receipts before labels are released. Scoring alone is not proof of run timing or provider origin.

## 13 — Add classic controls; hold on capacity

Under the risk-based review policy, PR #2 stays builder-reviewed; it is not high risk. Added the five classic LLM configurations as schema-constrained, development-only smokes. 20 local checks passed, including label/type hiding, served-model mismatch, negative clarity, ineligible lanes and paid substitution. The fleet capacity probe reported Claude and OpenAI occupancy as unknown because another pipeline worker is active or unclassified. Under fleet rules, that holds both the independent labeler and live Claude/Codex smokes. No model was called.

## 14 — Seal labels, smoke controls

Owner confirmed capacity (option B) and supplied the OpenRouter key from 1Password. An isolated Claude Opus 5.5 labeler sealed the 24-case holdout (labels digest `9b6e704a…0f96`, recorded on #3). D02 smokes: Haiku/low and Sonnet/medium chose `craft`; the free OpenRouter model abstained to review with zero reported cost. Codex rejected GPT-6.2 Sol on this ChatGPT account, so before any holdout the Codex pair was re-registered as GPT-6 Luna low/medium.

## 15 — Part 2: OpenAI Decisions and Jev

Owner upgraded ChatGPT to Pro, approved spending the existing OpenAI API balance, and funded a native TypeSafe account. Ticket #9 carried the outcome contract. D02 smokes passed for `gpt-6-luna` and `jev-1.14.0`. Holdout outputs were locked before scoring. OpenAI 13/24 correct, Jev 11/24, both with zero wrong lanes and many avoidable reviews. The next useful test is threshold calibration on development data, not more providers.
