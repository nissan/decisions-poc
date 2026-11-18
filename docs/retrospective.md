# Retrospective: separating routing judgment from authority

We started with a multimodal game QA idea, then moved to the decision the Workbench actually faces: which eligible provider, model and reasoning level should receive a planned task? That choice is already structured. A screenshot would test the wrong hypothesis.

## What the offline run found

On implementation commit `c607b42835`, `python3 -m unittest discover -s tests -v` ran 10 tests successfully. `python3 -m adviser --split holdout` ran the explicit rule baseline on 24 original synthetic cases with draft labels. It yielded 15 acceptable lane suggestions, seven justified reviews, and two suggestions that should have been reviews. H05 did not specify the desired thumbnail size; H13 simultaneously asked for a uniqueness proof and forbade reading the catalogue. Both had enough fields to pass the rule baseline's presence check. Six packets had no eligible lane, so neither arm could suggest one. The CLI made zero Decisions requests.

The live smoke stopped before a network request because no Gemini API key was configured. That is an environment prerequisite, not a service error. No token usage, latency, paired routing delta or savings was measured. The paired outcome is **inconclusive**, not a Gemini result. The current evidence supports a possible use for semantic assessment; it does not show that Gemini solves it.

## What to preserve

1. Share one deterministic eligibility filter across comparison arms. Treat model output as a suggestion over eligible options, never as authorization to add a provider, bypass an unknown limit, or dispatch work.
2. Freeze the baseline and independently assigned labels before evaluating the model. Record baseline errors instead of patching them in the middle of the comparison. Report any subsequent baseline improvement as a new comparison.
3. Compare projected costs on cases both arms routed acceptably, and report manual-review coverage separately. An abstention is not free, and a cheaper recommendation is not evidence of cheaper execution.

The full offline receipt is reproducible using the CLI on that commit. The exact-head result and human gates are tracked in [PR #2](https://github.com/nissan/gemini-decisions-poc/pull/2). The live comparison needs maintainer review of the labels and pass rule plus a confirmed free-tier credential. A separate execution study would be required to make downstream quality or cost claims.
