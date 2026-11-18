# Gemini Decisions API research

## Documented contract

Google [announced Gemini Decision 1 on November 11](https://blog.google/innovation-and-ai/technology/developers-tools/gemini-decisions-api/). The [API guide](https://aistudio.google.com/docs/decisions-api) documents `POST https://generativelanguage.googleapis.com/v1beta/decisions`, model `gemini-decision-1`, and Python/JavaScript SDK 3.2+ examples. REST is enough for this experiment.

| Question | Return | What to watch |
| --- | --- | --- |
| Yes/no (`noul`) | `P(yes)` in 0.01–0.99; confidence is `max(P(yes), 1−P(yes))` | High confidence may mean **no**. Gate positive evidence on `P(yes)`, not confidence. |
| Choice (`choice`) | Top option, probabilities for 2–255 configured choices, confidence | Exact ties go to the key sorted first in UTF-8 byte order. Keep a review/unknown option and a threshold. |
| Ordered rubric (`score`) | Probability-weighted expected level, distribution, legend and confidence | The expected level can hide disagreement between levels. Show the distribution; don't treat a rounded score as the most likely level. |

- Up to 1,000 independent questions run over one shared input in one pass. Questions cannot see each other's answers. Compose dependencies and policy in application code.
- The [model card](https://aistudio.google.com/docs/models/gemini-decision-1) lists 262,144 input tokens and zero output tokens. Inputs can mix text, images, audio, video and PDF; planning packets are already structured text, so no media is needed here. No text generation, function calling, Live API, caching, or Batch API for this model; evaluating many questions in one request is not Batch API support.
- [Pricing](https://aistudio.google.com/docs/pricing#gemini-decision): free tier; standard paid input at US$0.10 per million input tokens, zero output charge. Shared input counts once; each question adds instructions, criteria and formatting. Google marks free-tier use as eligible for product improvement. Use only original synthetic content regardless of tier. [Published free limits](https://aistudio.google.com/docs/rate-limits#gemini-decision) are 200 requests/minute, 50,000 tokens/minute and 10,000 requests/day; confirm the project's actual tier and quota before running.

## What we have not measured

Google reports 150–250 ms median end-to-end in its launch benchmark (inputs up to 16K tokens) and nearly flat latency from 1 to 100 questions per request in that setting. These are vendor measurements, not workstation targets or guarantees. The POC will measure local round-trip times, classifier usage and recommendation quality against explicit routing rules. It will report simulated downstream cost separately from observed classifier usage; it will not run the recommended models or establish domain-wide calibration. No authenticated Decisions request was made during research: no API key was configured in the session, and no paid usage or credential changes were authorized.
