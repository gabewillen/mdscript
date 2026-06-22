---
name: mdscript-exec
description: >-
  Execute MDScript Markdown workflows. Use when the user invokes
  /mdscript-exec, asks to run an MDScript file, asks to start from a specific
  heading, or a file header requires the mdscript-exec skill.
---

# MDScript Executor

Use this skill as the bootstrap executor for MDScript. Do not interpret this
SKILL.md as MDScript; these are normal skill instructions for executing other
Markdown workflow files that use MDScript syntax.

## Inputs

Accept any of these forms:

- `/mdscript-exec path/to/workflow.md`
- `/mdscript-exec path/to/workflow.md#heading-anchor`
- natural language that names a workflow file and, optionally, a heading to
  start from

If the workflow path is missing or ambiguous, ask for the path. If a heading is
provided, store it as the requested start state.

## Load The Workflow

Read the workflow file. If the path contains a `#fragment`, strip the fragment
from the file path and use the fragment as the requested heading or anchor.

If the workflow header says to use `mdscript-exec` or read the MDScript spec,
and the MDScript rules are not already clear in this session, read the linked
spec (`spec.md`) before executing the workflow.

## Parse States

Ignore YAML frontmatter, the execution header comment, and prose before the
first `##` heading.

Treat each `##` heading as a state. The state body continues until the next
`##` heading or end of file. Treat bullets under a state as executable
instructions.

Compute a Markdown anchor slug for each state heading using the normal
lowercase, hyphenated heading text convention. If the user requested a start
heading, match it against either the literal heading text or the anchor slug. If
there is no match, list the available headings and ask for a valid starting
heading instead of silently starting at the top.

When no start heading is requested, begin at the first state.

## Execute States

Execute each instruction in the current state in order. Maintain state for
MDScript variables such as `{{service_name}}` across the workflow.

Perform actions directly with available tools. Do not narrate that an action
would be performed. If an instruction says to infer, ask, read, create, edit,
run, verify, notify, or report something, do that action.

Follow Markdown links to state anchors when the surrounding condition applies.
Use those links for branches, retries, and loops. Follow Markdown links to other
files by reading or executing the linked file according to the instruction text.

If a required value is missing and cannot be inferred safely, ask the user for
that value and continue from the current state.

If a command or validation step fails and the workflow gives a linked recovery
state, follow that recovery link. If no recovery is specified, stop and report
the failed command or validation, the relevant output, and the current state.

When the current state completes without a branch, continue to the next state in
file order. Stop when there are no more states.

## Report Completion

At the end, summarize the workflow completed, files changed, commands run, and
validation results. Mention any skipped optional branches or unresolved
follow-ups.
