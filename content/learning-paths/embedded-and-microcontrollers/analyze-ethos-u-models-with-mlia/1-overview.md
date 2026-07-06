---
title: What is the ML Inference Advisor?

weight: 2

### FIXED, DO NOT MODIFY
layout: "learningpathall"
---

## Understand what MLIA does

Arm ML Inference Advisor (MLIA) helps you evaluate whether a machine learning model is suitable for a target inference platform.

In this Learning Path, you use MLIA from the command line to check model compatibility, estimate performance, and read advice that points toward useful model changes. These examples use Arm Ethos-U as an example target.

MLIA is most useful before full deployment or runtime profiling, when you are asking questions such as:

- Will this model map cleanly to my target?
- Which target profile should I use for early analysis?
- Which operators or layers are likely to matter most for performance?
- Is the model compute-bound, memory-bound, or affected by low MAC utilization?
- What should I investigate before building firmware or running on a board?

MLIA does not make the final optimization decision for you. It gives target-aware evidence so you can decide what to change, what to measure next, and which workflow stage deserves attention.

## Use the CLI first

The MLIA CLI is the primary workflow in this Learning Path. You will use it to:

- discover installed targets, target profiles, and backends
- run compatibility checks
- run performance analysis
- request JSON output
- inspect advice and metrics

After you understand the CLI workflow, you will briefly use the Python API. The API is useful when you want to embed MLIA results in another product, dashboard, CI job, or tool.

## Using MLIA alongside other tools

MLIA is not a replacement for graph visualization or runtime profiling. It is an advisory layer that helps earlier in the model preparation workflow.

| Tool | Use it to answer |
| --- | --- |
| MLIA | Is this model suitable for my target, and what should I change? |
| Model Explorer | What does the generated model artifact graph look like? |
| Vela | How does the Ethos-U compiler map supported work onto the NPU? |
| Runtime-specific profiling tools | What happened when the model actually ran? For example, use ETRecord, ETDump, and ExecuTorch Inspector for ExecuTorch deployments, or TensorFlow Lite benchmark and profiling tools for TFLite deployments. |

For example, MLIA can tell you which layers dominate estimated cycles or have low MAC utilization. Model Explorer can show how an ExecuTorch `.pte` artifact is partitioned into delegate regions. Runtime-specific profiling tools can show behavior after you have a runnable deployment.

Use these tools together:

- Use MLIA before or during model preparation.
- Use Model Explorer to inspect generated artifacts and delegation structure.
- Use runtime profiling tools after you can execute the model.

## Understand the plugin model

MLIA uses a plugin model. The `mlia` core package provides the shared command-line interface, output structure, and Python API. Target, backend, and converter support is added through plugins.

The important repositories are:

- `arm/mlia`: core MLIA package
- `arm/mlia-ethos-u`: Ethos-U target plugin and Vela/Corstone backend plugins
- `arm/mlia-converters-pytorch`: PyTorch `.pt2` converter plugin for TOSA and PTE routes
- `arm/mlia-legacy`: legacy support for older MLIA flows

## Understand the model formats

MLIA can analyze different kinds of model artifacts depending on what workflow you are using and the stage you want to analyze.

| Format | Where it fits |
| --- | --- |
| `.pt2` | PyTorch exported program input for PyTorch and ExecuTorch-oriented workflows. |
| `.tosa` | Intermediate representation consumed by compiler/backend flows such as Ethos-U Vela. |
| `.pte` | Serialized ExecuTorch program. Ethos-U `.pte` performance analysis uses Corstone backends. |
| `.tflite` | TensorFlow Lite model format used in many Ethos-U and embedded ML workflows. |

## What you have learned

You have learned what MLIA does, what you use it for, and how MLIA fits alongside other tools.

Next, you will install MLIA and inspect the capabilities available in your environment.
