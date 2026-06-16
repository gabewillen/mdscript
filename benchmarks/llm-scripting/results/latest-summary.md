# LLM Scripting Benchmark Results

- Judge model: `gpt-5.5` via `openai`
- Run started: `2026-06-16T15:42:34+00:00`
- Cases: release_notes, deploy_branch, onboard_service

## Overall Averages

| Rank | System | Overall | Performance | Readability | Simplicity | Fidelity |
| ---: | --- | ---: | ---: | ---: | ---: | ---: |
| 1 | MDScript | 8.57 | 7.67 | 9.0 | 9.33 | 8.67 |
| 2 | LMQL | 7.62 | 6.67 | 8.33 | 8.0 | 8.0 |
| 3 | OpenAI Agents SDK | 7.57 | 6.67 | 8.33 | 8.0 | 7.67 |
| 4 | Pydantic AI | 7.28 | 6.33 | 8.0 | 7.67 | 7.67 |
| 5 | Microsoft Agent Framework | 6.53 | 4.33 | 7.67 | 8.0 | 7.33 |
| 6 | Guidance | 6.48 | 5.0 | 7.67 | 6.67 | 7.67 |
| 7 | ell | 6.23 | 4.67 | 7.33 | 6.67 | 7.33 |
| 8 | LlamaIndex Workflows | 6.03 | 4.0 | 7.33 | 7.0 | 7.0 |
| 9 | LangGraph | 5.7 | 3.33 | 7.67 | 6.67 | 6.33 |
| 10 | DSPy | 5.15 | 3.0 | 6.67 | 5.33 | 7.33 |

## Case Winners

- `release_notes`: MDScript (8.9)
- `deploy_branch`: MDScript (8.65)
- `onboard_service`: MDScript (8.15)

## Judge Notes By System

### MDScript
The workflow satisfies nearly all success criteria with clear readable steps, though a few state transitions and artifact creation details are underspecified. The artifact covers most required scaffolding decisions with readable steps, but misses Docker Compose-specific output and only partially enforces kebab-case. The artifact directly covers all success criteria with readable, simple steps, though it leaves exact git commands, edge cases, and some state details implicit.

### LMQL
The workflow closely matches the required behavior in readable state bullets, but relies on natural-language execution for deployment, artifact packaging, and metric interpretation. The workflow covers most interactive scaffolding requirements with readable states, but misses explicit Docker Compose artifacts and leaves some validation and conditional generation semantics underspecified. The workflow expresses all core requirements at a high level, but relies on the LLM to infer concrete git/file operations and state persistence details.

### OpenAI Agents SDK
The workflow captures nearly all required control-flow semantics, but practical execution is weakened by vague deployment, rollback, artifact creation, environment, and health-check details. The workflow is readable and mostly faithful, but it misses Docker Compose-specific scaffolding and leaves several implementation details underspecified. The artifact covers the core release-notes workflow clearly, but leaves several practical tool commands and edge-case transitions underspecified.

### Pydantic AI
The artifact captures nearly all required workflow semantics in clear instructions, but several operational steps remain underspecified. The artifact captures most required interactive choices in readable state bullets, but it omits Docker Compose file generation and only partially validates service names. The artifact expresses all core requirements in readable workflow instructions, but execution reliability is limited by vague tool usage and largely implicit state control.

### Microsoft Agent Framework
The authored comments cover nearly all success criteria, but executable control flow is mostly linear and omits explicit conditional transitions for failures, retries, and rollback. The artifact captures most required workflow semantics in readable comments, but lacks an explicit Docker Compose scaffold path and relies on vague comment-only state and tool behavior. The artifact covers the main release-note workflow in comments, but lacks concrete tool/state operations and does not actually model the regeneration loop.

### Guidance
The authored instructions cover most requirements clearly, but the executable control loop is weakly constrained and relies on the model to follow the prose exactly. The artifact expresses most required workflow semantics clearly, but relies on the model to choose and enforce actions and omits explicit Docker Compose deployment files. The artifact states most required workflow semantics clearly, but execution reliability is weakened by unconstrained LLM-selected actions and transitions rather than concrete tool calls or enforced state logic.

### ell
The artifact states nearly all required workflow behavior, but much of the practical execution is delegated to ambiguous model/tool decisions rather than explicit commands and transitions. The artifact captures most interactive requirements in readable workflow text, but it omits Docker Compose-specific file generation and relies on ambiguous model-mediated control flow. The artifact states most required workflow semantics, but leaves key tool calls and state transitions underspecified and only partially implements regeneration and maintenance-prefix categorization.

### LlamaIndex Workflows
The artifact describes all major requirements in comments, but the executable workflow does not implement the conditional asks, confirmations, retries, rollback paths, or artifact/environment state handling. The artifact expresses most required onboarding semantics clearly, but relies on comment-level behavior and omits deployment-specific Docker Compose scaffolding. The artifact captures most required behavior in comments, but the executable workflow does not actually run git or branch for regeneration and only partially defines conventional-prefix maintenance grouping.

### LangGraph
The artifact describes the intended deploy workflow in comments but the executable graph ignores those decisions and cannot reliably perform confirmations, retries, failures, or rollbacks. The artifact describes most of the scaffold flow clearly, but relies on comments rather than concrete state updates and misses Docker Compose file handling. The artifact states most required release-note semantics in comments, but the executable workflow is a fixed linear graph with vague git/write steps and no real regeneration path.

### DSPy
The artifact faithfully describes the desired deployment workflow, but practical reliability is limited by ambiguous LLM-controlled actions and missing concrete state/result handling. The workflow captures most required semantics in readable prose, but execution reliability is weak and Docker Compose plus strict kebab-case handling are missing. The embedded workflow text covers most requirements, but the actual artifact delegates state transitions to an LLM without executing git or write steps and lacks reliable context/state mutation.
