---
title: Inspect the execution trace
description: Read the JSONL events that record the agent goal, decisions, tool results, verification, and stopping reason.
weight: 8

### FIXED, DO NOT MODIFY
layout: learningpathall
---

Progress messages help a person follow a live run. The JSONL trace provides a machine-readable record for debugging and comparison.

Each line contains one event with a UTC timestamp. Event types include:

- `observe`: the initial goal
- `decide`: the parsed model decision
- `act`: the validated tool result
- `verify`: the result status or decision error
- `stop`: the stopping reason

## Choose an explicit trace path

Run an agent request and store its trace at a known location:

```bash
bounded-agent \
  --trace runs/system-info.jsonl \
  "agent: report the local system architecture and CPU count"
```

Print the event type and step from each record:

```bash
jq -c '{event, step, reason, status}' runs/system-info.jsonl
```

The output is similar to:

```output
{"event":"observe","step":null,"reason":null,"status":null}
{"event":"decide","step":1,"reason":null,"status":null}
{"event":"act","step":1,"reason":null,"status":null}
{"event":"verify","step":1,"reason":null,"status":"ok"}
{"event":"decide","step":2,"reason":null,"status":null}
{"event":"stop","step":2,"reason":"answer","status":null}
```

The number of steps can differ because model decisions are not deterministic.

## Diagnose a stopped run

Inspect the final event:

```bash
tail -n 1 runs/system-info.jsonl | jq
```

The `reason` distinguishes a normal answer from a step limit, tool budget, or repeated action. Tool results also show whether an action ran, failed, required confirmation, or was only previewed.

Do not treat a trace as automatically safe to publish. It can contain user requests, generated content, file contents, paths, and tool results. Apply retention and redaction rules appropriate to the application.

## What you've accomplished

You have connected live progress to a structured execution record. Next, you will compare all three routes and identify what should remain outside the agent loop.
