# MDScript vs Modern LLM Scripting Libraries

This analysis is based on `benchmarks/llm-scripting/results/latest.json`, generated with OpenAI `gpt-5.5` using `--blind-labels` at temperature `0`.

## Frontier Judge Result

`gpt-5.5` completed all 30 blinded judgments with zero parse failures.

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

## Interpretation

The frontier judge still preferred MDScript after candidate-name masking and a representation-level rubric. The reason was not raw feature depth; it was that MDScript expressed state, branches, and required user/tool actions with less indirection than the framework-style artifacts.

MDScript's best dimensions were readability and simplicity. The judge consistently noted clear staged workflows and easy-to-follow state transitions. Its lower performance and fidelity scores came from underspecified details in the specific benchmark scripts: exact git commands, artifact archive creation, Docker Compose-specific scaffolding, strict kebab-case enforcement, and explicit stop paths when a user declines confirmation. That is not a critique of the MDScript spec being freeform; it is a critique of how much determinism a workflow author chose to put into one particular script.

LMQL and OpenAI Agents SDK formed the strongest second tier. Both kept the workflow readable and compact, but the judge found more reliance on model interpretation for concrete tool use and state persistence. Pydantic AI followed closely with stronger typing but more boilerplate and still-vague operational behavior in the rendered artifact.

The graph/workflow frameworks scored lower in this representation-level test because their benchmark artifacts read as framework skeletons with natural-language workflow semantics layered into comments or instruction strings. The revised rubric counts those comments as semantics, but the judge still penalized them when state transitions and concrete actions were not as directly represented as MDScript bullets and links.

DSPy came last because it is not primarily a workflow scripting language. It can optimize language-model behavior, but this task asks for long-horizon operational workflow expression.

## Local Stress Result

The earlier small-model stress run used local Ollama `gemma4:e4b` and also completed all 30 judgments with zero parse failures. It ranked MDScript first at 9.23 overall, ahead of Microsoft Agent Framework at 8.77.

That local result is still useful, but it should be framed differently: it tests whether a weaker model can read and score the workflow artifacts. The `gpt-5.5` blinded run is the stronger publication candidate for judge quality.

## MDScript Strengths

- Very low ceremony: state headings, variables, links, and natural language.
- Strong human reviewability in plain Markdown.
- Good fit for repository-owned workflows where the host coding agent provides execution.
- Clear enough for both a small local judge and a frontier judge to track long-horizon state and branch requirements.

## MDScript Weaknesses

- No static type checking, schema validation, or tool contract enforcement.
- Branches and loops are understandable, but not mechanically enforced by a runtime.
- Runtime behavior depends on the host agent actually executing the instructions.
- Operational detail is script-author controlled. The language can stay freeform, but a workflow that needs reproducible behavior should include enough natural-language detail for the host agent to act consistently.
- It is weaker than graph frameworks for durable execution, checkpointing, observability, retries, and multi-agent coordination.

## Publishable Claim

The strongest defensible claim is:

> In representation-level LLM workflow authoring tasks, MDScript produced artifacts that frontier and small local judges rated as more readable and simpler than framework-style alternatives while preserving comparable task fidelity.

Do not claim that MDScript is a better runtime framework than LangGraph, LlamaIndex Workflows, Microsoft Agent Framework, OpenAI Agents SDK, or Pydantic AI. Those systems offer execution infrastructure that this benchmark intentionally does not exercise.

## Next Improvements

- Add an executor benchmark where the same small model must actually follow each artifact in a sandbox and produce files.
- Add pairwise judging in addition to scalar scoring to reduce score calibration artifacts.
- Add a second frontier judge from another provider to reduce single-model judge bias.
- Strengthen all candidate artifacts so each uses its idiomatic best representation rather than a common generated skeleton.
- Add cases where runtime features matter, such as resumable workflows, parallel tool calls, and checkpoint recovery.
