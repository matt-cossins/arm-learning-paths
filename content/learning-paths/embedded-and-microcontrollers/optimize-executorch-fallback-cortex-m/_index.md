---
title: Deploy ML models across Cortex-M and Ethos-U with CMSIS-NN fallback

description: Build an ExecuTorch 1.5.1 application that delegates supported work to Ethos-U and uses CMSIS-NN for optimized Cortex-M fallback, demonstrated on Ethos-U55.

minutes_to_complete: 60

who_is_this_for: This Learning Path is for embedded machine learning developers who want to understand and build an ExecuTorch application split across an Ethos-U NPU and Cortex-M CPU.

learning_objectives:
    - Explain how ExecuTorch assigns model operations to Ethos-U, CMSIS-NN-backed Cortex-M operators, and portable kernels
    - Compare a Cortex-M baseline with a partially delegated Ethos-U program
    - Generate a model-specific CMSIS AI layer from published software packs
    - Build and run the mixed application on a Corstone-300 Ethos-U55 FVP

prerequisites:
    - A Windows or Linux computer with Git and Python 3.10 to 3.13
    - An internet connection and command-line access
    - Familiarity with PyTorch models and post-training quantization
    - Basic familiarity with Cortex-M processors and Ethos-U NPUs

author:
- Matt Cossins
- Kwashie Andoh

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
    - Windows
tools_software_languages:
    - Python
    - PyTorch
    - ExecuTorch
    - CMSIS
    - CMSIS Pack
    - CMSIS-NN
    - FVP
    - vcpkg

further_reading:
    - resource:
        title: CMSIS-Executorch example project
        link: https://github.com/Arm-Examples/CMSIS-Executorch
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
        title: ExecuTorch Arm Ethos-U backend
        link: https://docs.pytorch.org/executorch/stable/backends-arm-ethos-u.html
        type: documentation
    - resource:
        title: CMSIS-Toolbox MLOps integration
        link: https://open-cmsis-pack.github.io/cmsis-toolbox/build-overview/#mlops-information
        type: documentation
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
