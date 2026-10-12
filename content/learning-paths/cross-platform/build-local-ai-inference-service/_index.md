---
title: Build a local AI inference service on Arm

description: Design a reusable local inference layer that gives applications a consistent way to access generative and task-specific models on Arm.

minutes_to_complete: 75

who_is_this_for: This Learning Path is for developers who want to understand how local applications can use different model formats and inference runtimes through a consistent service interface.

learning_objectives:
  - Distinguish model artifacts, inference runtimes, hardware backends, services, and API contracts.
  - Build `llama.cpp` and run a GGUF language model directly on an Arm CPU.
  - Serve synchronous and streaming generation through a local HTTP API.
  - Use common generation and classification interfaces for `llama.cpp`, LiteRT, and ExecuTorch.

prerequisites:
  - An Arm computer or cloud instance running a Debian-based Linux distribution
  - At least 2 GB of available memory and 2 GB of free storage
  - Internet access and permission to install packages
  - Basic familiarity with the Linux command line and HTTP APIs

author:
  - Matt Cossins

generate_summary_faq: false
rerun_summary: false
rerun_faqs: false

### Tags
skilllevels: Introductory
subjects: ML
armips:
  - Cortex-A
  - Neoverse
operatingsystems:
  - Linux
tools_software_languages:
  - llama.cpp
  - LiteRT
  - LiteRT-LM
  - ExecuTorch
  - GGUF
  - CMake
  - Python
  - curl

shared_path: true
shared_between:
  - laptops-and-desktops
  - servers-and-cloud-computing

further_reading:
  - resource:
      title: llama.cpp server documentation
      link: https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md
      type: documentation
  - resource:
      title: LiteRT documentation
      link: https://ai.google.dev/edge/litert
      type: documentation
  - resource:
      title: LiteRT-LM repository
      link: https://github.com/google-ai-edge/LiteRT-LM
      type: repository
  - resource:
      title: ExecuTorch documentation
      link: https://docs.pytorch.org/executorch/stable/index.html
      type: documentation

### FIXED, DO NOT MODIFY
# ================================================================================
weight: 1
layout: "learningpathall"
learning_path_main_page: "yes"
---
