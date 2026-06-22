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

## Benchmark Results

The latest probabilistic scripting benchmark compared MDScript with Guidance, LMQL, and ell using OpenAI `gpt-5.5` for three blinded execution attempts per workflow and three independent judgments per execution across three workflow cases. It scores produced task outcomes: task success, requirements met, and failure recovery. See `benchmarks/llm-scripting/` for methodology, raw results, and analysis.

<!-- latest LLM scripting benchmark summary from benchmarks/llm-scripting/results/latest.json -->

| Rank | System | Overall | Task Success | Requirements Met | Failure Recovery | Std Dev | Judgments |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | MDScript | 9.73 | 9.89 | 9.67 | 9.33 | 0.35 | 27 |
| 2 | Guidance | 9.67 | 9.81 | 9.59 | 9.37 | 0.36 | 27 |
| 3 | ell | 9.65 | 9.78 | 9.63 | 9.30 | 0.37 | 27 |
| 4 | LMQL | 9.65 | 9.81 | 9.56 | 9.30 | 0.39 | 27 |

## Install the MDScript skills

The **mdscript-exec** skill executes MDScript workflows. The **mdscript-write** skill helps you author new Agent Skills whose `SKILL.md` bodies are executable MDScript. Install them with the [skills CLI](https://github.com/vercel-labs/skills):

```bash
# List available skills in this repo
npx skills add gabewillen/mdscript --list

# Install to Cursor (project scope)
npx skills add gabewillen/mdscript --skill mdscript-exec -a cursor -y
npx skills add gabewillen/mdscript --skill mdscript-write -a cursor -y

# Install globally
npx skills add gabewillen/mdscript --skill mdscript-exec -a cursor -g -y
npx skills add gabewillen/mdscript --skill mdscript-write -a cursor -g -y
```

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
