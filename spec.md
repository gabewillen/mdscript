# MDScript Execution Specification

This is the execution spec for MDScript: how an LLM or agent runs an MDScript
file. For what MDScript is, the design philosophy, benchmarks, and installation,
see [README.md](README.md).

MDScript is a minimal scripting format for guiding LLMs in coding assistants
like Cursor and Claude Code. It uses plain Markdown with just enough structure
to create reliable, repeatable workflows.

## Execution Header

Every MDScript file should include an execution comment near the top requiring
the executor skill first, with this specification as the fallback:

```markdown
<!-- mdscript: use the mdscript-exec skill or read [spec.md](https://raw.githubusercontent.com/gabewillen/mdscript/main/spec.md) -->
```

The path should be a relative path to this spec or a link to the raw file on
`github.com/gabewillen/mdscript`. This tells the LLM to use the installed
`mdscript-exec` skill when available, or to read this execution specification
directly when the skill is unavailable.

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

A Markdown link to another file means: read and execute that linked file. This
makes workflows composable (small, reusable scripts linked from larger ones),
and the same links remain click-navigable for a human browsing the repository.

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

Everything except headings, variables, and links is written in natural language.
The LLM interprets instructions using its language understanding:

```markdown
* if `{{product_path}}` doesn't exist
  * create `{{product_path}}` directory

* infer `{{use_cases}}` list from the input

* ask the user if they want to continue
```

No keywords, no operators, no formal syntax - just clear instructions.

## Execution

Every instruction in an MDScript file must be **executed**, not narrated. The LLM
should perform the action using its available capabilities rather than describing
what it would do. If an LLM cannot or does not carry out an instruction, it has
failed to follow the script.

Execution starts at the first `##` state unless the user asks to start from a
specific heading. A heading entry point can be provided by name or as a Markdown
anchor, such as `examples/deploy-branch.md#run-checks`.

Heading entry points make MDScript useful for cross-agent handoffs: one agent can
tell another to execute the same workflow from a precise state instead of
replaying the whole script.

For complete worked examples, see the `examples/` directory.
