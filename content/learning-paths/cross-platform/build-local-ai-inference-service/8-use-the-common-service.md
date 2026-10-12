---
title: Use the common inference service
description: Use a small companion service that exposes llama.cpp, LiteRT, and ExecuTorch through task-based endpoints.
weight: 9

### FIXED, DO NOT MODIFY
layout: learningpathall
---

The `llama-server` exercises showed how a ready-made server exposes a language model. LiteRT and ExecuTorch are more commonly embedded in an application. The companion project demonstrates both approaches behind one service.

{{% notice Note %}}
The companion project is a local repository during prototyping. Add its public repository URL here before publication.
{{% /notice %}}

The project provides these endpoints:

| Endpoint | Adapter | Model artifact |
| --- | --- | --- |
| `/generate` | Existing `llama-server` process | GGUF language model |
| `/embed` | Existing `llama-server` process configured for embeddings | GGUF embedding model |
| `/classify` with `litert` | LiteRT Compiled Model API | `.tflite` classifier |
| `/classify` with `executorch` | ExecuTorch Python runtime | `.pte` classifier |
| `/route` | Deterministic task router | Selects one of the operations above |

The Learning Path focuses on `llama-server`. The LiteRT and ExecuTorch adapters are complete examples of loading a prepared model, accepting an input tensor, executing the model, and returning the highest-scoring class. They do not attempt to provide universal image, audio, or text preprocessing. Those steps depend on the selected model.

## Install the companion service

From the directory that contains the `local-inference-service` repository, create its Python environment and install the core service:

```bash
cd local-inference-service
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

Make sure the `llama-server` process from the earlier section is listening on `127.0.0.1:8080`. Then start the common service:

```bash
local-inference-service
```

The common service listens on `127.0.0.1:8000`.

## Send a generation request

In another terminal, send a request to the common `/generate` operation:

```bash
curl --fail --silent http://127.0.0.1:8000/generate \
  -H 'Content-Type: application/json' \
  -d '{
    "prompt": "Explain why an inference service needs a readiness check. /no_think",
    "max_tokens": 64,
    "temperature": 0.2
  }' | jq
```

The common service forwards the request to `llama-server` and returns generated text, the finish reason, token usage, and server timings. The client does not send a GGUF path or a `llama.cpp` command.

## Inspect the configured adapters

Request the common service health endpoint:

```bash
curl --fail --silent http://127.0.0.1:8000/health | jq
```

Without classifier model paths, the response reports generation and embedding through `llama.cpp` and an empty classification list.

## Enable a LiteRT classifier

The LiteRT adapter uses the Compiled Model API. It expects a `.tflite` classifier with one input, one output, and a default signature.

Install the optional dependency and set the model path before starting the service:

```bash
python -m pip install -e '.[litert]'
export LITERT_MODEL_PATH=/absolute/path/to/classifier.tflite
export LITERT_LABELS_PATH=/absolute/path/to/labels.txt
local-inference-service
```

The labels file is optional. It contains one class label per line in model-output order. Without it, the service returns the selected output index as the label.

## Enable an ExecuTorch classifier

The ExecuTorch adapter expects a `.pte` program whose `forward` method accepts one floating-point tensor and returns class scores.

Install a PyTorch and ExecuTorch combination compatible with the exported program. Then install the adapter and set its model path:

```bash
python -m pip install -e '.[executorch]'
export EXECUTORCH_MODEL_PATH=/absolute/path/to/classifier.pte
export EXECUTORCH_LABELS_PATH=/absolute/path/to/labels.txt
local-inference-service
```

A `.pte` file can contain backend-specific delegation. Use a program exported for the target system and a compatible ExecuTorch runtime.

## Use the common classification contract

After configuring either classifier, send its prepared input tensor to `/classify`. Select the backend in the request:

```bash
curl --fail --silent http://127.0.0.1:8000/classify \
  -H 'Content-Type: application/json' \
  -d '{
    "backend": "litert",
    "inputs": [[0.1, 0.2, 0.3, 0.4]]
  }' | jq
```

The exact tensor shape and values must match the selected model. Change `backend` to `executorch` to use the same service contract with a configured `.pte` classifier.

The response contains the backend, selected label and index, selected score, and complete score list. This common response lets a client switch classifier runtimes without changing how it reads the result.

## Route by task

The `/route` endpoint uses an explicit `task` field. It does not ask a language model to decide which runtime to call.

Send a generation task through the router:

```bash
curl --fail --silent http://127.0.0.1:8000/route \
  -H 'Content-Type: application/json' \
  -d '{
    "task": "generate",
    "prompt": "Describe a task-specific model in one sentence. /no_think",
    "max_tokens": 48
  }' | jq
```

For classification, provide `task`, `backend`, and `inputs`. For embeddings, provide `task` and `inputs`. The explicit task keeps routing predictable; a later agent can call this service after application code has decided which operation is required.

## What you've accomplished

You have placed a common task-based API in front of a ready-made language-model server and two embedded inference runtimes. The main implementation remains easy to inspect, while LiteRT and ExecuTorch can be added without exposing their model-loading code to clients.
