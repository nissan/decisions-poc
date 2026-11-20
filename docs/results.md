# Holdout results (v1, partial matrix)

24 fresh synthetic planning cases, labels sealed before any run (`9b6e704a…0f96`), current-practice baseline locked before comparators (`f8e22dde…ff60`), comparator outputs locked on #6 before scoring. Scorer: `python3 -m adviser.compare`. Correct = acceptable lane or necessary review.

| Arm | Correct / 24 | Wrong lane | Avoidable review | Gains vs baseline | Regressions vs baseline | Verdict |
|---|---|---|---|---|---|---|
| **Current Workbench planner (baseline)** | **23** | 0 | 1 | — | — | — |
| Gemini Decision 1 (typed) | 17 | 0 | 7 | 0 | 6 | no-go |
| Claude Sonnet 5.5 / medium | 22 | 2 | 0 | 1 | 1 | no-go |
| Codex GPT-6 Luna / low | 20 | 3 | 1 | 0 | 3 | no-go |
| Codex GPT-6 Luna / medium | 20 | 3 | 1 | 0 | 3 | no-go |
| Claude Haiku 5.5 / low | 15 | 2 | 7 | 1 | 9 | no-go |
| OpenRouter LFM-3 1.7B free | 7 of 8 run | — | — | — | — | inconclusive (provider error, stopped) |
| OpenAI Decisions, GPT-6 Luna (typed, Part 2) | 13 | 0 | 11 | 0 | 10 | no-go |
| TypeSafe Jev 1.14 (typed, Part 2) | 11 | 0 | 13 | 0 | 12 | no-go |

No arm met the pass rule (zero regressions and at least two gains). No arm suggested an ineligible lane. Projected executor cost on cases both routed acceptably was equal except Sonnet (−4%, 13 cases). Gemini made no wrong suggestions but abstained on 7 routable cases at the 0.80 lane threshold; its useful property was safe abstention, not better routing.

**Part 2 (2026-11-20):** OpenAI Decisions and native Jev 1.14 ran on the same sealed cases, locked baseline and frozen 0.80/0.75 thresholds; outputs were locked on #9 before scoring. All three typed APIs share one pattern: zero wrong or ineligible lanes, but 7–13 routable tasks sent to review. At these thresholds a typed decisions API behaves as a conservative filter, not a better router. Part 2 ran after the labels were opened for Part 1 scoring; no label, threshold or prompt changed. A first OpenAI attempt sent an empty key (local 1Password prompt dismissed) and returned HTTP 401 before any model output; it is void and the rerun is reported. OpenAI used 11,585 input tokens and 0 output tokens (about US$0.001); Jev used 10,939 input tokens.

## Part 3: calibrated thresholds on a fresh sealed holdout (v2)

Per-API thresholds were chosen on 36 calibration cases (12 dev + the 24 opened v1 cases): zero wrong lanes, then most correct, ties to the stricter value. Frozen on #11 before v2 existed: Gemini lane ≥0.40 / clarity ≥0.65; OpenAI Decisions ≥0.85 / ≥0.55; Jev 1.14 ≥0.60 / ≥0.30. Holdout v2: 24 new packets, labelled by **Codex GPT-6 Luna** (a different family from the Opus planner) and sealed; the planner baseline was locked before any API ran; outputs locked before scoring.

| Arm | Correct / 24 | Wrong lane | Avoidable review | Gains | Regressions |
|---|---|---|---|---|---|
| Current Workbench planner (baseline) | 20 | 2 | 2 | — | — |
| Jev 1.14, calibrated | 20 | 0 | 4 | 1 | 1 |
| Gemini Decision 1, calibrated | 20 | 2 | 2 | 1 | 1 |
| OpenAI Decisions, calibrated | 13 | 0 | 11 | 0 | 7 |

Calibration closed most of the gap for Gemini and Jev. Calibrated Jev matched the planner's 20/24 with **no wrong lanes** where the planner made two; it traded those for two extra reviews. OpenAI's calibration set allowed no looser threshold without a wrong lane, so it stayed cautious. No arm met the pass rule (each had at least one regression). With a different-family labeler the planner scored 20/24, not 23/24, which supports the Part 1 caveat that a same-family labeler flattered the baseline.

## Validity limits

- The labeler and baseline planner were separate sessions of the same model family (Claude Opus 5.5); agreement between them likely favors the baseline. The usual GPT planner role was unavailable on ChatGPT Go.
- Labels are agent-generated and not yet maintainer-reviewed. 24 synthetic cases; single run per arm; no downstream execution, so no realized savings claim.
- Codex Luna low and medium gave identical decisions; Codex does not report the served model.
- Part 3: calibration reused the opened v1 cases, so thresholds fit those cases closely; only v2 is a fair test. 24 v2 cases, one run each; agent-generated labels; differences of one case are within noise.
