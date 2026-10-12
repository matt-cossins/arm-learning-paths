---
title: Plan routing and measurement
description: Plan how an application selects inference operations and measures loading, latency, throughput, and memory.
weight: 10

### FIXED, DO NOT MODIFY
layout: learningpathall
---

One large language model can handle many requests, but it is not always the fastest, smallest, or most predictable choice. A reusable inference layer can expose several operations while the application chooses the appropriate one.

## Route by task before model

Start with information the application already has. File type, selected feature, request metadata, or a fixed rule can often identify the task without another model call.

| Request | Suitable route | Reason |
| --- | --- | --- |
| Known arithmetic or lookup | Ordinary application code | Exact and inexpensive |
| Image categorization | Image classifier | Task-specific output and predictable schema |
| Semantic similarity | Embedding model | Produces vectors for comparison |
| Open-ended text response | Generative language model | Produces new language from a prompt |
| Ambiguous request type | Small intent classifier, then a task endpoint | Keeps routing separate from generation |

Routing is application logic. A model does not automatically discover other models or replace itself with a more suitable runtime.

Keep an explicit record of the selected route, model, runtime, and reason. This makes incorrect routing easier to distinguish from incorrect model output.

## Measure model loading

Model-loading time affects startup, scaling, and recovery. Record the time from starting a load until the service reports readiness.

Also record memory before loading, after loading, and after the first request. The first request can trigger additional allocation or runtime initialization that is not visible immediately after loading.

## Measure generation

For language generation, separate:

- Time to first token
- Prompt or prefill processing rate
- Output generation rate
- Total request time
- Prompt and output token counts

Use the same model, quantization, prompt, output limit, runtime settings, and hardware when comparing results. Warm and cold requests answer different questions, so label them separately.

## Measure task-specific inference

For classification or embedding, record:

- Preprocessing time
- Runtime execution time
- Postprocessing time
- End-to-end request time
- Peak or steady-state memory
- Input size and batch size

If an accelerator is expected, collect runtime evidence that the intended backend executed. Correct output alone does not show which processor performed the work.

## Account for concurrency

A result from one request does not describe service behavior under concurrent use. More clients can increase throughput while also increasing queue time, memory use, and individual request latency.

Define the expected number of clients before comparing service designs. Record queue time separately from inference time when the service provides both values.

## Complete the inference-layer design

Before implementation, document these choices:

- The tasks the service exposes
- The model artifact and runtime for each task
- The target Arm hardware backend and fallback behavior
- Request and response fields for each operation
- Model loading and readiness behavior
- Streaming and cancellation behavior
- Input, context, output, and concurrency limits
- Errors, logs, and measurements returned by the service
- The routing rules owned by the client application
- The access boundary for the local endpoint

The result is an inference layer that keeps application code separate from model formats and runtime details. The `llama-server` implementation provides generation. A later extension can add a small LiteRT or ExecuTorch wrapper for a task-specific model while preserving the same service boundary.

The next Learning Path in this series can consume these operations when building a bounded local agent. The agent can choose between ordinary software, classification, generation, and tools without loading each model runtime itself.

## What you've accomplished

You have separated the layers in a local inference system, compared runtime choices, defined task-based operations, and planned routing and measurements. These decisions provide the service boundary needed by the later agent and multi-agent Learning Paths.
