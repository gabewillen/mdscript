# MDScript

<!--
<mdscript>
  <required-executor>mdscript-exec</required-executor>
  <fallback>read spec.md</fallback>
</mdscript>
-->

## What is MDScript?

MDScript is a minimal scripting format for guiding LLMs in coding assistants like Cursor and Claude Code. It uses plain Markdown with just enough structure to create reliable, repeatable workflows.

## How MDScript works

Three things have special meaning: `##` headings are states, `{{variables}}` are
filled in as the workflow runs, and Markdown links jump between states or into
other files. Everything else is plain natural-language instructions the LLM
**executes** (not narrates). States run top-to-bottom unless a link redirects.

```markdown
## Select Branch

* if `{{branch}}` is empty
  * ask the user which branch to deploy
  * [Select Branch](#select-branch)

## Run Checks
* run `npm run typecheck`
  * if it fails, stop and report the errors
```

The full execution rules (variables, links, control flow, heading entry points,
composition across files, and the "execute, don't narrate" contract) live in
**[spec.md](spec.md)**. MDScript files point an executor at the spec with a header
comment:

```markdown
<!-- mdscript: use the mdscript-exec skill or read [spec.md](https://raw.githubusercontent.com/gabewillen/mdscript/main/spec.md) -->
```

## Use Cases

MDScript is designed for **version-controlled workflows** in repositories:

```
.cursor/
  commands/
    generate-product.md
    generate-feature.md
    generate-use-case.md
  templates/
    feature.template.md
    use-case.template.md
```

Developers can read and edit these workflows as normal Markdown. AI assistants
execute them to maintain consistency across the codebase. For complete worked
examples see `examples/`, and for the execution rules see **[spec.md](spec.md)**.

## Design Philosophy

* **No declarations** - Variables and logic emerge from natural language
* **Minimal syntax** - Only headings, variables, and links have special meaning
* **Human readable** - Developers can understand and modify workflows
* **LLM executable** - Structure is simple enough for consistent interpretation
* **Version controlled** - Workflows live in the repository alongside code

MDScript bridges human readability with machine executability by keeping structure minimal and relying on LLM language understanding for everything else.

## Benchmarks

MDScript is compared against idiomatic, hand-authored Guidance, LMQL, and ell
artifacts on the same repository workflows. The benchmark lives in
`benchmarks/robust/` and is built to *discriminate* rather than to flatter:
scenarios force specific conditional branches, the primary metric is a
deterministic checklist of observable behaviors (not a holistic LLM vibe score),
the executor (`claude-haiku`) and judge (`claude-sonnet`, blind) are separate
models, and MDScript executions are given the spec so the format is judged with
its manual. See `benchmarks/robust/README.md` for the full methodology and
honest limitations (execution is stochastic; only the grading is deterministic).

> An earlier `benchmarks/llm-scripting/` run reported a 9.65-9.73 ranking. On
> re-running it those differences proved to be inside the noise floor (all four
> systems within ~0.1 of each other, sub-1-standard-error gaps, rank order not
> reproducible). It is kept for history; the results below supersede it.

**Outcome correctness: deterministic checklist (primary), blind judge (secondary).**
16 branch-forcing scenarios across three cases, two repeats each.

| System | Checklist % | sd | Blind judge (1-10) |
| --- | ---: | ---: | ---: |
| MDScript | 100 | 0 | 9.00 |
| LMQL (idiomatic) | 100 | 0 | 8.66 |
| ell (idiomatic) | 96.1 | 15.9 | 8.06 |
| Guidance (idiomatic) | 95.8 | 18.2 | 8.28 |

MDScript reaches the ceiling on the deterministic metric with nothing but the
spec, and leads the blind judge. A format you can fully learn in 90 seconds
drove correct branch/loop/recovery behavior as reliably as the code-hosted DSLs.

**Agent-to-agent delegation: the jump-point advantage (`benchmarks/robust/relay/`).**
Every `##` heading is a stable entry point, so one agent can dispatch another to
`workflow.md#heading` and resume a shared workflow mid-flow. A multi-hop relay
(haiku workers dispatched to enter at each state with injected variables) shows:

| System | Lines to become dispatchable | Handoff correctness | Readability with that plumbing |
| --- | ---: | ---: | ---: |
| MDScript | **+0** | 86% | **9.00** |
| Guidance | +34 | 88% | 6.43 |
| ell | +35 | 88% | 7.29 |
| LMQL | +42 | 86% | 6.43 |

Handoff correctness is a tie (zero jump failures across all formats). MDScript
does not *execute* a relay better. The difference is cost: MDScript is
dispatchable-at-a-state for free because headings are already addressable, while
the DSLs need ~34-42 lines of dispatch plumbing (roughly doubling the file),
which also drops their readability by 1-1.5 points in a blind panel.

**Composition: reusable sub-scripts via links (`benchmarks/robust/compose/`).**
A Markdown link to another file means "execute that file," so workflows decompose
into small reusable scripts. Two parent workflows share two sub-components
(checks, deploy):

| System | Wiring lines to reuse | Click-navigable refs (GitHub) | Compose correctness |
| --- | ---: | ---: | ---: |
| MDScript | **0** | **4/4 (100%)** | tie (~90-100%) |
| Guidance | 8 | 0/4 (0%) | tie |
| LMQL | 8 | 0/4 (0%) | tie |
| ell | 8 | 0/4 (0%) | tie |

Again execution is a tie: agents follow MDScript file-links and DSL imports
equally well. The difference is that MDScript composes a shared sub-script with
zero wiring (the link is the instruction) and the same links stay
**click-navigable on GitHub** for a human, while DSL imports are not links in a
code host. The headings and links are simultaneously the docs, the control flow,
and the call interface, for both agents and people.

## Install the MDScript skills

The **mdscript-exec** skill executes MDScript workflows. The **mdscript-write** skill helps you author new Agent Skills whose `SKILL.md` bodies are executable MDScript. Install the repo with the [skills CLI](https://github.com/vercel-labs/skills) to get both skills:

```bash
# List available skills in this repo
npx skills add gabewillen/mdscript --list

# Install both to Cursor (project scope)
npx skills add gabewillen/mdscript -a cursor -y

# Install both globally
npx skills add gabewillen/mdscript -a cursor -g -y
```

Use `--skill mdscript-exec` or `--skill mdscript-write` only when you want to install one skill by itself.

Invoke `mdscript-write` with what you want the new skill to do:

```
/mdscript-write deploy a branch to staging with health checks
/mdscript-write onboard a new microservice from the service template
```

<!-- installable skills under skills/ matching npx skills add discovery -->

Installable skills:

- `mdscript-exec` lives at `skills/mdscript-exec/` and executes MDScript workflows.
- `mdscript-write` lives at `skills/mdscript-write/` and authors MDScript-backed Agent Skills.

To publish your own installable skills, place them under `skills/<name>/SKILL.md` in a GitHub repo so others can run `npx skills add <owner>/<repo>`.
