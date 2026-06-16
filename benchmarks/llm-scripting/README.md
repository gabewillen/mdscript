# LLM Scripting Benchmark

This benchmark compares MDScript with modern LLM workflow and prompt-programming systems using a two-stage LLM execution and judgment loop. It is intentionally representation-level: each system gets an equivalent source artifact for the same repository workflow, an executor model attempts the workflow three times, and a judge model scores each produced result three times.

The default judge is `gemma4:e4b`, the smallest installed Gemma 4-family model in this environment. That is deliberate: a small local model is more likely to expose whether a format remains legible under long-horizon workflow pressure. For publishable judge results, run the OpenAI backend with `gpt-5.5` and `--blind-labels`.

## Research Notes

The comparison set splits into three groups:

- State/workflow orchestration: LangGraph, LlamaIndex Workflows, Microsoft Agent Framework, OpenAI Agents SDK, and Pydantic AI. LangGraph describes itself as infrastructure for long-running, stateful workflows and agents. LlamaIndex Workflows presents workflows as event-driven, step-based application control. Microsoft Agent Framework now positions workflows as graph-based multi-step tasks with type-safe routing, checkpointing, and human-in-the-loop support. OpenAI Agents SDK centers agents as LLMs configured with instructions, tools, handoffs, guardrails, and structured outputs. Pydantic AI is a typed Python agent framework for production GenAI applications.
- Prompt and language-model programming: DSPy, Guidance, LMQL, and ell. DSPy emphasizes signatures, modules, and optimizers over hand-written prompts. Guidance and LMQL focus on constrained/scripted generation and control flow around model calls. ell treats prompts as functions with versioning, monitoring, and visualization.
- Retired or de-emphasized systems: Microsoft Prompt Flow is documented as retired for new development and scheduled for full retirement on April 20, 2027, with migration guidance pointing to Microsoft Agent Framework, so it is research context rather than a primary benchmark target.

Sources used for current positioning:

- LangGraph docs: <https://docs.langchain.com/oss/python/langgraph/overview>
- LlamaIndex Workflows docs: <https://developers.llamaindex.ai/python/llamaagents/workflows/>
- Microsoft Agent Framework overview: <https://learn.microsoft.com/en-us/agent-framework/overview/>
- OpenAI Agents SDK docs: <https://openai.github.io/openai-agents-python/agents/>
- OpenAI model docs: <https://developers.openai.com/api/docs/models>
- Pydantic AI overview: <https://pydantic.dev/docs/ai/overview/>
- DSPy docs: <https://dspy.ai/>
- Guidance repository/docs: <https://github.com/guidance-ai/guidance>
- LMQL docs: <https://lmql.ai/docs/latest/language/reference.html>
- ell docs: <https://docs.ell.so/>
- Prompt Flow retirement notice: <https://learn.microsoft.com/en-us/azure/machine-learning/prompt-flow/migrate-prompt-flow-to-agent-framework>

## Methodology

The harness renders equivalent workflow artifacts for each candidate and case. For each artifact, it runs:

1. Three independent execution attempts against a fixed task scenario.
2. Three independent judgments for each produced execution result.

That yields 9 judgments per case/system and 27 judgments per system across the three cases. Each judgment scores produced task outcomes on a 1-10 scale:

- `task_success`: how likely a capable coding agent is to complete the task end-to-end.
- `requirements_met`: how many explicit success criteria are likely to be satisfied in the final result.
- `failure_recovery`: how likely the workflow is to recover from normal branch/failure cases.

Overall score is weighted as:

```text
0.50 task_success + 0.35 requirements_met + 0.15 failure_recovery
```

The order of judge calls is randomized with a fixed seed to reduce position effects. All artifacts are generated locally from the same case definitions, and the judge prompt tells the model to score only the artifact, not ecosystem reputation. Use `--blind-labels` for publication-oriented runs; it masks candidate names in the judge prompt and replaces obvious framework identifiers in the artifact text.

The executor prompt treats natural-language bullets, comments, and instruction strings as workflow semantics. The judge prompt scores only produced execution results, not readability, simplicity, debuggability, or framework feature depth as independent virtues.

This benchmark does not install or run every framework. That is a feature of the test, not a shortcut: MDScript is not competing as a Python runtime framework, so giving framework baselines their full runtime machinery would make the comparison less apples-to-apples for readability and workflow expression.

## Latest Result

The current run used OpenAI `gpt-5.5` with `--blind-labels`. It completed 90 executions and 270 judgments with zero parse failures.

<!-- latest LLM scripting benchmark summary from results/latest.json -->

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

## Run

```bash
python3 benchmarks/llm-scripting/benchmark.py
```

Frontier judge run:

```bash
python3 benchmarks/llm-scripting/benchmark.py \
  --backend openai \
  --model gpt-5.5 \
  --blind-labels \
  --execution-runs 3 \
  --judgments-per-run 3 \
  --env-file ../cortext/.env
```

Useful overrides:

```bash
python3 benchmarks/llm-scripting/benchmark.py --backend ollama --model gemma4:e4b
python3 benchmarks/llm-scripting/benchmark.py --model gemma4:e4b
python3 benchmarks/llm-scripting/benchmark.py --cases release_notes,deploy_branch
python3 benchmarks/llm-scripting/benchmark.py --systems mdscript,langgraph,guidance
python3 benchmarks/llm-scripting/benchmark.py --execution-runs 1 --judgments-per-run 1
python3 benchmarks/llm-scripting/benchmark.py --dry-run
```

Outputs are written under `benchmarks/llm-scripting/results/`:

- `latest.json`: full run data, rendered artifacts, raw judge responses, and aggregate scores.
- `latest-summary.md`: compact markdown summary.
- timestamped JSON: immutable copy for each run.

## Cases And Systems

<!-- benchmark systems and cases from benchmark.py -->

Cases:

- `release_notes`: collect commits from a git range, categorize them, and write `CHANGELOG.md`.
- `deploy_branch`: select a branch, run checks, build an artifact, deploy it, and verify health.
- `onboard_service`: interactively scaffold a new service with language, infrastructure, and deployment choices.

Systems:

- `mdscript`: Markdown state machine for coding agents.
- `langgraph`: Python graph workflow for stateful agents.
- `llamaindex_workflows`: Python event-driven agent workflow.
- `microsoft_agent_framework`: Python/.NET agent workflow framework.
- `openai_agents`: Python agent loop with tools, guardrails, and tracing.
- `pydantic_ai`: typed Python agent framework.
- `dspy`: Python LM programming framework with signatures/modules.
- `guidance`: prompt programming language embedded in Python.
- `lmql`: language-model query language.
- `ell`: Python LMP functions for model programs.
