---
title: Define task-based API contracts
description: Define consistent generation, classification, and embedding operations without forcing every model into a chat interface.
weight: 5

### FIXED, DO NOT MODIFY
layout: learningpathall
---

An API contract describes what a client sends, what the service returns, and how failures are reported. A stable contract lets an application change runtimes or model versions without rewriting its inference calls.

## Use operations that match the task

Three operations cover many local AI applications:

| Operation | Typical input | Typical result |
| --- | --- | --- |
| `generate` | Prompt or messages, generation settings, and optional model identifier | Generated text, finish reason, token usage, and timing |
| `classify` | Text, image, audio, or prepared tensor plus task options | Labels, scores, and model version |
| `embed` | Text or another supported input | Numerical vector, dimensions, and model version |

These operations can share conventions for model selection, request identifiers, errors, and timing without sharing the same input fields.

## Define generation behavior

Generation can return one complete response or stream partial output.

A synchronous response is easier for clients that need the complete result before continuing. Streaming reduces the time before a user sees output and lets an application report progress during a longer response.

The contract should state:

- Whether input is plain text, chat messages, or both
- Which generation settings clients may control
- How maximum output and stop conditions work
- Whether token counts and timing are returned
- How cancellation and client disconnects are handled
- Whether the service supports concurrent requests

An OpenAI-compatible endpoint can make some existing clients easier to reuse. Compatibility does not imply that every API feature is present or that different models have the same capabilities. Document the supported subset.

## Define classification behavior

Classification needs a clear relationship between the input, preprocessing, and returned labels.

The contract should state:

- Accepted input types and size limits
- Whether the service or client performs preprocessing
- The label set and its version
- Whether scores are probabilities, logits, or another value
- How many results are returned
- How invalid or unsupported inputs are reported

Returning a label without its score or model version can make later comparison and diagnosis difficult.

## Define embedding behavior

Embedding clients need to know the vector size, numerical type, model version, and any input truncation. Vectors from different embedding models or versions are not automatically comparable.

If an application stores embeddings, store the model identity and relevant preprocessing details with them. Changing the embedding model can require regenerating the stored vectors.

## Add service-level operations

Task endpoints are only part of the interface. The service also needs a small set of operational signals:

- *Liveness*: the process is running.
- *Readiness*: the required model is loaded and can accept a request.
- *Model information*: the service reports the loaded model, task, version, and important limits.
- *Structured errors*: clients can distinguish invalid input, unavailable models, capacity limits, timeouts, and internal failures.

These signals prevent client applications from treating every failure as a model-generated answer or an unknown network error.

## What you've accomplished

You have defined task-based operations and the service information needed by clients. Next, you will decide how an application selects an operation and how to measure whether the inference layer meets its requirements.
