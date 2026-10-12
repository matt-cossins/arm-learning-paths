---
title: Compare inference runtimes
description: Compare runtime and model-format choices for language generation and task-specific inference on Arm.
weight: 4

### FIXED, DO NOT MODIFY
layout: learningpathall
---

The service interface can stay stable while the runtime behind it changes. Runtime selection still matters because it determines which model artifacts, operators, processors, and deployment environments are available.

## Compare the runtime families

| Runtime | Typical artifact | Typical use | Service approach |
| --- | --- | --- | --- |
| `llama.cpp` | GGUF | Language generation and embeddings | Use `llama-server` |
| LiteRT-LM | `.litertlm` | Language models on edge platforms | Use its serving support or embed it |
| LiteRT | `.tflite` | Classification, detection, audio, and other task-specific models | Embed it or add a small wrapper |
| ExecuTorch | `.pte` | PyTorch models deployed to edge devices | Embed it or add a small wrapper |

This comparison describes common uses, not hard boundaries. Check model support, runtime documentation, and target hardware before selecting a runtime.

## Start with the model and task

Ask these questions in order:

1. What task must the application perform?
2. Which models meet the quality, accuracy, latency, memory, and licensing requirements?
3. In which formats are those models available or exportable?
4. Which runtimes support the required model operations?
5. Which of those runtimes has a suitable backend for the target Arm hardware?
6. Does the runtime provide a suitable service, or does it need a wrapper?

Starting with a preferred runtime can exclude better models or force an unsuitable API. Starting with the task keeps the selection tied to application requirements.

## Separate portability from acceleration

A portable model format does not guarantee identical execution on every device. The runtime may use different kernels or delegate supported operations to different processors.

When an accelerator does not support an operation, the runtime might run that operation on the CPU. This fallback can be correct but slower than expected, and moving tensors between processors can add overhead.

For each runtime and backend, check:

- Supported operators and data types
- Quantization formats
- Maximum or practical input sizes
- CPU, GPU, and NPU coverage
- Fallback behavior
- Memory requirements
- Threading and concurrency behavior
- Tools for logs, traces, and profiling

## Treat conversion as part of deployment

Converting or exporting a model can change operator selection, tensor layout, quantization, or supported input shapes. A converted model should be checked against the original model using inputs like those the application will receive.

The service also needs the preprocessing and postprocessing associated with that artifact. Keeping those details versioned with the model avoids silent differences between clients.

## What you've learned

You can compare runtimes using the task, model support, hardware backend, and service needs. Next, you will define a small set of application-facing operations that do not expose unnecessary runtime details.
