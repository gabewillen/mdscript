# LLM Scripting Benchmark Results

- Executor model: `gpt-5.5` via `openai`
- Judge model: `gpt-5.5` via `openai`
- Execution runs per artifact: `3`
- Judgments per execution: `3`
- Run started: `2026-06-16T16:56:47+00:00`
- Cases: release_notes, deploy_branch, onboard_service

## Overall Averages

| Rank | System | Overall | Task Success | Requirements Met | Failure Recovery | Std Dev | Judgments |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | OpenAI Agents SDK | 9.71 | 9.93 | 9.56 | 9.33 | 0.29 | 27 |
| 2 | DSPy | 9.54 | 9.81 | 9.44 | 8.85 | 0.3 | 27 |
| 3 | ell | 9.39 | 9.56 | 9.22 | 9.22 | 0.55 | 27 |
| 4 | Pydantic AI | 9.35 | 9.56 | 9.19 | 9.07 | 0.57 | 27 |
| 5 | Guidance | 9.22 | 9.33 | 9.15 | 9.04 | 0.73 | 27 |
| 6 | LMQL | 9.15 | 9.22 | 9.11 | 9.0 | 0.79 | 27 |
| 7 | LangGraph | 9.05 | 9.26 | 8.85 | 8.81 | 0.64 | 27 |
| 8 | LlamaIndex Workflows | 8.96 | 9.15 | 8.78 | 8.74 | 0.69 | 27 |
| 9 | Microsoft Agent Framework | 8.94 | 9.07 | 8.81 | 8.78 | 0.71 | 27 |
| 10 | MDScript | 8.87 | 8.89 | 8.93 | 8.67 | 0.75 | 27 |

## Case Winners

- `deploy_branch`: OpenAI Agents SDK (9.8)
- `onboard_service`: DSPy (9.75)
- `release_notes`: OpenAI Agents SDK (9.73)

## Judge Notes By System

### OpenAI Agents SDK
The execution completed the scenario successfully with correct ordering, artifact creation, deployment, and three-attempt health verification. The execution satisfies the scenario end-to-end, including ordered checks, artifact deployment, and successful recovery after two failed health checks. The result fully matches the provided scenario, with only untriggered conditional requirements supported by stated evidence rather than demonstrated actions.

### DSPy
The execution completes the scenario correctly end-to-end, with strong evidence for the applicable checks, build, deploy, and health retry behavior. The execution matches the provided scenario well, with only conditional failure/confirmation behaviors not directly demonstrated. The execution completes the scenario correctly, with only untriggered conditional requirements supported by assertions rather than observed actions.

### ell
The execution satisfies the scenario end-to-end, with only unexercised edge-case requirements lacking direct evidence. The execution completed the requested staging deployment successfully and handled the failing health checks with retries as expected. The result completes the scenario end-to-end with correct ordering, artifact deployment, and health-check retry behavior; missing-branch, main-confirmation, low-coverage, and deployment-failure rollback paths are only asserted rather than demonstrated.

### Pydantic AI
The execution completed the scenario correctly, with only untriggered conditional behaviors supported mainly by assertions rather than observed evidence. The execution completed the staging deployment successfully with correct ordering, artifact output, and three health-check attempts, while untriggered guardrail paths rely on stated evidence rather than observed actions. The scenario was completed end-to-end with the expected artifact and correct health-check retry behavior, with only untested conditional paths limiting full credit.

### Guidance
The execution completed the deployment flow and health retry behavior, but created the wrong artifact path compared with the expected artifact. The scenario completed successfully except the created artifact used the raw branch path instead of the expected sanitized timestamped artifact name. The execution completed the scenario successfully except for creating the artifact at the wrong path/name compared with the expected artifact.

### LMQL
The execution satisfies the scenario fully, with only untested conditional requirements relying on stated evidence rather than observed actions. The execution completed the requested staging deployment successfully and handled the failing health checks with retries as expected. The execution matches the scenario well, including ordered checks, build, staging deploy, and health-check retries, with only unexercised rollback/confirmation paths not directly demonstrated.

### LangGraph
The execution matches the scenario well, with only conditional failure and confirmation behaviors supported by stated evidence rather than observed actions. The execution completed the requested staging deployment successfully and demonstrated the required health-check retry behavior for this scenario. The execution satisfies the scenario end-to-end, with only untested conditional behaviors supported by claimed logic rather than observed actions.

### LlamaIndex Workflows
The scenario was completed end-to-end with the required checks, artifact, deployment, and health-check retry behavior; untriggered edge-case requirements are supported only by stated evidence. The result satisfies the scenario end-to-end, but several general requirements are supported only by claimed semantics rather than observed execution. The scenario was completed successfully with correct ordering and health-check retry behavior, though some untriggered success criteria are supported only by claimed semantics rather than observed actions.

### Microsoft Agent Framework
The execution completed the scenario end-to-end with correct ordering, artifact, deployment target, and health-check retry behavior. The produced result matches the scenario fully, with only untriggered conditional failure and confirmation paths relying on asserted evidence rather than observed actions. The execution satisfies the scenario end-to-end, with only untriggered confirmation and rollback requirements supported by claimed semantics rather than observed actions.

### MDScript
The scenario largely completed successfully, but the created artifact was dist/feature/checkout-health-{timestamp}.tar.gz instead of the expected dist/feature-checkout-health-{timestamp}.tar.gz. The run completed the main happy path and health retry scenario, but produced dist/feature/checkout-health-{timestamp}.tar.gz instead of the expected dist/feature-checkout-health-{timestamp}.tar.gz. The execution completes the scenario successfully except the artifact name/path differs from the expected dist/feature-checkout-health-{timestamp}.tar.gz.
