---
title: Compare and validate the agent
description: Compare software, direct-model, and agent execution and verify the harness tests and stopping behavior.
weight: 9

### FIXED, DO NOT MODIFY
layout: learningpathall
---

The goal is not to send every request through the agent. Compare the three routes before deciding where the extra control loop is justified.

| Property | Software route | Direct model route | Agent route |
| --- | --- | --- | --- |
| Model calls | None | One | One or more |
| Tool calls | One known Python function | None | Selected after model decisions |
| Output predictability | High for supported inputs | Depends on model | Depends on model and observations |
| Main failure modes | Validation or software error | Invalid or poor model output | Model, validation, tool, budget, and policy errors |
| Trace needed | Usually small | Request and response | Step-by-step decisions and actions |

Use deterministic software for recognized calculations and known workflows. Use a direct model call when the application needs only generated language. Use the agent when the next registered operation depends on an earlier observation.

## Run the complete test suite

Run all model-free tests:

```bash
pytest -q
```

The expected result is:

```output
9 passed
```

The tests verify routing, safe calculation, mutation controls, path containment, tool observations, and repeated-action stopping. They do not test model quality or whether a particular model selects the best tool.

## Check the boundaries

Before adding another tool, answer these questions:

- Can deterministic application code complete the request instead?
- What exact input schema does the tool accept?
- What resources can it access?
- Does it read state or change state?
- What confirmation is needed?
- What timeout and call budget are appropriate?
- What must be recorded or redacted in the trace?
- How will the application detect that the tool made progress?

The model can help choose among registered operations, but it should not expand its own authority.

## Prepare for the multi-agent path

This harness becomes the baseline for the third Learning Path. A specialist agent will be one configured instance of the same components:

- Role and instructions
- Context and observations
- Registered tools
- Model configuration
- State and execution budget

The multi-agent system can then add a deterministic coordinator, per-agent limits, structured task messages, and global stopping conditions. The single-agent trace and test cases provide the baseline needed to decide whether that extra coordination improves the result.

## What you've accomplished

You have built one transparent local agent without an agent framework. It reuses the Path 1 inference layer, selects only registered tools, validates every proposed call, limits execution, controls mutations, reports progress, and records a trace.
