---
title: Build a GStreamer-based AI inference perception pipeline & app on Raspberry Pi 5 (CPU or Accelerator)

description: Build and customize a GStreamer-based AI perception pipeline using Arm's Perception Pipeline Kit. Run on CPU or optionally on a Hailo accelerator using a live video input and your own model. Integrate into a simple python application.

minutes_to_complete: 45

who_is_this_for: This is an introductory topic for edge and physical AI developers who want to use the Arm Perception Pipeline Kit to build new GStreamer-based perception pipelines for AI inference using their own model and data sources, as well as integrating these pipelines into python applications.

learning_objectives: 
    - Understand the required components for a pipeline, and create a new custom pipeline leveraging live video input
    - Select a non-demo AI model and export to the .ONNX format before creating the required model.json and opchain.json files
    - Validate your custom GStreamer inference pipeline using the provided websink
    - (Optional) Move your inference onto a Hailo accelerator by selecting and using a Hailo-compatible model
    - Integrate your custom pipeline into a simple python application, and understand how to get started with building apps that leverage the pipelines.

prerequisites:
    - Raspberry Pi 5 (Recommended at least 32GB SD card or SSD)
    - (Optional) Hailo8, Hailo8L or Hailo10 (AI Hat+, AI Hat+ 2) accelerators
    - Arm Perception Pipeline Kit installed and set up according to the [Install Guide](https://learn.arm.com/install-guides/perception-kit/)
    - USB Camera

author: Matt Cossins

### Tags
skilllevels: Introductory
subjects: ML
armips:
    - Cortex-A
tools_software_languages:
    - GStreamer
    - ONNX
    - Docker
    - Dev Containers
    - JSON
    - Raspberry Pi
    - Python
operatingsystems:
    - Linux

further_reading:
    - resource:
        title: Perception Kit repository
        link: https://github.com/Arm-Debug/amp-dev-forge
        type: documentation
    - resource:
        title: GStreamer application development manual
        link: https://gstreamer.freedesktop.org/documentation/application-development/
        type: documentation


### FIXED, DO NOT MODIFY
# ================================================================================
weight: 1                       # _index.md always has weight of 1 to order correctly
layout: "learningpathall"       # All files under learning paths have this same wrapper
learning_path_main_page: "yes"  # This should be surfaced when looking for related content. Only set for _index.md of learning path content.
---
