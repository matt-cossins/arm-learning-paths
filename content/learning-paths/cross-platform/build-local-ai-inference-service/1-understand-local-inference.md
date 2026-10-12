---
title: Understand local AI inference
description: Separate the model artifact, runtime, hardware backend, service, and client application in a local inference system.
weight: 2

### FIXED, DO NOT MODIFY
layout: learningpathall
---

Before designing an inference service, separate the parts that are often grouped together as "the model." A model file, inference runtime, hardware backend, and HTTP endpoint each have a different job.

## Separate training from inference

Training creates a model. It presents examples to a neural network and adjusts numerical parameters called *weights*.

Inference uses the saved weights to calculate an output for a new input. An image classifier can assign scores to an image it has not seen before. A language model can receive a new prompt and predict the tokens that follow it.

This Learning Path covers inference. It does not train or fine-tune a model.

## Identify the parts of an inference system

A local AI application has five main layers:

| Layer | Responsibility |
| --- | --- |
| Application | Decides which task is required and uses the result |
| Service and API | Accepts requests, validates inputs, and returns results |
| Inference runtime | Loads the model and executes its operations |
| Hardware backend | Runs supported calculations on the CPU, GPU, or NPU |
| Model artifact | Stores the trained weights and information needed for inference |

A downloaded model artifact can contain weights, operations, tensor details, quantization information, and tokenizer configuration. It does not usually accept network requests or manage several clients. The runtime and service provide those capabilities.

Model formats include:

- GGUF, commonly used with `llama.cpp`
- `.litertlm`, used by LiteRT-LM
- `.tflite`, used by LiteRT
- `.pte`, used by ExecuTorch
- ONNX, used by ONNX Runtime and other tools

These formats are not interchangeable. Each runtime supports particular formats, operators, and hardware backends.

## Understand what the runtime does

An inference runtime:

1. Loads the model artifact.
2. Allocates memory for weights, inputs, outputs, and temporary data.
3. Converts application data into the tensors expected by the model.
4. Executes the model operations.
5. Uses available CPU, GPU, or NPU implementations.
6. Returns the output to the application.

Some runtimes are embedded directly into an application. Others include a server. The presence of a runtime does not by itself mean that an HTTP service is available.

## Account for different model tasks

Not every model accepts text and produces a conversational answer. Models can generate text, classify images, detect objects, transcribe speech, produce embeddings, or classify intent.

Each task has different inputs and outputs. An image classifier can receive an image tensor and return class scores. An embedding model can receive text and return a numerical vector. A language model receives tokens and repeatedly predicts another token.

The service interface should reflect these differences. A generation request and a classification request do not need to look like the same operation.

## Follow language-model generation

A language model generates a response one token at a time:

1. A tokenizer converts the prompt into token identifiers.
2. The model processes the prompt. This phase is called *prefill*.
3. The model calculates probabilities for the next token.
4. The runtime selects a token and adds it to the sequence.
5. The model repeats this *decode* phase until it reaches a stopping condition.

A long prompt increases prefill work. A long response increases decode work. This distinction leads to three useful measurements:

- *Time to first token (TTFT)*: the delay before generated output begins
- *Generation speed*: the rate at which output tokens are produced
- *Total generation time*: the time required for the complete response

During decode, the runtime stores intermediate attention data in the *key-value cache*, usually shortened to *KV cache*. This avoids recalculating earlier tokens but consumes memory. Longer contexts and concurrent requests can increase this memory requirement.

## Consider quantization and processor choice

Quantization represents model values at lower precision. It can reduce file size, memory use, loading time, and computation. It can also change model quality or task accuracy, so the effect must be checked for the selected model and workload.

The runtime can divide work between processors. A GPU or NPU might execute supported model operations while the CPU continues to handle tokenization, request processing, sampling, and unsupported operations.

Model format alone does not determine performance. Runtime implementation, processor support, model structure, quantization, memory bandwidth, input size, and concurrency all contribute.

## What you've learned

You can now separate the application, service, runtime, hardware backend, and model artifact. Next, you will decide where the service boundary belongs and what it should provide to client applications.
