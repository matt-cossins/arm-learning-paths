---
title: Understand the Metis review workflow
description: Learn how Metis gathers evidence, runs security reviews, and presents findings for human triage.
weight: 2
layout: "learningpathall"
---

## What is Metis?

Arm Metis is an open-source, agentic security code-review framework. It combines language-aware source tooling with a large language model (LLM) to investigate security-relevant behavior and return structured review candidates. Metis supports multiple programming and hardware description languages through language plugins. This Learning Path uses C examples, but the same concepts can be applied to the other supported languages.

You first run Metis on a small C program with known vulnerabilities. This gives you a quick look at the command flow, JSON output, SARIF output, and reported findings. You then prepare a libpng source tree from the [Magma](https://hexhive.epfl.ch/magma/) benchmark and triage a captured Metis finding against the source diff.

The exercises show how to use Metis during a security review. They do not benchmark Metis accuracy. Model choice, provider behavior, Metis version, and source changes can all affect a run. Use published benchmark results for comparative performance data.

{{% notice Note %}}
Model-backed review can consume substantial API tokens. The initial exercise is less expensive than the optional live libpng run. A pre-captured libpng report candidate is included so you can complete the triage exercise without running the larger review.
{{% /notice %}}

## How Metis reviews code

A Metis review starts with source files and project context. Metis collects language-aware evidence, asks your configured model to investigate possible vulnerabilities, and returns structured findings for a human reviewer.

For C programs, reviewers often care about memory safety, integer arithmetic, resource management, parser state, and input validation. Tree-sitter is a parser that turns source files into syntax trees, so tools can identify functions, variables, calls, and other language constructs without treating code as plain text. Metis uses Tree-sitter to build a code graph of symbols and relationships. Its reachability review follows paths between possible attacker-controlled inputs and security-sensitive operations. The model receives source paths and targeted checks, rather than only a large prompt containing raw files.

## Providing Metis with context

Metis has two main ways to give the model source-code context:

- **Source navigation:** this is the default for review commands. Metis reads files from the codebase and gives the model targeted source snippets, paths, and checks. For C code, this includes Tree-sitter-based reachability analysis. Use this mode when you want to review a file, directory, patch, or small codebase without building an index first.
- **Vector indexing:** this is optional. The `index` command builds an embedding index for code and documentation, and `update` refreshes that index from a patch. Use indexing when you want to ask broad questions with `ask`, search across a larger repository, or add indexed context to later review and triage commands.

The exercises in this Learning Path use source navigation and C reachability analysis. You do not build an index because the review targets are small and the tasks are focused.

A typical Metis workflow looks like this:

1. Pick the review question, such as "review this parser file" or "review this patch."
2. Choose a command: `review_code`, `review_dir`, `review_file`, `review_patch`, `ask`, or `triage`.
3. Add project-specific security context in `.metis.md` when the source needs extra assumptions.
4. Run Metis and save the result as JSON, SARIF, or both.
5. Check each finding against the source code, input boundaries, build configuration, and tests.

Metis supplies the review workflow, source navigation, prompts, validation stages, and output handling. The model provider supplies the reasoning model. Results can vary between models and providers even when the source code is unchanged.

## Choose the review scope

Use the narrowest scope that answers your review question:

- `review_code` reviews files selected from the codebase and is useful for a broad first pass.
- `review_dir` focuses on one directory.
- `review_file` focuses on one source file while retaining codebase context.
- `review_patch` focuses on changed code and is suited to pull-request or pre-merge review.

This Learning Path demonstrates use of `review_code` and `review_file`.

## Interpret Metis findings

A Metis finding normally includes the issue, source location, reasoning, suggested mitigation, Common Weakness Enumeration (CWE) identifier, severity, and confidence. These fields provide a starting point for you to then investigate the findings.

{{% notice Note %}}
CWE identifiers, such as `CWE-190` for integer overflow, provide standard names for common classes of software weakness.
{{% /notice %}}

The main benefit is that Metis can reduce the amount of source navigation you do before a review becomes in-depth. You still decide whether a candidate is reachable, exploitable, already mitigated, or worth fixing.

For each finding, ask:

- Can untrusted data reach the reported value or operation?
- Does the build configuration include the reported code?
- Are the arithmetic limits and platform assumptions correct?
- Does an existing check or caller contract invalidate the report?
- Can you reproduce the behavior with a focused test or sanitizer?
- Does the proposed mitigation preserve intended behavior?

You will apply these questions to the libpng report later in the Learning Path.

## What you've learned and what's next

You have seen how Metis gathers source evidence, when indexing is useful, and why every result needs human triage. Next, you will install the tested release and add your provider API key.
