# LLM Scripting Benchmark

This benchmark compares MDScript with modern LLM workflow and prompt-programming systems using an LLM-as-judge. It is intentionally representation-level: each system gets an equivalent source artifact for the same repository workflow, and the judge scores the artifact a maintainer would read and a coding agent would follow.

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

The harness renders equivalent workflow artifacts for each candidate and case, then asks the same local judge to score each artifact on a 1-10 scale:

- `performance`: expected execution reliability and practical efficiency for a capable coding agent.
- `readability`: how easily a human can review and modify the workflow.
- `simplicity`: how little syntax, boilerplate, indirection, and framework knowledge are needed.
- `fidelity`: how fully the artifact covers the task success criteria.

Overall score is weighted as:

```text
0.35 performance + 0.25 readability + 0.25 simplicity + 0.15 fidelity
```

The order of judge calls is randomized with a fixed seed to reduce position effects. All artifacts are generated locally from the same case definitions, and the judge prompt tells the model to score only the artifact, not ecosystem reputation. Use `--blind-labels` for publication-oriented runs; it masks candidate names in the judge prompt and replaces obvious framework identifiers in the artifact text.

The judge prompt treats natural-language bullets, comments, and instruction strings as workflow semantics. That keeps the comparison focused on authoring representation rather than whether a Python baseline includes real tool implementations in the benchmark fixture.

This benchmark does not install or run every framework. That is a feature of the test, not a shortcut: MDScript is not competing as a Python runtime framework, so giving framework baselines their full runtime machinery would make the comparison less apples-to-apples for readability and workflow expression.

## Latest Result

The current publishable run used OpenAI `gpt-5.5` with `--blind-labels`. It completed all 30 judgments with zero parse failures.

<!-- latest LLM scripting benchmark summary from results/latest.json -->

| Rank | System | Overall | Performance | Readability | Simplicity | Fidelity |
| ---: | --- | ---: | ---: | ---: | ---: | ---: |
| 1 | MDScript | 8.57 | 7.67 | 9.00 | 9.33 | 8.67 |
| 2 | LMQL | 7.62 | 6.67 | 8.33 | 8.00 | 8.00 |
| 3 | OpenAI Agents SDK | 7.57 | 6.67 | 8.33 | 8.00 | 7.67 |
| 4 | Pydantic AI | 7.28 | 6.33 | 8.00 | 7.67 | 7.67 |
| 5 | Microsoft Agent Framework | 6.53 | 4.33 | 7.67 | 8.00 | 7.33 |
| 6 | Guidance | 6.48 | 5.00 | 7.67 | 6.67 | 7.67 |
| 7 | ell | 6.23 | 4.67 | 7.33 | 6.67 | 7.33 |
| 8 | LlamaIndex Workflows | 6.03 | 4.00 | 7.33 | 7.00 | 7.00 |
| 9 | LangGraph | 5.70 | 3.33 | 7.67 | 6.67 | 6.33 |
| 10 | DSPy | 5.15 | 3.00 | 6.67 | 5.33 | 7.33 |

Case winners:

- `release_notes`: MDScript, 8.90.
- `deploy_branch`: MDScript, 8.65.
- `onboard_service`: MDScript, 8.15.

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
  --env-file ../cortext/.env
```

Useful overrides:

```bash
python3 benchmarks/llm-scripting/benchmark.py --backend ollama --model gemma4:e4b
python3 benchmarks/llm-scripting/benchmark.py --model gemma4:e4b
python3 benchmarks/llm-scripting/benchmark.py --cases release_notes,deploy_branch
python3 benchmarks/llm-scripting/benchmark.py --systems mdscript,langgraph,guidance
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
