# MDScript vs Modern LLM Scripting Libraries

This analysis is based on `benchmarks/llm-scripting/results/latest.json`, generated with OpenAI `gpt-5.5` using `--blind-labels` at temperature `0`.

## Outcome Judge Result

`gpt-5.5` completed all 30 blinded judgments with zero parse failures. The rubric scores expected task outcomes, not readability or simplicity as independent virtues.

| Rank | System | Overall | Task Success | Requirements Met | Failure Recovery | Consistency |
| ---: | --- | ---: | ---: | ---: | ---: | ---: |
| 1 | LMQL | 7.37 | 7.67 | 8.33 | 5.00 | 6.67 |
| 2 | MDScript | 7.33 | 7.67 | 7.67 | 5.67 | 7.33 |
| 3 | Pydantic AI | 7.32 | 7.67 | 8.00 | 5.33 | 6.67 |
| 4 | Guidance | 7.02 | 7.33 | 8.00 | 5.00 | 5.67 |
| 5 | OpenAI Agents SDK | 6.92 | 7.00 | 7.67 | 5.33 | 6.67 |
| 6 | ell | 6.80 | 7.00 | 7.67 | 5.00 | 6.00 |
| 7 | Microsoft Agent Framework | 6.37 | 6.67 | 7.33 | 4.00 | 5.67 |
| 8 | LlamaIndex Workflows | 6.13 | 6.33 | 7.33 | 3.67 | 5.33 |
| 9 | LangGraph | 5.75 | 6.00 | 7.00 | 3.00 | 5.00 |
| 10 | DSPy | 5.70 | 5.67 | 7.33 | 3.67 | 4.00 |

Case winners:

- `release_notes`: LMQL, 7.75.
- `deploy_branch`: LMQL, 8.05.
- `onboard_service`: OpenAI Agents SDK, 7.00.

## Interpretation

Under the outcome rubric, MDScript no longer "crushes" every alternative. It ranks second overall, 0.04 behind LMQL and 0.01 ahead of Pydantic AI. That is the more credible result: MDScript is highly competitive on expected task outcome while remaining much lighter than the framework-style approaches.

The judge rated MDScript equal to LMQL and Pydantic AI on average task success, and highest on average consistency. Its weaker dimension was requirements met, especially on the `onboard_service` case, where the benchmark script did not explicitly scaffold Docker Compose files or fully specify several validation branches.

LMQL ranked first because the outcome judge saw it as likely to satisfy more explicit success criteria in the release-notes and deploy cases. OpenAI Agents SDK won the onboarding case, likely because its instruction/tool framing gave the judge more confidence that an agent would carry out the broad scaffold workflow.

The heavier graph/workflow frameworks still ranked lower in this representation-level fixture. That should not be overclaimed. The benchmark artifacts for those systems are generated skeletons, not hand-optimized production LangGraph or LlamaIndex implementations. A runtime execution benchmark that actually uses typed state, checkpoints, traces, retries, and parallel branches could produce a different ranking.

## What Changed

The previous rubric mixed outcome with readability and simplicity, which made the benchmark look too much like a test of MDScript's design goals. The fixed rubric removes those as direct scoring categories.

Current overall score:

```text
0.45 task_success + 0.30 requirements_met + 0.15 failure_recovery + 0.10 consistency
```

Readability, simplicity, debuggability, and framework feature depth now matter only when the judge thinks they improve or harm the expected task result.

## MDScript Takeaway

The stronger claim is:

> In a blinded, outcome-focused LLM-as-judge benchmark of repository workflow artifacts, MDScript was statistically close to the top result and ranked second overall while using a much lighter representation than most alternatives.

That is less flashy than "MDScript crushes everything," but it is much more publishable.

## Limits

- This is still a judge benchmark, not a real execution benchmark.
- It estimates expected task outcomes rather than measuring completed files/actions in a sandbox.
- It compares generated representations, not best-effort expert implementations for each framework.
- It does not yet measure real 100-run consistency, wall-clock time, token cost, trace quality, or human intervention rate.

## Next Improvements

- Add an executor benchmark where the same agent actually follows each artifact in a sandbox and the scorer checks concrete output files/actions.
- Run each artifact multiple times and measure real success rate, requirement coverage, recovery, and variance.
- Add hand-authored best-effort baselines for LangGraph, LlamaIndex Workflows, Pydantic AI, and OpenAI Agents SDK.
- Keep the judge rubric outcome-only, and move readability/simplicity to explanatory analysis rather than score categories.
