# MDScript Reference for Skill Authors

## Skill file anatomy

```markdown
---
name: my-workflow
description: Third-person WHAT and WHEN. Include trigger terms and /my-workflow.
disable-model-invocation: true
---

<!-- mdscript: use the mdscript-exec skill or read [mdscript.md](https://raw.githubusercontent.com/gabewillen/mdscript/main/README.md) -->

## Setup

* if `{{target}}` is empty
  * infer `{{target}}` from the input

## Execute

* perform the work using available tools

* if validation fails
  * [Execute](#execute)
```

## Core elements

| Element | Syntax | Role |
|---------|--------|------|
| State | `## Title` | One workflow step, fallthrough target, and `mdscript-exec` entry point |
| Variable | `{{name}}` | Created on first mention; no declarations |
| Branch/loop | `[Title](#title)` | Redirect flow to another state |
| External call | `[Label](path/to/file.md)` | Run or read another MDScript or template |
| Execution header | `<!-- mdscript: use the mdscript-exec skill or read [mdscript.md](url) -->` | Points agent at the executor skill or execution spec |

## Control flow patterns

**Cross-agent entry point**

```markdown
Tell another agent to continue this workflow at a specific heading:

`/mdscript-exec .agents/skills/deploy-staging/SKILL.md#verify-deployment`
```

**Infer from input**

```markdown
* if `{{service_name}}` is empty
  * infer `{{service_name}}` from the input
```

**Set derived values**

```markdown
* set `{{service_path}}` to `services/{{service_name}}`
```

**Branch**

```markdown
* if `{{service_path}}` already exists
  * ask the user for a different name
    * [Setup Name](#setup-name)
```

**Retry loop**

```markdown
* run `npm test`
  * if tests fail, fix issues and [Verify](#verify)
```

**External script**

```markdown
* create the service using [Create Service](examples/create-service.md)
```

## Cursor skill metadata

| Field | Rules |
|-------|-------|
| `name` | Lowercase, hyphens, ≤64 chars; matches `/name` invocation |
| `description` | Third person; WHAT + WHEN; ≤1024 chars; discovery keywords |
| `disable-model-invocation` | `true` for explicit `/skill` commands (default for MDScript skills) |

## Publishing with the skills CLI

Place installable skills at `skills/<name>/SKILL.md` in a GitHub repo, then:

```bash
npx skills add owner/repo --skill <name> -a cursor
npx skills add owner/repo --skill <name> -a cursor -g -y   # global, non-interactive
```

## Anti-patterns

- Narrating instead of executing ("I would create…" — do it)
- Prose-only branching without anchor links
- Declaring variables in a separate block
- SKILL.md bodies over 500 lines without a `reference.md` split
- Vague descriptions ("helps with workflows")
- First-person descriptions ("I can help you…")

## Repo examples

| File | Pattern |
|------|---------|
| `examples/generate-product.md` | Multi-state setup with external calls |
| `examples/runbook-incident.md` | Branching severity and escalation |
| `examples/refactor-function.md` | Complexity gate and retry on test failure |
| `examples/create-service.md` | Scaffold from template |
| `examples/deploy-branch.md` | Deployment verification loop |
