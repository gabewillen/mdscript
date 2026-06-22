---
name: mdscript-write
description: >-
  Write Agent Skills whose SKILL.md body is executable MDScript. Use when the
  user invokes /mdscript-write, asks to create an mdscript skill, or wants a
  repeatable agent workflow with cross-agent heading entry points.
---

# MDScript Skill Writer

Use this skill to author MDScript workflows and MDScript-backed Agent Skills. Do
not interpret this SKILL.md as MDScript; these are normal authoring instructions
for producing files that use MDScript syntax.

## Understand The Request

Treat the user's request after `/mdscript-write` as the skill purpose. If the
purpose is missing, ask what the generated skill or workflow should accomplish.

Infer:

- `skill_name`: lowercase hyphenated name, at most 64 characters
- `skill_description`: third-person description of what the skill does and when
  to use it
- `input_variable`: the primary value the workflow reads from user input
- `workflow_states`: ordered `##` state headings needed to accomplish the
  workflow

If the name is ambiguous or collides with an existing skill, propose two or
three concrete names and ask the user to choose.

## Choose The Output Location

Use an explicit location if the user provides one. Otherwise choose based on the
workflow:

- Use `skills/<skill_name>/` for a publishable repo skill.
- Use `.cursor/skills/<skill_name>/` for a manual project-local skill.
- Use `~/.cursor/skills/<skill_name>/` for a manual personal skill.

Default to `skills/<skill_name>/` when the workflow is shareable or intended for
installation through `npx skills add`. Default to project-local only when the
workflow depends on repo-private paths, templates, or commands.

## Design The MDScript Workflow

Draft concise states using MDScript conventions:

- Use `##` headings as sequential states and stable `mdscript-exec` entry
  points.
- Use `{{variables}}` for inferred, remembered, or input-derived values.
- Use `[State Title](#state-title)` links for branches, loops, and retries.
- Use file links for external scripts or templates, such as
  `[Template](templates/service.template.md)`.
- Use natural language instructions only; do not invent formal syntax beyond
  headings, variables, and links.

Treat headings as public cross-agent communication targets. Another agent can
be told to continue the workflow with `/mdscript-exec path/to/SKILL.md#heading`.
Make headings durable, descriptive, and unique enough to be referenced from
another thread or handoff.

Include guard states where they reduce ambiguity or risk: missing input,
confirm-before-destructive-action, validation failures, retry loops, and
recovery branches.

Keep generated `SKILL.md` files under 500 lines. Move long examples or reference
material to `reference.md` in the generated skill directory and link to it from
the generated skill.

Before writing files, show the user a brief outline of proposed states and key
variables when the design is non-trivial. Apply requested changes before
writing.

## Write The Skill Files

Create the selected skill directory and write `SKILL.md` with valid YAML
frontmatter followed by an MDScript body. Generated MDScript skills should use
this shape:

```markdown
---
name: {{skill_name}}
description: {{skill_description}}
---

<!-- mdscript: use the mdscript-exec skill or read [spec.md](https://raw.githubusercontent.com/gabewillen/mdscript/main/spec.md) -->

## First State Title

* if `{{input_variable}}` is empty
  * infer `{{input_variable}}` from the input

* ...workflow instructions...
```

Use the GitHub raw `spec.md` link in the execution header for publishable skills
so the workflow still works when copied into another repo or personal skill folder.

If the workflow needs templates, examples, or helper scripts, create them under
the generated skill directory and link to them from the MDScript body.

## Validate The Output

Confirm the generated skill has:

- valid YAML frontmatter with `name` and `description`
- the MDScript execution header requiring `mdscript-exec` or reading the
  MDScript spec
- `##` states that match the approved outline
- durable heading names that can be used as `mdscript-exec` entry points
- Markdown anchor links for branches and loops
- actionable bullets that can be executed rather than narrated

Tell the user the generated skill path, normal invocation form, heading-entry
form, and any supporting files created.

## Reference

For MDScript syntax, control flow, publishing notes, and examples, read
[reference.md](reference.md) when details are needed.
