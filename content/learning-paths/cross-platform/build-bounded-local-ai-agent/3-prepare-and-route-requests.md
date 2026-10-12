---
title: Prepare the harness and route requests
description: Install the bounded-agent project and compare software, direct-model, and agent routes.
weight: 4

### FIXED, DO NOT MODIFY
layout: learningpathall
---

{{% notice Note %}}
The `bounded-local-agent` companion project is a local repository during prototyping. Add its public repository URL here before publication.
{{% /notice %}}

## Check the inference dependency

Confirm that the common inference service from Path 1 is ready:

```bash
curl --fail --silent http://127.0.0.1:8000/health | jq
```

The response should report `status` as `ok` and generation through `llama.cpp`.

## Install the agent project

From the directory containing the companion repository, create a virtual environment and install the project:

```bash
cd bounded-local-agent
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[test]'
```

## Use deterministic software

Send an arithmetic request:

```bash
bounded-agent "calculate 18 * 7"
```

The expected output is:

```output
route: software (recognized arithmetic expression)
126
```

The router recognizes the arithmetic grammar and uses the Python calculator. No model request is made.

## Use the model directly

Send a request that needs language generation but no tool:

```bash
bounded-agent "Explain the difference between RAM and storage in two sentences."
```

The first output line identifies the route:

```output
route: model (no tool use is required)
```

The remaining output comes from Path 1's `/generate` endpoint and will vary by model and sampling settings.

## Enter the agent loop

Prefix a request with `agent:` to select the bounded loop explicitly:

```bash
bounded-agent "agent: report the local system architecture and CPU count"
```

The output is similar to:

```output
route: agent (agent route requested)
step 1: deciding
step 1: running system_info
step 2: deciding
```

The model proposes `system_info`, Python runs it, and the result returns to the model as an observation. The final line reports the JSONL trace path.

## What you've accomplished

You have compared an exact software call, one direct model call, and a multi-step agent request. Next, you will inspect how the harness turns model text into a validated tool call.
