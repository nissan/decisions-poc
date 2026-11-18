# Retrospective and publication plan

**Audience:** engineers deciding whether closed-set scoring belongs in a task-to-model router. **Question:** did the classifier find better task-to-model assignments than explicit rules once we accounted for abstentions, bad suggestions and projected cost?

## Evidence to retain as we build

- **Decisions:** public-safe request summaries, rejected alternatives and why, exact versioned model question/rubric changes, threshold changes and their development-split evidence.
- **Results:** case IDs, fixture and question revisions, exact code commit, arm, redacted service errors, typed decisions, usage and latency. Keep observed classifier usage separate from projected agent cost and held-out results separate from tuning runs. Preserve failed runs; do not overwrite them with reruns.
- **Retrospective:** starting hypothesis, what changed, developer mistakes (and their corrections), paired results and misses, threat to validity, and what we would keep or change. End with one reusable practice for the proposed Shared Brain review flow if the evidence supports it.
- **Claim ledger:** for each publishable claim, record its exact wording, source or run receipt, denominator, limitations and allowed channels. Vendor figures stay attributed. The public repo should contain original fixtures and only approved derivatives of local run receipts.

## Deliverables from the same evidence

| Channel | Angle | Include |
| --- | --- | --- |
| Technical blog | Is typed model routing better than explicit rules? | Question map, policy filter, paired counts, forecast assumptions, one example that helped and one that didn't, reproducibility steps. |
| LinkedIn | What the model could judge versus what the application had to decide | One supported finding, one limitation, link to the article and narrated demo. |
| X / Twitter | One concrete before/after | Short thread or single post linking the repo and article; add an approved clip or still only if it helps. |
| Other technical channels | Reproducible experiment, not product promotion | Adapt for a project newsletter or an appropriate developer community; respect each community's rules. Link to the canonical article rather than duplicating claims. |

Draft copy only after the evidence is available. Before posts or video uploads, get owner approval of exact copy, asset hashes, destinations and visibility. After each approved upload verify logged-out accessibility and record the permanent URL, revision/hash and receipt. Public GitHub setup does not authorize posting elsewhere.
