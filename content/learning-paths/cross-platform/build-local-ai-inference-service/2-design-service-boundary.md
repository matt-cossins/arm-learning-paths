---
title: Design the service boundary
description: Decide when to embed a runtime and when to expose inference through a separate local service.
weight: 3

### FIXED, DO NOT MODIFY
layout: learningpathall
---

An application can call an inference runtime directly or send a request to a separate service. Both designs can run entirely on local Arm hardware.

## Compare embedded and service-based inference

| Design | Advantages | Costs |
| --- | --- | --- |
| Embed the runtime | No network boundary; direct access to runtime features; simple packaging for one application | Each application manages model loading, memory, dependencies, and runtime updates |
| Use a local service | One loaded model can serve several clients; clients use a stable interface; runtime changes stay behind the service | Adds request handling, process management, access control, and failure handling |

Embedding works well when one application owns the model lifecycle and needs close control of inputs, memory, or hardware resources. A service is useful when several applications need the same model, when models are expensive to load, or when the runtime must change without changing every client.

## Define the service responsibilities

The service can own:

- Model loading and unloading
- Request validation
- Input preprocessing and tokenization
- Inference
- Output decoding and postprocessing
- Streaming
- Health and readiness checks
- Error responses
- Request queues and concurrency limits
- Timing and memory measurements

The boundary should hide runtime-specific details that clients do not need. It should not hide information that clients need to use results correctly, such as class labels, confidence values, embedding dimensions, or truncation.

## Choose between a ready-made server and a wrapper

There are two common ways to expose local inference.

### Use a runtime server

`llama-server` exposes HTTP endpoints for GGUF language models. LiteRT-LM provides serving support for compatible language-model bundles. These servers already handle much of the model lifecycle, request processing, and streaming needed for text generation.

A ready-made server is a good starting point when its API and lifecycle match the application. The client remains responsible for understanding which features the selected model actually supports.

### Wrap an embedded runtime

LiteRT and ExecuTorch are commonly embedded into applications. A small wrapper service can expose only the tasks that other applications need.

For a classifier, the wrapper can accept an application-friendly input, apply the required preprocessing, run the model, and return labels with scores. The model performs classification; the wrapper manages the service boundary.

The wrapper should keep model-specific preprocessing close to the model. Otherwise, each client can interpret image size, normalization, tokenization, or output labels differently.

## Keep local services private by default

"Local" describes where inference runs, not who can reach it. A service bound only to the local machine has a different risk profile from one exposed to a local network or the internet.

Before making an endpoint reachable beyond the machine, account for authentication, encrypted transport, request size limits, rate limits, model licensing, sensitive inputs, and generated output. A service intended only for later Learning Paths should remain local unless remote access is a stated requirement.

## What you've accomplished

You have chosen the responsibilities that belong inside an inference service and identified when to use a runtime server or a small wrapper. Next, you will compare runtime families without assuming that one runtime fits every model task.
