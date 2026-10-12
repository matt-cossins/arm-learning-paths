---
title: Bound tools and mutations
description: Apply step limits, tool budgets, timeouts, repeated-call detection, dry runs, and mutation approval.
weight: 7

### FIXED, DO NOT MODIFY
layout: learningpathall
---

The harness starts with these limits:

| Limit | Default | Effect |
| --- | --- | --- |
| Model-decision steps | 4 | Stops a long decide-and-act sequence |
| Tool calls | 2 | Caps external actions even if steps remain |
| Tool timeout | 5 seconds | Stops waiting for a slow tool |
| Repeated identical call | Not allowed | Stops a loop that does not make progress |
| Mutation approval | Off | Prevents file writes by default |

Change the numeric bounds with `--max-steps`, `--tool-budget`, and `--tool-timeout`. These values are enforced by Python and are not sent as requests for the model to follow.

## Preview a file write

Use dry-run mode for a mutating request:

```bash
bounded-agent --dry-run \
  "agent: write a file named summary.txt containing a short note about local inference"
```

If the model proposes `write_text_file`, the tool returns `dry_run` with the validated path and content. It does not create the file.

Confirm that the file is absent:

```bash
test ! -e workspace/summary.txt && echo "No file was written"
```

The expected output is:

```output
No file was written
```

## Approve the bounded mutation

Authorize writes inside the configured workspace:

```bash
bounded-agent --approve-mutations \
  "agent: write a file named summary.txt containing a short note about local inference"
```

Check the file:

```bash
cat workspace/summary.txt
```

The generated content varies. The path remains restricted to `workspace/`.

Approval applies only to registered mutating tools for this run. It does not allow shell commands or paths outside the workspace.

## Test the policy directly

Run all tool-policy tests:

```bash
pytest -q tests/test_tools.py
```

The expected result is:

```output
4 passed
```

The tests cover safe arithmetic, confirmation, dry-run behavior, and path containment.

## What you've accomplished

You have made limits and mutation authority explicit application settings. Next, you will inspect the trace that records how a run used that authority.
