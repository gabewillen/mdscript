# MDScript vs Modern LLM Scripting Libraries

This analysis is based on `benchmarks/llm-scripting/results/latest.json`, generated with OpenAI `gpt-5.5` using `--blind-labels`, 3 execution runs per artifact, and 3 judgments per execution.

## Outcome Result

`gpt-5.5` completed 90 executions and 270 judgments with zero parse failures. The rubric scores produced task outcomes, not readability or simplicity as independent virtues.

| Rank | System | Overall | Task Success | Requirements Met | Failure Recovery | Std Dev | Judgments |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | OpenAI Agents SDK | 9.71 | 9.93 | 9.56 | 9.33 | 0.29 | 27 |
| 2 | DSPy | 9.54 | 9.81 | 9.44 | 8.85 | 0.30 | 27 |
| 3 | ell | 9.39 | 9.56 | 9.22 | 9.22 | 0.55 | 27 |
| 4 | Pydantic AI | 9.35 | 9.56 | 9.19 | 9.07 | 0.57 | 27 |
| 5 | Guidance | 9.22 | 9.33 | 9.15 | 9.04 | 0.73 | 27 |
| 6 | LMQL | 9.15 | 9.22 | 9.11 | 9.00 | 0.79 | 27 |
| 7 | LangGraph | 9.05 | 9.26 | 8.85 | 8.81 | 0.64 | 27 |
| 8 | LlamaIndex Workflows | 8.96 | 9.15 | 8.78 | 8.74 | 0.69 | 27 |
| 9 | Microsoft Agent Framework | 8.94 | 9.07 | 8.81 | 8.78 | 0.71 | 27 |
| 10 | MDScript | 8.87 | 8.89 | 8.93 | 8.67 | 0.75 | 27 |

Case winners:

- `release_notes`: OpenAI Agents SDK, 9.73.
- `deploy_branch`: OpenAI Agents SDK, 9.80.
- `onboard_service`: DSPy, 9.75.

## Interpretation

With three execution attempts and three judgments per execution, the result no longer supports the earlier artifact-only story. MDScript ranks last in this simulated execution benchmark, although its absolute score remains high at 8.87.

The important read is not that MDScript failed. The stronger systems benefited from the executor model producing very complete structured results from their instruction/tool scaffolds. MDScript remained competitive in absolute terms, but its looser workflow artifacts left more room for small execution differences to become judged gaps.

The MDScript-specific notes are concrete:

- In `deploy_branch`, one execution used `dist/feature/checkout-health-{timestamp}.tar.gz` instead of the expected sanitized `dist/feature-checkout-health-{timestamp}.tar.gz`.
- In `onboard_service`, executions repeatedly omitted the Docker Compose file required by the selected deployment target.
- In `release_notes`, MDScript performed well, with judgments mostly noting only minor evidence gaps such as not showing full generated file contents.

This is useful feedback on the benchmark scripts, not a reason to make the MDScript spec less freeform. It says that when the desired outcome depends on exact path normalization or deployment-specific artifacts, the script author needs to include those details in natural language.

## What Changed

The prior benchmark judged the artifact directly. This version separates execution from judgment:

1. The executor model follows the workflow artifact and produces a structured task result.
2. The judge model scores only that produced result against the task scenario.
3. Each artifact receives 3 execution attempts and 3 judgments per attempt.

Current overall score:

```text
0.50 task_success + 0.35 requirements_met + 0.15 failure_recovery
```

This better matches the claim we actually care about: which workflow representation produces better task outcomes under repeated attempts.

## MDScript Takeaway

The defensible claim is now narrower:

> In a repeated LLM execution-and-judgment benchmark, MDScript produced generally successful outcomes but underperformed more explicit agent/tool scaffolds on exact artifact details in these benchmark tasks.

That is not as flattering, but it is much more useful. It points directly to improvements for the example workflows: specify path normalization, Docker Compose outputs, and other exact artifacts when those details are part of the required result.

## Limits

- This is still an LLM-simulated execution benchmark, not a sandboxed real tool execution benchmark.
- The executor and judge both used `gpt-5.5`; provider/model coupling may favor OpenAI-style agent artifacts.
- The framework artifacts are generated representations, not expert-authored best implementations.
- The benchmark scenarios exercise only three workflow families.

## Next Improvements

- Run a true sandbox executor that creates files and runs commands, then judge concrete filesystem/output state.
- Add hand-authored best-effort artifacts for every framework.
- Add multiple executor models, including a smaller local model, to test whether MDScript helps weaker agents more than frontier agents.
- Add targeted MDScript variants with more explicit natural-language artifact requirements and compare them against the current terse examples.
