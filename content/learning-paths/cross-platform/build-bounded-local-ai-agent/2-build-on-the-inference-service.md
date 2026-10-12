---
title: Build on the inference service
description: Place agent decisions, tools, policy, and traces above the model-serving layer from the first Learning Path.
weight: 3

### FIXED, DO NOT MODIFY
layout: learningpathall
---

The second Learning Path reuses Path 1 instead of loading model artifacts inside the agent.

## Separate the two layers

| Path 1: inference layer | Path 2: agent layer |
| --- | --- |
| Loads GGUF, `.tflite`, or `.pte` artifacts | Receives a user goal |
| Runs `llama.cpp`, LiteRT, or ExecuTorch | Routes the goal to software, a model, or the agent loop |
| Exposes `/generate`, `/classify`, and `/embed` | Describes registered tools to the model |
| Returns model output and timings | Validates and executes proposed tool calls |
| Owns model and runtime configuration | Owns permissions, budgets, timeouts, stopping, and traces |

The agent calls `http://127.0.0.1:8000/generate`. It does not need the GGUF path, `llama-server` command, quantization, or runtime-specific response format.

## Follow one agent step

The bounded loop repeats five application-owned stages:

1. **Observe**: collect the user goal and previous tool results.
2. **Decide**: ask the language model for either a final answer or one structured tool call.
3. **Act**: validate the tool name and arguments, then run ordinary Python.
4. **Verify**: record success, rejection, timeout, or validation failure.
5. **Stop or continue**: return the answer or begin another step within the remaining budget.

The inference service participates only in **Decide**. This means the application can change its tool policy without rebuilding the model server, and the inference runtime can change without rewriting the agent loop.

## Route ambiguous requests

The prototype begins with deterministic routing rules:

- Recognized arithmetic goes directly to a safe Python calculator.
- Requests that name system or file operations enter the agent loop.
- Other language requests use one direct generation call.

Path 1 also exposes `/classify`. A later router can send ambiguous requests to a small intent classifier and map its labels to `software`, `model`, or `agent`. The larger language model still handles reasoning and generation. Keeping this optional means the first agent run does not depend on a second model artifact.

## Keep the agent local and bounded

The prototype provides four tools:

- `calculator`
- `system_info`
- `read_text_file`
- `write_text_file`

The file tools can access only a configured workspace directory. There is no shell tool, package installer, network tool, or unrestricted filesystem access.

## What you've learned

Path 1 supplies model results; Path 2 supplies control and authority. With that boundary established, you can install the harness and compare its three request routes.
