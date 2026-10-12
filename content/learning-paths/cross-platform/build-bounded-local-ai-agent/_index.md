---
title: Build a bounded local AI agent from first principles

description: Build a local tool-using agent that calls an existing inference service while Python enforces tool schemas, budgets, permissions, and stopping conditions.

minutes_to_complete: 90

who_is_this_for: This Learning Path is for developers who want to understand and implement one local agent without hiding its control flow inside an agent framework.

learning_objectives:
  - Distinguish deterministic software, direct model calls, tool-calling assistants, and agents.
  - Connect an application-owned agent harness to the local inference service from the previous Learning Path.
  - Validate and execute structured tool calls in ordinary Python.
  - Bound the agent with step limits, tool budgets, timeouts, mutation controls, and execution traces.

prerequisites:
  - Complete [Build a local AI inference service on Arm](/learning-paths/cross-platform/build-local-ai-inference-service/)
  - Keep `llama-server` and `local-inference-service` from that Learning Path running
  - Basic familiarity with Python, JSON, and HTTP APIs

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
  - Python
  - llama.cpp
  - Pydantic
  - JSON
  - Generative AI

shared_path: true
shared_between:
  - laptops-and-desktops
  - servers-and-cloud-computing

further_reading:
  - resource:
      title: Build a local AI inference service on Arm
      link: /learning-paths/cross-platform/build-local-ai-inference-service/
      type: learning path
  - resource:
      title: Pydantic models
      link: https://docs.pydantic.dev/latest/concepts/models/
      type: documentation
  - resource:
      title: Python abstract syntax trees
      link: https://docs.python.org/3/library/ast.html
      type: documentation
  - resource:
      title: Python concurrent futures
      link: https://docs.python.org/3/library/concurrent.futures.html
      type: documentation

### FIXED, DO NOT MODIFY
# ================================================================================
weight: 1
layout: "learningpathall"
learning_path_main_page: "yes"
---
