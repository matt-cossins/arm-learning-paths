---
title: Follow the bounded agent loop
description: Follow observations, model decisions, tool results, verification, and stopping through one agent run.
weight: 6

### FIXED, DO NOT MODIFY
layout: learningpathall
---

The `BoundedAgent` class keeps observations and limits in application memory. It sends only the goal, tool schemas, and completed observations to the model.

## Observe

At the start of a run, the harness records the user goal. After each tool call, it appends a structured result such as:

```json
{
  "status": "ok",
  "tool": "system_info",
  "output": {
    "operating_system": "Linux",
    "machine": "aarch64",
    "cpu_count": 8
  }
}
```

The exact operating system and CPU count depend on the machine.

## Decide

The model receives the current goal, registered tool schemas, and observations. It returns one `ModelDecision`: answer or tool.

If the response is not valid JSON or does not match the decision schema, the harness records an `invalid_decision` observation. The next step can try again if the step budget remains.

## Act and verify

For a tool decision, Python checks:

1. The tool is registered.
2. Its arguments match the Pydantic model.
3. The same call has not already occurred.
4. The tool budget remains.
5. Mutation policy permits the action.
6. The call finishes before its timeout.

The result becomes the next observation whether it succeeds, fails validation, needs confirmation, or is a dry run.

## Stop or continue

The loop stops when:

- The model returns a final answer.
- The step limit is reached.
- The tool budget is reached.
- An identical tool call repeats.
- A tool exceeds its timeout.

The application checks stopping conditions. The prompt does not ask the model to enforce its own budget.

## Test the sequence without a model

Run the agent-loop tests:

```bash
pytest -q tests/test_agent.py
```

The expected result is:

```output
2 passed
```

The tests use a fake decision client. One test returns a tool call followed by an answer; the other repeats the same tool call and confirms that Python stops the run.

## What you've accomplished

You have traced control through observe, decide, act, verify, and stop. Next, you will exercise the mutation policy and change the execution budgets.
