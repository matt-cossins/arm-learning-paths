---
title: Analyze ML models with Arm ML Inference Advisor

description: Learn how to use Arm ML Inference Advisor from the command line to check model compatibility, estimate performance, and identify target-aware model improvement opportunities using Ethos-U as the example target.

minutes_to_complete: 45

who_is_this_for: This Learning Path is for ML developers who want to use Arm's ML Inference Advisor (MLIA) to evaluate whether a model is suitable for a target before moving into deployment, graph inspection, or runtime profiling.

learning_objectives:
  - Explain what MLIA does and where it fits in model preparation
  - Use the MLIA CLI to discover targets, target profiles, and backends
  - Run compatibility and performance analysis on model artifacts
  - Interpret MLIA JSON output, metrics, unavailable fields, and advice
  - Compare how TOSA, TensorFlow Lite, and ExecuTorch artifacts enter MLIA workflows
  - Understand how to use the MLIA Python API to integrate MLIA with other tools and workflows.

prerequisites:
  - Ubuntu 22.04 LTS or another compatible Linux environment
  - Python 3.10 or later
  - Git and Git LFS to download the model artifacts
  - Basic familiarity with machine learning model deployment concepts
  - Basic familiarity with command-line tools

author:
  - Matt Cossins

### Tags
skilllevels: Introductory
subjects: ML
armips:
  - Cortex-M
  - Ethos-U

operatingsystems:
  - Linux

tools_software_languages:
  - MLIA
  - Vela
  - ExecuTorch
  - PyTorch
  - Python
  - TOSA
  - TensorFlow Lite

further_reading:
  - resource:
      title: Arm MLIA
      link: https://github.com/arm/mlia
      type: repository
  - resource:
      title: MLIA Ethos-U Plugin
      link: https://github.com/arm/mlia-ethos-u
      type: repository
  - resource:
      title: MLIA PyTorch Converter Plugin
      link: https://github.com/arm/mlia-converters-pytorch
      type: repository
  - resource:
      title: Arm ML model artifacts
      link: https://github.com/arm-education/ml-model-artifacts
      type: repository
  - resource:
      title: Ethos-U Vela compiler
      link: https://gitlab.arm.com/artificial-intelligence/ethos-u/ethos-u-vela
      type: repository

### FIXED, DO NOT MODIFY
# ================================================================================
weight: 1
layout: "learningpathall"
learning_path_main_page: "yes"
---
