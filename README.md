# MDScript

<!--
<mdscript>
  <required-executor>mdscript-exec</required-executor>
  <fallback>read this README</fallback>
</mdscript>
-->

## What is MDScript?

MDScript is a minimal scripting format for guiding LLMs in coding assistants like Cursor and Claude Code. It uses plain Markdown with just enough structure to create reliable, repeatable workflows.

## Execution Header

Every MDScript file must include an execution comment near the top requiring the executor skill first, with this specification as the fallback:

```markdown
<!-- mdscript: use the mdscript-exec skill or read [mdscript.md](https://raw.githubusercontent.com/gabewillen/mdscript/main/README.md) -->
```

The path should be a relative path to this README or a link to the raw file on `github.com/gabewillen/mdscript`. This tells the LLM to use the installed `mdscript-exec` skill when available, or to read this execution specification directly when the skill is unavailable.

## Core Elements

### 1. States (Headings)

Each `##` heading defines a step in the workflow:

```markdown
## Setup Product Name
## Create Feature File
```

States execute sequentially (fallthrough) unless explicitly redirected.

### 2. Variables

Variables use double curly braces:

```markdown
{{product_name}}
{{feature_path}}
{{use_cases}}
```

No declarations needed - variables are created when first mentioned.

### 3. Links

Markdown links navigate between states:

```markdown
[Setup Feature Name](#setup-feature-name)
```

Links enable loops, branches, and early exits.

### 4. External Calls

Reference other scripts or templates:

```markdown
[Generate Product](.cursor/commands/generate-product.md)
[Feature Template](.cursor/templates/feature.template.md)
```

## Control Flow

**Fallthrough**: States execute top-to-bottom unless a link redirects flow.

**Branching**: Use links for conditional navigation.

**Loops**: Link back to the current or previous state.

**Example**:

```markdown
## Setup Feature Name

* if `{{feature_name}}` is empty
  * infer `{{feature_name}}` from the input

* if `{{feature_path}}` already exists
  * ask the user to provide a different feature name
    * [Setup Feature Name](#setup-feature-name)

## Create Feature File
* create the feature file
```

## Natural Language

Everything except headings, variables, and links is written in natural language. The LLM interprets instructions using its language understanding:

```markdown
* if `{{product_path}}` doesn't exist
  * create `{{product_path}}` directory
  
* infer `{{use_cases}}` list from the input

* ask the user if they want to continue
```

No keywords, no operators, no formal syntax - just clear instructions.

## Execution

Every instruction in an MDScript file must be **executed**, not narrated. The LLM should perform the action using its available capabilities rather than describing what it would do. If an LLM cannot or does not carry out an instruction, it has failed to follow the script.

Execution starts at the first `##` state unless the user asks to start from a specific heading. A heading entry point can be provided by name or as a Markdown anchor, such as `examples/deploy-branch.md#run-checks`.

Heading entry points make MDScript useful for cross-agent handoffs: one agent can tell another to execute the same workflow from a precise state instead of replaying the whole script.

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

Developers can read and edit these workflows as normal Markdown. AI assistants execute them to maintain consistency across the codebase.

## Example

```markdown
## Generate Feature

* if `{{product_name}}` is empty
  * infer `{{product_name}}` from the input

* set `{{product_path}}` to `.cursor/products/{{product_name}}`

## Setup Product Path

* if `{{product_path}}` doesn't exist
  * get `{{product_path}}` from [Generate Product](.cursor/commands/generate-product.md)
  * [Setup Feature Name](#setup-feature-name)

* ask the user if they want to add the feature to `{{product_path}}`
  * if yes [Setup Feature Name](#setup-feature-name)
  * if no, ask the user to provide the product name
    * [Setup Product Path](#setup-product-path)

## Setup Feature Name

* if `{{feature_name}}` is empty
  * infer `{{feature_name}}` from the input

* set `{{feature_path}}` to `{{product_path}}/features/{{feature_name}}`

* if `{{feature_path}}` already exists
  * ask the user to provide a different feature name
    * [Setup Feature Name](#setup-feature-name)

* create `{{feature_path}}` directory

## Create Feature File

* create `{{feature_name}}.feature.md` in `{{feature_path}}` 
  adhering to [Feature Template](.cursor/templates/feature.template.md)
```

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

> An earlier `benchmarks/llm-scripting/` run reported a 9.65–9.73 ranking. On
> re-running it those differences proved to be inside the noise floor (all four
> systems within ~0.1 of each other, sub-1-standard-error gaps, rank order not
> reproducible). It is kept for history; the results below supersede it.

**Outcome correctness — deterministic checklist (primary), blind judge (secondary).**
16 branch-forcing scenarios across three cases, two repeats each.

| System | Checklist % | sd | Blind judge (1–10) |
| --- | ---: | ---: | ---: |
| MDScript | 100 | 0 | 9.00 |
| LMQL (idiomatic) | 100 | 0 | 8.66 |
| ell (idiomatic) | 96.1 | 15.9 | 8.06 |
| Guidance (idiomatic) | 95.8 | 18.2 | 8.28 |

MDScript reaches the ceiling on the deterministic metric with nothing but the
README spec, and leads the blind judge — a format you can fully learn in 90
seconds drove correct branch/loop/recovery behavior as reliably as the
code-hosted DSLs.

**Agent-to-agent delegation — the jump-point advantage (`benchmarks/robust/relay/`).**
Every `##` heading is a stable entry point, so one agent can dispatch another to
`workflow.md#heading` and resume a shared workflow mid-flow. A multi-hop relay
(haiku workers dispatched to enter at each state with injected variables) shows:

| System | Lines to become dispatchable | Handoff correctness | Readability with that plumbing |
| --- | ---: | ---: | ---: |
| MDScript | **+0** | 86% | **9.00** |
| Guidance | +34 | 88% | 6.43 |
| ell | +35 | 88% | 7.29 |
| LMQL | +42 | 86% | 6.43 |

Handoff correctness is a tie (zero jump failures across all formats) — MDScript
does not *execute* a relay better. The difference is cost: MDScript is
dispatchable-at-a-state for free because headings are already addressable, while
the DSLs need ~34–42 lines of dispatch plumbing (roughly doubling the file),
which also drops their readability by 1–1.5 points in a blind panel. The
headings are simultaneously the docs, the control flow, and the inter-agent call
interface.

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
