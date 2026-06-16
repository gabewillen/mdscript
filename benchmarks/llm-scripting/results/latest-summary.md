# LLM Scripting Benchmark Results

- Judge model: `gpt-5.5` via `openai`
- Run started: `2026-06-16T16:14:15+00:00`
- Cases: release_notes, deploy_branch, onboard_service

## Overall Averages

| Rank | System | Overall | Task Success | Requirements Met | Failure Recovery | Consistency |
| ---: | --- | ---: | ---: | ---: | ---: | ---: |
| 1 | LMQL | 7.37 | 7.67 | 8.33 | 5.0 | 6.67 |
| 2 | MDScript | 7.33 | 7.67 | 7.67 | 5.67 | 7.33 |
| 3 | Pydantic AI | 7.32 | 7.67 | 8.0 | 5.33 | 6.67 |
| 4 | Guidance | 7.02 | 7.33 | 8.0 | 5.0 | 5.67 |
| 5 | OpenAI Agents SDK | 6.92 | 7.0 | 7.67 | 5.33 | 6.67 |
| 6 | ell | 6.8 | 7.0 | 7.67 | 5.0 | 6.0 |
| 7 | Microsoft Agent Framework | 6.37 | 6.67 | 7.33 | 4.0 | 5.67 |
| 8 | LlamaIndex Workflows | 6.13 | 6.33 | 7.33 | 3.67 | 5.33 |
| 9 | LangGraph | 5.75 | 6.0 | 7.0 | 3.0 | 5.0 |
| 10 | DSPy | 5.7 | 5.67 | 7.33 | 3.67 | 4.0 |

## Case Winners

- `release_notes`: LMQL (7.75)
- `deploy_branch`: LMQL (8.05)
- `onboard_service`: OpenAI Agents SDK (7.0)

## Judge Notes By System

### LMQL
The artifact states nearly all required workflow behavior, but leaves some operational details and negative confirmation transitions ambiguous. The workflow addresses most required prompts and scaffolding steps, but misses Docker Compose handling and has weak validation and recovery semantics. The artifact directly encodes the requested changelog workflow and should usually succeed, but relies on the agent to fill in git command details and lacks robust failure handling.

### MDScript
The workflow satisfies most required deployment semantics, with minor ambiguity around packaging, failure stops, and branch/coverage confirmation rejection paths. The workflow satisfies most high-level scaffolding requirements but misses Docker Compose handling and leaves several validations and conditional branches vague. The workflow directly covers the main changelog generation path, but its categorization and recovery semantics are somewhat underspecified.

### Pydantic AI
The artifact captures nearly all required workflow semantics in instructions, but several operational details and some failure branches are underspecified. The workflow directly encodes most required interactions and scaffold actions, but misses Docker Compose-specific files and leaves validation and execution details somewhat underspecified. The artifact clearly encodes the required changelog workflow, but leaves command details and failure branches to the agent.

### Guidance
The artifact states nearly all required behavior in natural language, but the executable loop does not enforce the conditions or transitions, making outcomes dependent on the agent's faithful interpretation. The artifact describes most required scaffolding behavior, but omits Docker Compose-specific output and relies on loose LM-selected actions and states rather than robust enforced control flow. The artifact states most required behavior clearly enough for a capable agent, but relies on free-form action generation and has limited recovery or deterministic control.

### OpenAI Agents SDK
The workflow states most required behavior, but several key actions are underspecified enough that reliable end-to-end deployment would require agent inference. The workflow captures most required decisions and scaffold steps, but misses explicit Docker Compose handling and leaves several implementation and recovery details vague. The artifact directly encodes most required behavior and a capable agent would likely complete the changelog, but some command details, conventional prefix matching, and recovery/regeneration semantics are incomplete.

### ell
The artifact restates nearly all required workflow semantics, but several operational steps are underspecified enough to reduce reliability. The workflow captures most required interactions and scaffold actions, but misses Docker Compose file handling and relies on broad natural-language instructions for several critical generation details. The workflow semantics are mostly sufficient for a capable agent to produce CHANGELOG.md, but several operational details and recovery paths are left vague.

### Microsoft Agent Framework
The artifact states nearly all required workflow semantics, but relies on comments and has ambiguous conditional control flow, reducing reliability if executed as authored. The workflow semantically covers most onboarding steps, but misses Docker Compose-specific output and leaves several validations and recovery paths underspecified. The comments describe most core behavior, but the executable workflow state transitions and regeneration support are incomplete and some categorization semantics are imprecise.

### LlamaIndex Workflows
The artifact states nearly all required behaviors in comments, but the executable workflow lacks conditional transitions and concrete tool semantics, making correct end-to-end execution only moderately likely. The workflow would likely scaffold a useful service and satisfy most criteria, but Docker Compose handling and failure recovery are under-specified. The artifact describes enough for a capable agent to produce a basic changelog, but key behavior is underspecified or not represented in actual workflow transitions.

### LangGraph
The artifact states most required behavior in comments, but the executable graph is linear and lacks concrete branching, retries, rollback paths, or user-confirmation handling. The workflow comments describe most required behavior, but Docker Compose handling and robust validation/recovery are underspecified. The comments express most core requirements, but the executable workflow is linear and does not actually support the stated regeneration loop or robust failure handling.

### DSPy
The artifact states most required workflow semantics, but relies on a generative next-action loop without deterministic execution, state updates, or robust failure handling. The embedded workflow addresses most success criteria at a high level, but it relies on vague LLM state transitions and omits concrete Docker Compose handling. The workflow text captures most required behavior, but relies on vague LLM decisions without explicit tool calls, persisted outputs, or robust transitions.
