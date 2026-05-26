---
name: mdscript
description: >-
  Write Cursor Agent Skills whose SKILL.md body is executable MDScript. Use when
  the user invokes /mdscript, asks to create an mdscript skill, or wants a
  repeatable agent workflow encoded as MDScript states in a skill file.
disable-model-invocation: true
metadata:
  author: gabewillen
  version: "1.0.0"
  argument-hint: "<what the skill should accomplish>"
---

<!-- read [mdscript.md](https://raw.githubusercontent.com/gabewillen/mdscript/main/README.md) -->

# MDScript Skill Author

Accept `/mdscript <purpose>` or natural language after invoking this skill. Treat the remainder as `{{skill_purpose}}`.

Examples:
- `/mdscript deploy a branch to staging with health checks`
- `/mdscript onboard a new microservice from the service template`
- `mdscript skill for generating release notes from git history`

Every instruction below must be **executed**, not narrated.

## Parse Purpose

* if `{{skill_purpose}}` is empty
  * ask the user what the skill should accomplish

* infer from `{{skill_purpose}}`:
  * `{{skill_name}}` — lowercase, hyphens, max 64 chars (e.g. `deploy-staging`, `onboard-service`)
  * `{{skill_description}}` — third-person WHAT + WHEN, max 1024 chars, includes trigger terms
  * `{{input_variable}}` — primary variable the skill reads from user input (e.g. `{{branch_name}}`, `{{service_name}}`)
  * `{{workflow_states}}` — ordered list of `##` state titles that accomplish the purpose

* if `{{skill_name}}` is ambiguous or collides with an existing skill
  * propose 2–3 name options and ask the user to pick one
    * [Parse Purpose](#parse-purpose)

## Choose Location

* if the user specified personal or project scope, set `{{skill_location}}` accordingly

* if `{{skill_location}}` is unset, ask:
  * **install with skills CLI** — `npx skills add <owner>/<repo> --skill {{skill_name}} -a cursor` (project: `.agents/skills/`; add `-g` for global)
  * **manual project skill** — `.cursor/skills/{{skill_name}}/`
  * **manual personal skill** — `~/.cursor/skills/{{skill_name}}/`
  * default to **skills CLI project install** when the workflow is shareable with a team
  * default to **manual personal** when the workflow is generic and not tied to a repo

* set `{{skill_dir}}` to the chosen path

## Design Workflow

* for each state in `{{workflow_states}}`, draft bullet instructions using MDScript conventions:
  * `##` headings as sequential states (fallthrough unless redirected)
  * `{{variables}}` for values inferred, set, or read from input — no declarations
  * `[State Title](#state-title)` for branches, loops, and retries
  * file paths in backticks for `[External Script](path/to/script.md)` and `[Template](path/to/template.md)` calls
  * natural language only — no formal keywords beyond headings, variables, and links

* include guard states when useful:
  * empty-input inference from user message
  * confirm-before-destructive-action
  * retry loops linking back to the failing state
  * validation steps (run command, check file exists) with branch on failure

* keep generated SKILL.md under 500 lines; move long reference material to `reference.md` in `{{skill_dir}}`

* show the user a brief outline of states and variables; ask for changes
  * if changes requested, update the design and ask again
  * if approved, [Write Skill Files](#write-skill-files)

## Write Skill Files

* create `{{skill_dir}}` if it does not exist

* write `{{skill_dir}}/SKILL.md` with this shape:

```markdown
---
name: {{skill_name}}
description: {{skill_description}}
disable-model-invocation: true
---

<!-- read [mdscript.md](https://raw.githubusercontent.com/gabewillen/mdscript/main/README.md) -->

## First State Title

* if `{{input_variable}}` is empty
  * infer `{{input_variable}}` from the input

* …workflow instructions…
```

* use the **GitHub raw mdscript link** in the version header so the skill works when copied to personal skills or other repos

* set `disable-model-invocation: true` unless the user explicitly wants ambient auto-discovery

* if the workflow needs templates, examples, or scripts, create them under `{{skill_dir}}/` and link from the MDScript body

* if the user wants a publishable skill repo, place shareable skills under `skills/{{skill_name}}/` so others can run `npx skills add <owner>/<repo> --skill {{skill_name}}`

* [Verify Skill](#verify-skill)

## Verify Skill

* confirm `{{skill_dir}}/SKILL.md` has valid YAML frontmatter (`name`, `description`)

* confirm the MDScript body:
  * starts with the version header comment
  * uses `##` states that match the approved outline
  * branches and loops use markdown anchor links, not prose-only jumps
  * every bullet is actionable and executable

* confirm the description is third person and names when to invoke the skill (include `/{{skill_name}}` if appropriate)

* tell the user:
  * skill path: `{{skill_dir}}/SKILL.md`
  * invoke with: `/{{skill_name}} <input>`
  * optional supporting files created
  * to publish: push to GitHub, then `npx skills add <owner>/<repo> --skill {{skill_name}} -a cursor`

* if the user wants edits, [Design Workflow](#design-workflow)

## Reference

For MDScript syntax, control flow, and authoring patterns, see [reference.md](reference.md).

For examples in this repo, see `examples/` at the repository root.
