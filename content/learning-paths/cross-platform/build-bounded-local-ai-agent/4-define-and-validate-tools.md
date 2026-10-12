---
title: Define and validate tools
description: Describe tools with JSON schemas and validate model-proposed names and arguments before execution.
weight: 5

### FIXED, DO NOT MODIFY
layout: learningpathall
---

A tool is an ordinary Python operation with four pieces of metadata:

- A unique name
- A description of when to use it
- A Pydantic model for its arguments
- A flag that identifies whether it changes state

The harness converts each Pydantic model into JSON Schema and includes those schemas in the decision prompt.

## Inspect a tool schema

Display the registered schema for `write_text_file`:

```bash
python - <<'PY'
import json
from pathlib import Path

from bounded_agent.tools import ToolRegistry

registry = ToolRegistry.default(Path("workspace"))
schema = next(item for item in registry.schemas() if item["name"] == "write_text_file")
print(json.dumps(schema, indent=2))
PY
```

The output identifies `path` and `content` as strings and marks the tool as mutating. The model sees the same description.

## Treat the model response as untrusted input

The decision client accepts only two JSON shapes:

```json
{"action": "answer", "answer": "final answer for the user"}
```

```json
{
  "action": "tool",
  "tool": {
    "name": "system_info",
    "arguments": {}
  }
}
```

Pydantic rejects missing action fields and invalid types. The registry separately checks that the tool name exists and that its arguments match the tool schema.

Validation is still required when the model receives a schema in its prompt. Prompt instructions influence model output; they do not enforce Python types or permissions.

## Restrict file paths

The file tools accept only paths relative to the agent workspace. The harness resolves the requested path and rejects it if the result leaves that directory.

Run the path-containment test:

```bash
pytest -q tests/test_tools.py -k path
```

The expected result is:

```output
1 passed
```

The model cannot use `../` or an absolute path to turn a workspace tool into unrestricted file access.

## What you've accomplished

You have separated a model's tool proposal from application validation and execution. Next, you will follow those pieces through the complete agent loop.
