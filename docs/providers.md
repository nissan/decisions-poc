# Comparison arms and access

## Native typed decision models

| Arm | Proposed API and model | No-additional-spend path | Uncached paid input per 1M tokens |
| --- | --- | --- | --- |
| Gemini | [Google Decisions API](https://aistudio.google.com/docs/decisions-api), `gemini-decision-1` | [Native free tier](https://aistudio.google.com/docs/pricing#gemini-decision). Confirm the project's tier; device verification may be required. Google may use free-tier inputs to improve its products. | US$0.10 |
| OpenAI | [OpenAI Decisions API](https://developers.openai.com/api/docs/guides/decisions), `gpt-6-luna` | No general free tier documented for this endpoint. [Eligible ChatGPT Pro or Business owners can claim subscription API credits](https://developers.openai.com/api/docs/guides/chatgpt-api-credits#what-the-credits-cover), explicitly covering Decisions without an API payment method. Check the linked organization's eligible balance; paid credits are charged after free credits are exhausted if present. | US$0.10 |
| TypeSafe | [Jev 1.13 via OpenCode Console](https://opencode.ai/docs/zen/), `jev-1.13-free` | Officially listed as a limited-time free model. The gateway's normal signup instructions ask for billing details and credits; whether an already-authorized account can use the offer without adding funds is unverified. For a separately approved paid run, [Jev 1.14](https://docs.typesafe.ai/models) is the newer version; use a fixed version and report it. | US$0.042 for native Jev 1.13/1.14 |

All three list zero output-token charges. List prices are not measured latency or cost; account minimums and gateway charges are separate. [OpenRouter lists Luna Decisions](https://openrouter.ai/openai/gpt-6-luna-decisions) and [Jev 1.14](https://openrouter.ai/typesafe/jev-1.14) as paid, not a free substitute. The OpenAI subscription benefit is not a free signup tier, and an interactive playground is not proof of reusable API access. No paid sign-up, top-up, auto-recharge, subscription linkage, or payment method is assumed authorized.

## Classic generative controls

Run ordinary text generation constrained by a JSON schema, not a Decisions API. The [current Workbench planning workflow](experiment.md#primary-baseline-current-workbench-planning-workflow) is the baseline; these are comparators even when they use a model the current planner also uses.

| Control | Economy | Standard | Access boundary |
| --- | --- | --- | --- |
| [Claude Code](https://code.claude.com/docs/en/cli-reference) | Haiku / low | Sonnet / medium | Already provisioned subscription path. Pin the [resolved versions and supported effort](https://code.claude.com/docs/en/model-config); run only inside included allowance. Do not enable extra usage or use an API key as fallback. |
| [Codex CLI](https://developers.openai.com/codex/non-interactive-mode) | GPT-6.2 Sol / low | GPT-6.2 Sol / medium | Same [model](https://developers.openai.com/codex/models), two reasoning levels; use ChatGPT sign-in within included allowance. This does not authenticate OpenAI's native Decisions endpoint. |
| [OpenRouter Chat Completions](https://openrouter.ai/docs/guides/features/structured-outputs) | `liquid/lfm-3-1.7b:free` | — | The [public catalog](https://openrouter.ai/api/v1/models) listed the exact free slug at zero input/output price with structured outputs. Verify on the served endpoint and account. Require schema support and do not substitute a paid variant or a moving free router. |

Claude's two configurations change both model and effort; do not attribute the difference to one variable. Codex's two configurations are an effort-only contrast. These are draft starting points, not verified inferences or a new deployment model policy. If an effort is unsupported, report it or pre-register a replacement before holdout. Defer frontier/high-effort rows unless their included allowance and decision value justify the extra comparison. Subscription usage is real quota consumption; auth status alone does not prove a remaining allowance or permission for extra credits.

Classic controls return a lane ID or `review`, a task-clear boolean, and an ordered complexity level. Validate the schema and enum against the eligible candidates. Use only synthetic context with no tools enabled for task execution, no integration or account data, and no retries that silently change the arm. Retain exact harness, schema, model/effort and usage evidence; report harness overhead rather than presenting end-to-end latency as pure model latency.

## Fair head-to-head

- Retain the same synthetic corpus. Score the same three judgments with equivalent instructions: lane selection, task clarity, and ordered complexity. Native types are `choice`, `predicate` (OpenAI) / `noul` (Gemini and Jev), and `score`. Use one request per eligible case and the same local eligibility and no-dispatch policy.
- For typed arms, normalize `P(yes)` and probability of the selected lane, retaining native confidence and raw distributions. Classic arms supply categorical outputs and can abstain; do not treat emitted confidence numbers as if they were native calibrated probabilities. Report quality with and without confidence gating as specified in the [experiment](experiment.md).
- Compare each arm to current practice on paired cases. Show the static rule reference and arm-to-arm results separately. Record exact model, effort, provider/endpoint and harness, code and fixture hashes, accuracy, review/error counts, usage and latency. Separate gateway or CLI overhead and classifier consumption from projected executor cost.
- Review labels and thresholds before live holdout. Verify one development smoke per configuration and do not silently fall back. Label any partial comparison as partial; do not rank unrun arms.

Current implementation: diagnostic rules, a live-smoked Gemini adapter, and offline-verified OpenAI/Jev development adapters. Current-practice capture, sealed multi-arm holdout execution and classic controls are not yet qualified.
