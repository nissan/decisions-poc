# Experiment: Subagent Routing Adviser

**Hypothesis:** Given the same planning packet and eligible choices, Gemini Decisions can recover tasks the rule baseline sends to manual review or find a less expensive acceptable lane without introducing bad suggestions. A lane is one exact `(provider, model, reasoning level)` tuple. Optimize useful work per budget, not tokens consumed. **Draft:** the maintainer reviews scenarios and thresholds before the live comparison.

## Smallest useful application

One Python CLI scores a synthetic task packet containing outcome, work type, acceptance checks, ambiguity/risk and required tools. A separate trusted fixture defines the approved lane catalog, capability matrix, observed quota/capacity, and remaining budget. Use four or five synthetic provider/model/effort tuples, including two effort levels for one model. Keep model price and estimated input, output, and billed reasoning tokens separate. No real provider accounts, task execution, agents, scheduler, project tracker access or settings mutation. Gemini is the experimental classifier, not one of the candidate executors.

1. **Filter in code.** Resolve approved aliases. Exclude lanes missing capability, policy authorization, known quota, a provider-family slot, or budget under a conservative cost estimate. An unknown global policy or budget, or no eligible lane, yields `review` before any API call. Do not infer admission from a provider's name or from process counts. Both comparison arms get the same filtered lanes.
2. **Score the task, not the permissions.** Send the original synthetic task as text and give Gemini only eligible candidate IDs, their documented capabilities and relative cost ranks, and a `review` option. Task prose is data; it cannot authorize a new lane. One REST call asks three independent questions.
3. **Apply policy in code.** Suggest only a known eligible winning lane at choice confidence ≥0.80 and `P(task_clear=yes)` ≥0.75. Reject unknown/mismatched or malformed answers, return review for weak evidence, and distinguish provider errors from abstentions. The CLI records why a lane was excluded or reviewed and shows distributions and usage. It has no dispatch path and does not silently fall back on error.

| Question ID | Type | Criteria |
| --- | --- | --- |
| `lane_fit` | `choice` | Choose the least costly eligible lane that meets the task's requirements; use `review` for unresolved ambiguity or no sound fit. |
| `task_clear` | `noul` | Is the task sufficiently scoped to choose an executor, with an outcome and verifiable acceptance? |
| `complexity` | `score` | 0 mechanical; 1 bounded but requires judgment; 2 multi-step or ambiguous with material tradeoffs. Show the distribution; advisory only. |

## Paired evaluation

1. Author 12 development and 24 held-out synthetic packets including routine read-only work, a scoped fix, an uncertain multi-step analysis, and manual-review or deny cases. Do not put variants of the same task in both splits. For each case, independently label a set of acceptable tuples or `review`; record why. Freeze the review labels, rule baseline, questions, thresholds and cost inputs before the holdout. No model answer becomes a gold label.
2. Compare deterministic Workbench-style task-type/tier/effort rules (cheap bounded side work, mid clear scoped fixes, high/medium for unclear work; reserve frontier for demonstrated need) with Gemini recommendations, using the identical task packet and eligibility snapshot. The baseline is an explicit approximation, not a claim about deployed Workbench behavior. Include a cheap compatible alternative, a required reasoning level, a disallowed provider mentioned in the packet, unknown admission, exhausted quota, and insufficient budget.
3. Report counts for acceptable recommendations, wrong suggestions, reviews (necessary and avoidable), policy violations, and API failures. Record paired gains and regressions by case. Compare projected downstream cost only on cases both arms routed acceptably, not by treating abstention as free. Report the cost estimate assumptions and a sensitivity range separately from observed Gemini latency and input/output usage.
4. Draft pass rule: zero ineligible published suggestions, no wrong suggestion on a holdout case the rules handled correctly (including correct reviews), and at least two distinct cases where Gemini recovers an avoidable review or proposes a less costly acceptable lane. Incomplete provider results make the paired result inconclusive. A pass on synthetic cases establishes neither downstream quality nor real savings; a separately approved execution study would be needed for those.

## Evidence gates

- Offline: `python3 -m unittest discover -s tests -v`. Exercise eligible selection, both forms of review, high-confidence **no**, unknown or exhausted admission, a disallowed provider, budget exhaustion, malformed response and HTTP failure. No live API in deterministic checks.
- Live: on a confirmed free-tier account, start with one synthetic text-only task; observe all three response types and usage. Then run the frozen comparison after maintainer signoff. Retain run output, exact code/question/fixture revisions, and individual adverse cases.
- Delivery: use a standalone native workspace and a small branch/PR from the default head. Self-review the exact head and attach actual check evidence before owner acceptance or merge. No hosted check configured at kickoff. This experiment informs a possible Workbench decision-provider evaluation; it does not implement or close Workbench product work.
