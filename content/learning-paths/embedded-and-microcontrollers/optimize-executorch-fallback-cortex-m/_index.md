---
title: Deploy ML models across Cortex-M and Ethos-U with CMSIS-NN optimized kernels and the ExecuTorch CMSIS Pack

description: Build and run an ExecuTorch 1.4.0 application from the published ExecuTorch CMSIS Pack using Ethos-U, CMSIS-NN, and portable Cortex-M kernels.

minutes_to_complete: 60

who_is_this_for: This is an introductory topic for embedded machine learning developers building ExecuTorch applications for Cortex-M CPUs and Ethos-U NPUs.

learning_objectives:
    - Export an ExecuTorch graph with Ethos-U, CMSIS-NN, and portable-kernel execution regions
    - Lower quantized CPU fallback operations to optimized CMSIS-NN-backed Cortex-M operators, and understand the benefits in doing so
    - Install and consume the published ExecuTorch CMSIS Pack for version 1.4.0 with selected runtime and operator components
    - Run an application built from the ExecuTorch CMSIS Pack on a Corstone-300 Ethos-U55 FVP
    - Understand when and why to use the ExecuTorch CMSIS Pack

prerequisites:
    - An arm64 Linux computer with Docker and at least 30 GB of free storage; Ubuntu 24.04 LTS is a recommended option
    - Python 3.12 with support for virtual environments
    - Familiarity with PyTorch export and post-training quantization
    - Familiarity with CMake and command-line development tools
    - Awareness of Ethos-U NPU, and Cortex-M CPU

author:
- Matt Cossins

generate_summary_faq: false
rerun_summary: false
rerun_faqs: false
test_maintenance: false

### Tags
skilllevels: Introductory
subjects: ML
armips:
    - Cortex-M
    - Ethos-U
operatingsystems:
    - Linux
tools_software_languages:
    - Python
    - PyTorch
    - ExecuTorch
    - CMake
    - CMSIS
    - CMSIS Pack
    - CMSIS-NN
    - Docker
    - FVP
    - GCC

further_reading:
    - resource:
        title: ExecuTorch 1.4.0 release
        link: https://github.com/pytorch/executorch/releases/tag/v1.4.0
        type: documentation
    - resource:
        title: Published ExecuTorch CMSIS Pack
        link: https://www.keil.arm.com/packs/executorch-pytorch/overview/
        type: documentation
    - resource:
        title: ExecuTorch Arm Cortex-M backend
        link: https://docs.pytorch.org/executorch/stable/backends/arm-cortex-m/arm-cortex-m-overview.html
        type: documentation
    - resource:
        title: ExecuTorch Ethos-U with CMSIS-NN fallback example
        link: https://github.com/pytorch/executorch/blob/v1.4.0/examples/arm/ethos_u_cmsis_nn_fallback_example.ipynb
        type: documentation
    - resource:
        title: CMSIS-Toolbox install guide
        link: /install-guides/cmsis-toolbox/
        type: install_guide
    - resource:
        title: CMSIS-NN documentation
        link: https://arm-software.github.io/CMSIS-NN/latest/
        type: documentation

### FIXED, DO NOT MODIFY
# ================================================================================
weight: 1
layout: "learningpathall"
learning_path_main_page: "yes"
---
