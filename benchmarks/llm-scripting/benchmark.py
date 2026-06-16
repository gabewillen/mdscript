#!/usr/bin/env python3
"""LLM-as-judge benchmark for MDScript and adjacent LLM workflow formats.

The benchmark compares concise source artifacts for the same workflow tasks.
It intentionally does not install or execute each framework; the measured
object is the workflow artifact a maintainer would read and an agent would
follow.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import os
import random
import re
import statistics
import textwrap
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


DEFAULT_MODEL = "gemma4:e4b"
DEFAULT_OPENAI_MODEL = "gpt-5.5"
RESULTS_DIR = Path(__file__).with_name("results")


SYSTEMS: dict[str, dict[str, str]] = {
    "mdscript": {
        "name": "MDScript",
        "kind": "Markdown state machine for coding agents",
    },
    "langgraph": {
        "name": "LangGraph",
        "kind": "Python graph workflow for stateful agents",
    },
    "llamaindex_workflows": {
        "name": "LlamaIndex Workflows",
        "kind": "Python event-driven agent workflow",
    },
    "microsoft_agent_framework": {
        "name": "Microsoft Agent Framework",
        "kind": "Python/.NET agent workflow framework",
    },
    "openai_agents": {
        "name": "OpenAI Agents SDK",
        "kind": "Python agent loop with tools, guardrails, and tracing",
    },
    "pydantic_ai": {
        "name": "Pydantic AI",
        "kind": "Typed Python agent framework",
    },
    "dspy": {
        "name": "DSPy",
        "kind": "Python LM programming framework with signatures/modules",
    },
    "guidance": {
        "name": "Guidance",
        "kind": "Prompt programming language embedded in Python",
    },
    "lmql": {
        "name": "LMQL",
        "kind": "Language-model query language",
    },
    "ell": {
        "name": "ell",
        "kind": "Python LMP functions for model programs",
    },
}


CASES: list[dict[str, Any]] = [
    {
        "id": "release_notes",
        "name": "Generate release notes",
        "source": "examples/generate-release-notes.md",
        "goal": "Collect commits from a git range, categorize them, and write CHANGELOG.md.",
        "inputs": ["git_range"],
        "success": [
            "Infers git_range from the last tag to HEAD when it is missing.",
            "Collects commits with git log.",
            "Groups feature, fix, and maintenance commits by conventional prefixes.",
            "Writes only nonempty sections to CHANGELOG.md.",
            "Supports regenerating notes without losing the workflow context.",
        ],
        "states": [
            {
                "id": "gather_changes",
                "title": "Gather Changes",
                "actions": [
                    "If git_range is empty, infer it from the last tag to HEAD.",
                    "Collect commits in git_range using git log.",
                    "Store commit subjects for categorization.",
                ],
                "next": "categorize_commits",
            },
            {
                "id": "categorize_commits",
                "title": "Categorize Commits",
                "actions": [
                    "Put commits matching feat: or feature: in features.",
                    "Put commits matching fix: or bug: in fixes.",
                    "Put every other commit in chores.",
                ],
                "next": "generate_notes",
            },
            {
                "id": "generate_notes",
                "title": "Generate Notes",
                "actions": [
                    "Write a Features section only when features is not empty.",
                    "Write a Bug Fixes section only when fixes is not empty.",
                    "Write a Maintenance section only when chores is not empty.",
                    "Write the final markdown to CHANGELOG.md.",
                    "If the user wants to regenerate, return to Gather Changes.",
                ],
                "next": None,
            },
        ],
    },
    {
        "id": "deploy_branch",
        "name": "Deploy branch",
        "source": "examples/deploy-branch.md",
        "goal": "Select a branch, run checks, build an artifact, deploy it, and verify health.",
        "inputs": ["branch", "environment", "deploy_url"],
        "success": [
            "Asks for a branch when branch is missing.",
            "Requires confirmation before deploying main.",
            "Runs typecheck and coverage tests before build.",
            "Warns and confirms when coverage is below 80 percent.",
            "Builds a timestamped artifact and deploys it to the requested environment.",
            "Rolls back and notifies the team on deployment failure.",
            "Retries health checks three times, then rolls back if still failing.",
        ],
        "states": [
            {
                "id": "select_branch",
                "title": "Select Branch",
                "actions": [
                    "If branch is empty, ask the user for the branch name.",
                    "If branch is main, warn that deployment requires approval.",
                    "Ask for confirmation before proceeding with main.",
                ],
                "next": "run_checks",
            },
            {
                "id": "run_checks",
                "title": "Run Checks",
                "actions": [
                    "Run npm run typecheck and stop with errors on failure.",
                    "Run npm run test -- --coverage.",
                    "If coverage is below 80 percent, warn and ask whether to proceed.",
                ],
                "next": "build_artifact",
            },
            {
                "id": "build_artifact",
                "title": "Build Artifact",
                "actions": [
                    "Run npm run build.",
                    "If build fails, return to Run Checks.",
                    "Set artifact to dist/{branch}-{timestamp}.tar.gz.",
                ],
                "next": "deploy",
            },
            {
                "id": "deploy",
                "title": "Deploy",
                "actions": [
                    "Deploy artifact to environment.",
                    "On success, notify Slack and continue to Verify Deployment.",
                    "On failure, roll back to the previous version, notify the team, and return to Select Branch.",
                ],
                "next": "verify_deployment",
            },
            {
                "id": "verify_deployment",
                "title": "Verify Deployment",
                "actions": [
                    "Run a health check against deploy_url/health.",
                    "Retry failed health checks up to three times.",
                    "If health passes, mark the deploy complete.",
                    "If health still fails after three retries, roll back and return to Select Branch.",
                ],
                "next": None,
            },
        ],
    },
    {
        "id": "onboard_service",
        "name": "Onboard service scaffold",
        "source": "examples/onboard-service.md",
        "goal": "Interactively scaffold a new service with language, infrastructure, and deployment choices.",
        "inputs": ["service_name"],
        "success": [
            "Asks for a service name when missing and enforces kebab-case.",
            "Supports Go, TypeScript, Rust, and custom runtimes.",
            "Captures database, messaging, HTTP framework, and deployment choices.",
            "Handles Kubernetes, Lambda, and Docker Compose deployment-specific files.",
            "Creates README, entrypoint, and conditional database/messaging stubs.",
            "Offers git initialization without doing it silently.",
            "Either starts local development or prints a scaffold summary.",
        ],
        "states": [
            {
                "id": "name_service",
                "title": "Name Service",
                "actions": [
                    "If service_name is empty, ask the user for a name.",
                    "If service_name has spaces or uppercase letters, warn and ask again for kebab-case.",
                    "Set service_path to services/{service_name}.",
                ],
                "next": "choose_language",
            },
            {
                "id": "choose_language",
                "title": "Choose Language",
                "actions": [
                    "Ask for language: Go, TypeScript, Rust, or other.",
                    "If language is other, ask for a custom runtime.",
                    "Set language_config from the chosen language or custom runtime.",
                ],
                "next": "pick_stack",
            },
            {
                "id": "pick_stack",
                "title": "Pick Stack",
                "actions": [
                    "Ask for database: PostgreSQL, SQLite, or none.",
                    "Ask for messaging: Kafka, NATS, or none.",
                    "Ask whether to use an HTTP framework or a raw server.",
                ],
                "next": "configure_deployment",
            },
            {
                "id": "configure_deployment",
                "title": "Configure Deployment",
                "actions": [
                    "Ask for deployment target: Kubernetes, Lambda, or Docker Compose.",
                    "If Kubernetes, ask whether a helm chart is needed.",
                    "If Lambda, ask for memory_size in MB.",
                    "Ask whether the service exposes a health endpoint.",
                ],
                "next": "scaffold",
            },
            {
                "id": "scaffold",
                "title": "Scaffold",
                "actions": [
                    "Create service_path/README.md with a service description.",
                    "Create a language-specific entrypoint from language_config.",
                    "If Kubernetes, create Dockerfile and deployment manifest.",
                    "If Lambda, create serverless.yml with memory_size.",
                    "If database is set, add a database connection module.",
                    "If messaging is set, add a producer/consumer stub.",
                    "Ask whether to initialize git; if yes, run git init.",
                ],
                "next": "verify",
            },
            {
                "id": "verify",
                "title": "Verify",
                "actions": [
                    "Ask whether to run the service locally now.",
                    "If yes, start the service in development mode.",
                    "If no, print the scaffold summary.",
                ],
                "next": None,
            },
        ],
    },
]


def slug_to_name(slug: str) -> str:
    return SYSTEMS[slug]["name"]


def state_function_name(state_id: str) -> str:
    return state_id.replace("-", "_")


def case_variables(case: dict[str, Any]) -> list[str]:
    variables = set(case["inputs"])
    variables.update(["timestamp"])
    for state in case["states"]:
        for action in state["actions"]:
            for token in re.findall(r"\b[a-z][a-z0-9_]*\b", action):
                if token in {
                    "artifact",
                    "branch",
                    "chores",
                    "commits",
                    "coverage",
                    "database",
                    "deploy_url",
                    "environment",
                    "features",
                    "fixes",
                    "git_range",
                    "health_endpoint",
                    "language",
                    "language_config",
                    "memory_size",
                    "messaging",
                    "service_name",
                    "service_path",
                }:
                    variables.add(token)
    return sorted(variables)


def numbered_requirements(case: dict[str, Any]) -> str:
    lines = [f"Goal: {case['goal']}", "", "Success criteria:"]
    for idx, item in enumerate(case["success"], 1):
        lines.append(f"{idx}. {item}")
    return "\n".join(lines)


def actions_comment(actions: list[str], indent: str = "    ") -> str:
    return "\n".join(f"{indent}# {action}" for action in actions)


def render_mdscript(case: dict[str, Any]) -> str:
    chunks = ["<!-- read [mdscript.md](../../README.md) -->"]
    replacements = {
        "language_config": "{{language_config}}",
        "health_endpoint": "{{health_endpoint}}",
        "service_name": "{{service_name}}",
        "service_path": "{{service_path}}",
        "memory_size": "{{memory_size}}",
        "deploy_url": "{{deploy_url}}",
        "git_range": "{{git_range}}",
        "environment": "{{environment}}",
        "timestamp": "{{timestamp}}",
        "database": "{{database}}",
        "messaging": "{{messaging}}",
        "artifact": "{{artifact}}",
        "language": "{{language}}",
        "branch": "{{branch}}",
    }
    variable_names = "|".join(re.escape(key) for key in replacements)
    brace_pattern = re.compile(r"\{(" + variable_names + r")\}")
    variable_pattern = re.compile(r"(?<!\{)\b(" + variable_names + r")\b(?!\})")
    for state in case["states"]:
        chunks.append(f"\n## {state['title']}\n")
        for action in state["actions"]:
            text = brace_pattern.sub(lambda match: replacements[match.group(1)], action)
            text = variable_pattern.sub(lambda match: replacements[match.group(1)], text)
            if "return to " in text:
                target = text.split("return to ", 1)[1].rstrip(".")
                text += f" [link target: {target}]"
            chunks.append(f"* {text}")
        if state["next"]:
            chunks.append(f"* continue to [{case_state_title(case, state['next'])}](#{state['next'].replace('_', '-')})")
    return "\n".join(chunks)


def case_state_title(case: dict[str, Any], state_id: str) -> str:
    for state in case["states"]:
        if state["id"] == state_id:
            return state["title"]
    raise KeyError(state_id)


def render_langgraph(case: dict[str, Any]) -> str:
    lines = [
        "from typing import Literal, TypedDict",
        "from langgraph.graph import END, StateGraph",
        "",
        "class WorkflowState(TypedDict, total=False):",
    ]
    for var in case_variables(case):
        lines.append(f"    {var}: str")
    lines += [
        "    retries: int",
        "    proceed: bool",
        "",
        "def ask(prompt: str) -> str: ...",
        "def run(command: str) -> str: ...",
        "def write_file(path: str, body: str) -> None: ...",
        "def notify(target: str, message: str) -> None: ...",
        "",
    ]
    for state in case["states"]:
        fn = state_function_name(state["id"])
        next_id = state["next"] or "END"
        lines.append(f"def {fn}(state: WorkflowState) -> WorkflowState:")
        lines.append(actions_comment(state["actions"]))
        lines.append("    state = dict(state)")
        lines.append(f"    state['last_state'] = '{state['id']}'")
        lines.append(f"    state['next'] = '{next_id}'")
        lines.append("    return state")
        lines.append("")
    lines += [
        "def route(state: WorkflowState) -> str:",
        "    return state.get('next', END)",
        "",
        "graph = StateGraph(WorkflowState)",
    ]
    for state in case["states"]:
        fn = state_function_name(state["id"])
        lines.append(f"graph.add_node('{state['id']}', {fn})")
    lines.append(f"graph.set_entry_point('{case['states'][0]['id']}')")
    for state in case["states"]:
        if state["next"]:
            lines.append(f"graph.add_edge('{state['id']}', '{state['next']}')")
        else:
            lines.append(f"graph.add_edge('{state['id']}', END)")
    lines.append("workflow = graph.compile()")
    return "\n".join(lines)


def render_llamaindex_workflows(case: dict[str, Any]) -> str:
    lines = [
        "from llama_index.core.workflow import Event, StartEvent, StopEvent, Workflow, step",
        "",
        "class WorkflowEvent(Event):",
        "    state: dict",
        "",
    ]
    for state in case["states"]:
        lines.append(f"class {state_function_name(state['id']).title().replace('_', '')}Event(WorkflowEvent):")
        lines.append("    pass")
        lines.append("")
    lines.append(f"class {case['id'].title().replace('_', '')}Workflow(Workflow):")
    first_event = f"{state_function_name(case['states'][0]['id']).title().replace('_', '')}Event"
    lines.append("    @step")
    lines.append(f"    async def start(self, ev: StartEvent) -> {first_event}:")
    lines.append("        return " + first_event + "(state=dict(ev))")
    lines.append("")
    for state in case["states"]:
        event_name = f"{state_function_name(state['id']).title().replace('_', '')}Event"
        next_event = (
            f"{state_function_name(state['next']).title().replace('_', '')}Event"
            if state["next"]
            else "StopEvent"
        )
        lines.append("    @step")
        lines.append(f"    async def {state_function_name(state['id'])}(self, ev: {event_name}) -> {next_event}:")
        lines.append(actions_comment(state["actions"], indent="        "))
        lines.append("        state = dict(ev.state)")
        lines.append(f"        state['last_state'] = '{state['id']}'")
        if state["next"]:
            lines.append(f"        return {next_event}(state=state)")
        else:
            lines.append("        return StopEvent(result=state)")
        lines.append("")
    return "\n".join(lines)


def render_microsoft_agent_framework(case: dict[str, Any]) -> str:
    lines = [
        "from agent_framework import AgentWorkflowBuilder, WorkflowContext, workflow_step",
        "",
        "builder = AgentWorkflowBuilder(name='" + case["id"] + "')",
        "",
    ]
    for state in case["states"]:
        fn = state_function_name(state["id"])
        lines.append("@workflow_step(name='" + state["id"] + "')")
        lines.append(f"async def {fn}(ctx: WorkflowContext) -> dict:")
        lines.append(actions_comment(state["actions"]))
        lines.append("    await ctx.trace('completed " + state["id"] + "')")
        lines.append("    return dict(ctx.state)")
        lines.append("")
        lines.append(f"builder.add_step({fn})")
    lines.append(f"builder.set_start('{case['states'][0]['id']}')")
    for state in case["states"]:
        if state["next"]:
            lines.append(f"builder.add_transition('{state['id']}', '{state['next']}')")
        else:
            lines.append(f"builder.add_terminal('{state['id']}')")
    lines.append("workflow = builder.build()")
    return "\n".join(lines)


def render_openai_agents(case: dict[str, Any]) -> str:
    steps = format_steps_for_prompt(case)
    return textwrap.dedent(
        f"""
        from agents import Agent, Runner, function_tool

        @function_tool
        def ask_user(question: str) -> str: ...

        @function_tool
        def run_shell(command: str) -> str: ...

        @function_tool
        def write_file(path: str, body: str) -> str: ...

        @function_tool
        def notify_team(message: str) -> str: ...

        workflow_agent = Agent(
            name="{case['name']}",
            instructions=\"\"\"
        You execute this repository workflow exactly. Keep state variables across
        steps, ask before destructive or ambiguous actions, and use tools rather
        than only describing actions.

        {steps}
            \"\"\",
            tools=[ask_user, run_shell, write_file, notify_team],
        )

        result = Runner.run_sync(workflow_agent, input="{case['goal']}")
        """
    ).strip()


def render_pydantic_ai(case: dict[str, Any]) -> str:
    steps = format_steps_for_prompt(case)
    return textwrap.dedent(
        f"""
        from pydantic import BaseModel
        from pydantic_ai import Agent, RunContext

        class WorkflowState(BaseModel):
            values: dict[str, str] = {{}}
            completed_states: list[str] = []
            next_state: str | None = None

        class WorkflowDecision(BaseModel):
            action: str
            next_state: str | None
            reason: str

        agent = Agent(
            "repo-workflow-agent",
            output_type=WorkflowDecision,
            instructions=\"\"\"
        Follow the workflow as typed state. Use tools for repository actions.
        Preserve variables and branch exactly as specified.

        {steps}
            \"\"\",
        )

        @agent.tool
        async def ask_user(ctx: RunContext[WorkflowState], question: str) -> str: ...

        @agent.tool
        async def run_shell(ctx: RunContext[WorkflowState], command: str) -> str: ...

        @agent.tool
        async def write_file(ctx: RunContext[WorkflowState], path: str, body: str) -> str: ...
        """
    ).strip()


def render_dspy(case: dict[str, Any]) -> str:
    steps = format_steps_for_prompt(case)
    return textwrap.dedent(
        f"""
        import dspy

        class NextWorkflowAction(dspy.Signature):
            \"\"\"Choose and justify the next repository workflow action.\"\"\"

            task: str = dspy.InputField()
            current_state: str = dspy.InputField()
            variables: dict = dspy.InputField()
            next_action: str = dspy.OutputField()
            next_state: str = dspy.OutputField()

        class {case['id'].title().replace('_', '')}(dspy.Module):
            def __init__(self):
                self.decide = dspy.ChainOfThought(NextWorkflowAction)

            def forward(self, variables: dict):
                workflow = \"\"\"{steps}\"\"\"
                current_state = "{case['states'][0]['id']}"
                transcript = []
                while current_state != "done":
                    decision = self.decide(
                        task=workflow,
                        current_state=current_state,
                        variables=variables,
                    )
                    transcript.append(decision.next_action)
                    current_state = decision.next_state
                return transcript
        """
    ).strip()


def render_guidance(case: dict[str, Any]) -> str:
    steps = format_steps_for_prompt(case)
    first = case["states"][0]["id"]
    return textwrap.dedent(
        f"""
        import guidance
        from guidance import gen, select

        @guidance
        def workflow(lm, user_input):
            lm += \"\"\"Execute the repository workflow. Use the exact states and
        conditions below, maintain variables, and stop only after success.

        {steps}
        \"\"\"
            state = "{first}"
            while state != "done":
                lm += f"Current state: {{state}}\\n"
                lm += "Choose the next concrete action: " + gen("action", stop="\\n")
                lm += "Choose next state: " + select(
                    list({[s['id'] for s in case['states']]}) + ["done"],
                    name="next_state",
                )
                state = lm["next_state"]
            return lm
        """
    ).strip()


def render_lmql(case: dict[str, Any]) -> str:
    steps = format_steps_for_prompt(case)
    states = ", ".join(f'"{s["id"]}"' for s in case["states"])
    return textwrap.dedent(
        f"""
        argmax
            \"\"\"You are executing a repo workflow.

            {steps}

            Current variables: {{{{variables}}}}
            At each turn, emit ACTION and NEXT_STATE. Use tools for shell and file work.
            ACTION: [ACTION]
            NEXT_STATE: [NEXT_STATE]
            \"\"\"
        from
            "local-or-hosted-llm"
        where
            STOPS_AT(ACTION, "\\n") and
            NEXT_STATE in [{states}, "done"]
        """
    ).strip()


def render_ell(case: dict[str, Any]) -> str:
    steps = format_steps_for_prompt(case)
    return textwrap.dedent(
        f"""
        import ell

        @ell.tool()
        def ask_user(question: str) -> str: ...

        @ell.tool()
        def run_shell(command: str) -> str: ...

        @ell.tool()
        def write_file(path: str, body: str) -> str: ...

        @ell.complex(model="repo-workflow-model", tools=[ask_user, run_shell, write_file])
        def choose_next_action(state: dict) -> list:
            return [
                ell.system(\"\"\"Execute this workflow exactly and return the next tool
        call or state transition. Keep variables explicit.

        {steps}
                \"\"\"),
                ell.user(str(state)),
            ]

        def run_workflow(inputs: dict):
            state = {{"state": "{case['states'][0]['id']}", **inputs}}
            while state["state"] != "done":
                state.update(choose_next_action(state))
            return state
        """
    ).strip()


RENDERERS = {
    "mdscript": render_mdscript,
    "langgraph": render_langgraph,
    "llamaindex_workflows": render_llamaindex_workflows,
    "microsoft_agent_framework": render_microsoft_agent_framework,
    "openai_agents": render_openai_agents,
    "pydantic_ai": render_pydantic_ai,
    "dspy": render_dspy,
    "guidance": render_guidance,
    "lmql": render_lmql,
    "ell": render_ell,
}


def format_steps_for_prompt(case: dict[str, Any]) -> str:
    lines = [numbered_requirements(case), "", "Workflow states:"]
    for state in case["states"]:
        lines.append(f"- {state['title']} ({state['id']}):")
        for action in state["actions"]:
            lines.append(f"  - {action}")
        if state["next"]:
            lines.append(f"  - Default next state: {state['next']}.")
        else:
            lines.append("  - Terminal state.")
    return "\n".join(lines)


def static_metrics(artifact: str) -> dict[str, int]:
    lines = [line for line in artifact.splitlines() if line.strip()]
    lower = artifact.lower()
    return {
        "chars": len(artifact),
        "nonblank_lines": len(lines),
        "branch_markers": sum(lower.count(token) for token in [" if ", "if ", "else", "return to", "add_edge", "transition", "where"]),
        "dependency_markers": sum(lower.count(token) for token in ["import ", "from ", "@", "agent", "workflow", "graph"]),
        "state_mentions": sum(lower.count(token) for token in ["state", "step", "event", "node"]),
    }


def anonymize_artifact(system_slug: str, artifact: str) -> str:
    replacements = {
        "mdscript": "workflow_spec",
        "MDScript": "WorkflowSpec",
        "LangGraph": "GraphRuntime",
        "langgraph": "graph_runtime",
        "llama_index": "event_runtime",
        "LlamaIndex": "EventRuntime",
        "agent_framework": "workflow_runtime",
        "AgentWorkflowBuilder": "WorkflowBuilder",
        "OpenAI": "ModelProvider",
        "from agents": "from agent_runtime",
        "pydantic_ai": "typed_agent_runtime",
        "Pydantic": "TypedModel",
        "dspy": "lm_modules",
        "DSPy": "LMModules",
        "guidance": "prompt_runtime",
        "Guidance": "PromptRuntime",
        "lmql": "query_runtime",
        "LMQL": "QueryRuntime",
        "ell": "lmp_runtime",
    }
    masked = artifact
    for old, new in replacements.items():
        masked = masked.replace(old, new)
    return masked


def build_prompt(case: dict[str, Any], system_slug: str, artifact: str, blind_labels: bool) -> str:
    system = SYSTEMS[system_slug]
    if blind_labels:
        candidate_header = textwrap.dedent(
            f"""
            Candidate:
            - id: candidate_{list(SYSTEMS).index(system_slug) + 1:02d}
            - kind: anonymized workflow artifact
            """
        ).strip()
        artifact_for_judge = anonymize_artifact(system_slug, artifact)
    else:
        candidate_header = textwrap.dedent(
            f"""
            Candidate:
            - id: {system_slug}
            - name: {system['name']}
            - kind: {system['kind']}
            """
        ).strip()
        artifact_for_judge = artifact
    return textwrap.dedent(
        f"""
        You are judging one LLM workflow artifact against one task. Score only the
        source artifact shown below, not the general reputation of the ecosystem.
        Assume a capable coding agent can execute normal shell, file, ask-user,
        notification, and deployment tools when the artifact clearly asks for them.
        This is a workflow-authoring comparison: natural-language bullets,
        comments, and instruction strings are part of the authored workflow
        semantics when they are how the artifact expresses behavior. Do not
        penalize omitted host tool implementations or framework plumbing marked
        with ellipses. Do penalize missing workflow requirements, ambiguous state
        transitions, vague tool use, or semantics that are only implied.

        Task:
        {numbered_requirements(case)}

        {candidate_header}

        Artifact:
        ```text
        {artifact_for_judge}
        ```

        Rubric, 1 to 10:
        - performance: expected execution reliability and practical efficiency for
          this task. Reward explicit state, branches, failure handling, and low
          incidental runtime overhead. Penalize ambiguity, hidden control flow, or
          likely tool-use mistakes.
        - readability: how easily a human maintainer can review and modify the
          workflow artifact.
        - simplicity: how little syntax, boilerplate, indirection, and framework
          knowledge are needed for this task.
        - fidelity: coverage of every success criterion.

        Return only compact JSON with this schema:
        {{
          "candidate": "{system_slug}",
          "case": "{case['id']}",
          "performance": 1,
          "readability": 1,
          "simplicity": 1,
          "fidelity": 1,
          "overall": 1,
          "strengths": ["short phrase"],
          "weaknesses": ["short phrase"],
          "notes": "one sentence"
        }}
        """
    ).strip()


def call_ollama(model: str, prompt: str, timeout: int) -> str:
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You are a precise benchmark judge. Return valid JSON only.",
            },
            {"role": "user", "content": prompt},
        ],
        "stream": False,
        "format": "json",
        "options": {"temperature": 0, "num_ctx": 16384},
    }
    req = urllib.request.Request(
        "http://127.0.0.1:11434/api/chat",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        body = json.loads(response.read().decode("utf-8"))
    return body["message"]["content"]


def load_env_file(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(path)
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'\"")
        if key and key not in os.environ:
            os.environ[key] = value


def call_openai(model: str, prompt: str, timeout: int) -> str:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")
    base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    payload = {
        "model": model,
        "input": [
            {
                "role": "system",
                "content": "You are a precise benchmark judge. Return valid JSON only.",
            },
            {"role": "user", "content": prompt},
        ],
        "text": {"format": {"type": "json_object"}},
    }
    req = urllib.request.Request(
        f"{base_url}/responses",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"OpenAI API error {exc.code}: {detail[:1000]}") from exc
    if isinstance(body.get("output_text"), str):
        return body["output_text"]
    output = body.get("output", [])
    texts: list[str] = []
    for item in output:
        for content in item.get("content", []):
            text = content.get("text")
            if isinstance(text, str):
                texts.append(text)
    if texts:
        return "\n".join(texts)
    raise ValueError(f"no text output in OpenAI response: {body.keys()}")


def call_judge(backend: str, model: str, prompt: str, timeout: int) -> str:
    if backend == "ollama":
        return call_ollama(model, prompt, timeout)
    if backend == "openai":
        return call_openai(model, prompt, timeout)
    raise ValueError(f"unknown backend: {backend}")


def extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError(f"no JSON object found in: {text[:200]}")
    return json.loads(text[start : end + 1])


def clamp_score(value: Any) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return math.nan
    return max(1.0, min(10.0, number))


def normalize_judgment(raw: dict[str, Any], case_id: str, system_slug: str) -> dict[str, Any]:
    scores = {
        "performance": clamp_score(raw.get("performance")),
        "readability": clamp_score(raw.get("readability")),
        "simplicity": clamp_score(raw.get("simplicity")),
        "fidelity": clamp_score(raw.get("fidelity")),
    }
    if any(math.isnan(score) for score in scores.values()):
        raise ValueError(f"missing numeric score in {raw}")
    calculated_overall = (
        0.35 * scores["performance"]
        + 0.25 * scores["readability"]
        + 0.25 * scores["simplicity"]
        + 0.15 * scores["fidelity"]
    )
    overall = clamp_score(raw.get("overall", calculated_overall))
    if math.isnan(overall):
        overall = calculated_overall
    return {
        "case": case_id,
        "candidate": system_slug,
        **scores,
        "overall": round(overall, 2),
        "weighted_overall": round(calculated_overall, 2),
        "strengths": list(raw.get("strengths") or [])[:3],
        "weaknesses": list(raw.get("weaknesses") or [])[:3],
        "notes": str(raw.get("notes", ""))[:500],
    }


def judge_candidate(
    case: dict[str, Any],
    system_slug: str,
    artifact: str,
    backend: str,
    model: str,
    blind_labels: bool,
    timeout: int,
    retries: int,
) -> dict[str, Any]:
    prompt = build_prompt(case, system_slug, artifact, blind_labels)
    last_error: str | None = None
    raw_text = ""
    for _ in range(retries + 1):
        try:
            raw_text = call_judge(backend, model, prompt, timeout)
            raw = extract_json(raw_text)
            result = normalize_judgment(raw, case["id"], system_slug)
            result["raw_response"] = raw_text
            return result
        except (json.JSONDecodeError, KeyError, ValueError, urllib.error.URLError, TimeoutError) as exc:
            last_error = repr(exc)
            prompt += "\n\nYour previous answer was not valid JSON. Return only the required JSON object."
    return {
        "case": case["id"],
        "candidate": system_slug,
        "performance": math.nan,
        "readability": math.nan,
        "simplicity": math.nan,
        "fidelity": math.nan,
        "overall": math.nan,
        "weighted_overall": math.nan,
        "strengths": [],
        "weaknesses": [last_error or "unknown judge error"],
        "notes": "judge failed",
        "raw_response": raw_text,
    }


def aggregate(results: list[dict[str, Any]]) -> dict[str, Any]:
    by_candidate: dict[str, list[dict[str, Any]]] = {slug: [] for slug in SYSTEMS}
    by_case: dict[str, list[dict[str, Any]]] = {case["id"]: [] for case in CASES}
    for result in results:
        by_candidate[result["candidate"]].append(result)
        by_case[result["case"]].append(result)

    def mean_score(items: list[dict[str, Any]], key: str) -> float:
        values = [item[key] for item in items if not math.isnan(float(item[key]))]
        return round(statistics.mean(values), 2) if values else math.nan

    candidate_summary = {}
    for slug, items in by_candidate.items():
        candidate_summary[slug] = {
            "name": slug_to_name(slug),
            "performance": mean_score(items, "performance"),
            "readability": mean_score(items, "readability"),
            "simplicity": mean_score(items, "simplicity"),
            "fidelity": mean_score(items, "fidelity"),
            "overall": mean_score(items, "weighted_overall"),
        }

    case_winners = {}
    for case_id, items in by_case.items():
        valid = [item for item in items if not math.isnan(float(item["weighted_overall"]))]
        if valid:
            winner = max(valid, key=lambda item: item["weighted_overall"])
            case_winners[case_id] = {
                "candidate": winner["candidate"],
                "name": slug_to_name(winner["candidate"]),
                "score": winner["weighted_overall"],
            }

    return {
        "candidate_summary": candidate_summary,
        "case_winners": case_winners,
    }


def render_summary(run: dict[str, Any]) -> str:
    summary = run["summary"]["candidate_summary"]
    ordered = sorted(summary.items(), key=lambda item: item[1]["overall"], reverse=True)
    lines = [
        "# LLM Scripting Benchmark Results",
        "",
        f"- Judge model: `{run['judge']['model']}` via `{run['judge']['backend']}`",
        f"- Run started: `{run['started_at']}`",
        f"- Cases: {', '.join(case['id'] for case in CASES)}",
        "",
        "## Overall Averages",
        "",
        "| Rank | System | Overall | Performance | Readability | Simplicity | Fidelity |",
        "| ---: | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for rank, (slug, item) in enumerate(ordered, 1):
        lines.append(
            f"| {rank} | {item['name']} | {item['overall']} | {item['performance']} | "
            f"{item['readability']} | {item['simplicity']} | {item['fidelity']} |"
        )

    lines += ["", "## Case Winners", ""]
    for case_id, winner in run["summary"]["case_winners"].items():
        lines.append(f"- `{case_id}`: {winner['name']} ({winner['score']})")

    lines += ["", "## Judge Notes By System", ""]
    for slug, item in ordered:
        result_notes = [
            result
            for result in run["results"]
            if result["candidate"] == slug and result.get("notes")
        ]
        notes = " ".join(result["notes"] for result in result_notes[:3])
        lines.append(f"### {item['name']}")
        lines.append(notes or "No notes.")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(run: dict[str, Any], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = run["started_at"].replace(":", "").replace("-", "").replace("+", "Z")
    backend = re.sub(r"[^A-Za-z0-9_.-]+", "-", run["judge"]["backend"])
    model = re.sub(r"[^A-Za-z0-9_.-]+", "-", run["judge"]["model"])
    output_path = output_dir / f"{timestamp}-{backend}-{model}.json"
    output_path.write_text(json.dumps(run, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    latest_path = output_dir / "latest.json"
    latest_path.write_text(json.dumps(run, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    summary_path = output_dir / "latest-summary.md"
    summary_path.write_text(render_summary(run), encoding="utf-8")
    print(f"Wrote {output_path}")
    print(f"Wrote {latest_path}")
    print(f"Wrote {summary_path}")


def select_cases(case_ids: str | None) -> list[dict[str, Any]]:
    if not case_ids:
        return CASES
    wanted = {case_id.strip() for case_id in case_ids.split(",") if case_id.strip()}
    cases = [case for case in CASES if case["id"] in wanted]
    missing = wanted - {case["id"] for case in cases}
    if missing:
        raise SystemExit(f"unknown cases: {', '.join(sorted(missing))}")
    return cases


def select_systems(system_ids: str | None) -> list[str]:
    if not system_ids:
        return list(SYSTEMS)
    wanted = [system_id.strip() for system_id in system_ids.split(",") if system_id.strip()]
    missing = [system_id for system_id in wanted if system_id not in SYSTEMS]
    if missing:
        raise SystemExit(f"unknown systems: {', '.join(missing)}")
    return wanted


def run_benchmark(args: argparse.Namespace) -> dict[str, Any]:
    if args.env_file:
        load_env_file(args.env_file)
    cases = select_cases(args.cases)
    systems = select_systems(args.systems)
    started_at = dt.datetime.now(dt.UTC).isoformat(timespec="seconds")
    rng = random.Random(args.seed)
    jobs = [(case, system) for case in cases for system in systems]
    rng.shuffle(jobs)

    results: list[dict[str, Any]] = []
    artifacts: dict[str, dict[str, Any]] = {}
    for index, (case, system_slug) in enumerate(jobs, 1):
        artifact = RENDERERS[system_slug](case)
        artifacts[f"{case['id']}::{system_slug}"] = {
            "case": case["id"],
            "candidate": system_slug,
            "metrics": static_metrics(artifact),
            "artifact": artifact,
        }
        print(f"[{index}/{len(jobs)}] judging {case['id']} / {system_slug}", flush=True)
        if args.dry_run:
            judgment = {
                "case": case["id"],
                "candidate": system_slug,
                "performance": math.nan,
                "readability": math.nan,
                "simplicity": math.nan,
                "fidelity": math.nan,
                "overall": math.nan,
                "weighted_overall": math.nan,
                "strengths": [],
                "weaknesses": [],
                "notes": "dry run",
            }
        else:
            judgment = judge_candidate(
                case=case,
                system_slug=system_slug,
                artifact=artifact,
                backend=args.backend,
                model=args.model,
                blind_labels=args.blind_labels,
                timeout=args.timeout,
                retries=args.retries,
            )
        judgment["static_metrics"] = static_metrics(artifact)
        results.append(judgment)

    run = {
        "started_at": started_at,
        "judge": {
            "backend": args.backend,
            "model": args.model,
            "blind_labels": args.blind_labels,
            "temperature": 0,
            "seed": args.seed,
            "rubric": {
                "overall_formula": "0.35 performance + 0.25 readability + 0.25 simplicity + 0.15 fidelity",
                "scale": "1-10, higher is better",
            },
        },
        "cases": [
            {
                "id": case["id"],
                "name": case["name"],
                "source": case["source"],
                "goal": case["goal"],
                "success": case["success"],
            }
            for case in cases
        ],
        "systems": SYSTEMS,
        "artifacts": artifacts,
        "results": sorted(results, key=lambda item: (item["case"], item["candidate"])),
    }
    run["summary"] = aggregate(run["results"])
    return run


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", choices=["ollama", "openai"], default="ollama")
    parser.add_argument("--model", help="Model to use as judge")
    parser.add_argument("--cases", help="Comma-separated case ids")
    parser.add_argument("--systems", help="Comma-separated system ids")
    parser.add_argument("--env-file", type=Path, help="Optional env file containing OPENAI_API_KEY")
    parser.add_argument("--blind-labels", action="store_true", help="Hide candidate names in judge prompts")
    parser.add_argument("--output-dir", type=Path, default=RESULTS_DIR)
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--retries", type=int, default=1)
    parser.add_argument("--seed", type=int, default=17)
    parser.add_argument("--dry-run", action="store_true", help="Render artifacts without LLM calls")
    args = parser.parse_args()
    if args.model is None:
        args.model = DEFAULT_OPENAI_MODEL if args.backend == "openai" else DEFAULT_MODEL
    return args


def main() -> None:
    args = parse_args()
    run = run_benchmark(args)
    write_outputs(run, args.output_dir)


if __name__ == "__main__":
    main()
