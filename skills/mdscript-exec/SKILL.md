---
name: mdscript-exec
description: >-
  Execute MDScript Markdown workflows. Use when the user invokes /mdscript-exec,
  asks to run an MDScript file, asks to start from a specific heading, or a file
  header requires the mdscript-exec skill.
disable-model-invocation: true
metadata:
  author: gabewillen
  version: "1.0.0"
  argument-hint: "<path[#heading] or workflow request>"
---

<!-- mdscript: use the mdscript-exec skill or read [mdscript.md](https://raw.githubusercontent.com/gabewillen/mdscript/main/README.md) -->

# MDScript Executor

Execute the referenced MDScript workflow. Every instruction below must be **executed**, not narrated.

## Load Workflow

* if `{{workflow_path}}` is empty
  * infer `{{workflow_path}}` from the input
  * infer `{{start_heading}}` from the input when the user specifies a heading or a `#heading` anchor

* if `{{workflow_path}}` is still empty
  * ask the user for the MDScript file path
  * [Load Workflow](#load-workflow)

* read `{{workflow_path}}`

* if the file is missing
  * report that `{{workflow_path}}` was not found
  * ask the user for a different path
  * [Load Workflow](#load-workflow)

* if the top comment says to read an MDScript README and that README has not been read in this session
  * read the referenced README before executing the workflow

* if `{{workflow_path}}` includes a `#heading` fragment
  * move the fragment into `{{start_heading}}`
  * remove the fragment from `{{workflow_path}}`
  * read `{{workflow_path}}` again without the fragment if needed

## Parse Workflow

* ignore YAML frontmatter, the execution header comment, and prose before the first `##` state

* identify each `##` heading as a state

* identify each state's Markdown anchor slug from its heading text

* identify each bullet under a state as an instruction to execute

* keep a table of `{{variables}}` encountered while executing the workflow

* if `{{start_heading}}` is set
  * find the state whose heading exactly matches `{{start_heading}}` or whose anchor slug matches `{{start_heading}}`
  * if no state matches, report the available headings and ask the user for a valid heading
    * [Parse Workflow](#parse-workflow)
  * begin at the matching state

* if `{{start_heading}}` is empty
  * begin at the first state

## Execute State

* execute each instruction in the current state in order using available tools

* when an instruction says to infer, ask, read, create, edit, run, verify, notify, or report something, perform that action directly

* when an instruction sets a `{{variable}}`, remember the value for later states

* when an instruction contains a Markdown link to another state, follow that link if the condition for that instruction applies

* when an instruction contains a Markdown link to another file, read or execute that file according to the instruction text

* if a required value is missing and cannot be inferred safely
  * ask the user for the missing value
  * [Execute State](#execute-state)

* if a command or validation step fails and the workflow specifies a linked recovery state
  * follow the recovery link

* if a command or validation step fails and the workflow does not specify recovery
  * stop and report the failure with the command, relevant output, and current state

## Advance

* if execution followed a state link
  * set the current state to the linked state
  * [Execute State](#execute-state)

* if there is another state after the current state
  * set the current state to the next state
  * [Execute State](#execute-state)

* if there are no more states
  * report the completed workflow, files changed, commands run, and any validation results
