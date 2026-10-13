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

Metis uses two complementary review approaches:

- **Simple LLM review:** the model examines source code or a patch using language-specific security prompts and project guidance. It returns structured findings without requiring a code graph. This is also the review path for languages without C/C++ reachability support.
- **Reachability and codegraph review:** for C/C++, Tree-sitter parses source into a graph of functions and call relationships. Metis uses that graph to give the model focused source context around possible attacker-controlled inputs and security-sensitive operations. The model can assess a candidate in the context of callers, callees, and relevant checks rather than treating a source snippet in isolation.

In Metis v1.5.5, the packaged Review stage runs both `simple_llm_review` and `reachability`, then combines and deduplicates their findings. The C exercises use this stage through `review_code` and `review_file`. Graph evidence helps explain possible paths through the code; it does not by itself prove attacker control, build reachability, or exploitability.

## Follow the review workflow

A typical Metis workflow looks like this:

1. Pick the review question, such as "review this parser file" or "review this patch."
2. Choose a review command: `review_code`, `review_dir`, `review_file`, or `review_patch`.
3. Add project-specific security context in `.metis.md` when the source needs extra assumptions.
4. Run Metis and save the result as JSON, SARIF, or both.
5. Optionally run Metis triage to assess the candidates against additional source evidence.
6. Check the remaining findings against the source code, input boundaries, build configuration, and tests.

Metis supplies the review workflow, source navigation, prompts, validation stages, and output handling. The model provider supplies the reasoning model. Results can vary between models and providers even when the source code is unchanged.

## Choose the review scope

Use the narrowest scope that answers your review question:

- `review_code` reviews files selected from the codebase and is useful for a broad first pass.
- `review_dir` focuses on one directory.
- `review_file` focuses on one source file while retaining codebase context.
- `review_patch` focuses on changed code and is suited to pull-request or pre-merge review.

This Learning Path demonstrates `review_code` and `review_file` at the prompt started with `--interactive`. Direct review commands run their Initialize prerequisites automatically, so the exercises do not need a separate `init` command.

## Strengthen findings with automated triage

Review discovers candidate issues; triage checks those candidates against concrete evidence. For C/C++, Metis gives the model the reported source, enclosing function, caller/callee relationships, and reachability context. Navigation tools can help resolve missing definitions, macros, or guards. The model returns `valid`, `invalid`, or `inconclusive`, with file-and-line citations and an explanation connecting the evidence to the finding.

A contradicted claim can be rejected, while a missing critical caller, guard, or input path can leave a finding `inconclusive`. Checking these details can strengthen well-supported findings, reduce false positives, and expose evidence gaps that need human investigation. A `valid` decision remains a static assessment, not proof of a working exploit.

Without `--interactive`, Metis v1.5.5 runs the full configured graph. The packaged graph includes Initialize, Review, and Triage, so it triages findings automatically. In interactive mode, `--triage` optionally chains Triage after `review_code`, `review_dir`, `review_file`, or `review_patch`; the `triage` command can instead assess an existing SARIF report.

Automated triage can consume additional model tokens. These exercises use `--interactive` without `--triage` so you can inspect review-only findings and practice manual triage. See the [Metis v1.5.5 triage flow](https://github.com/arm/metis/blob/metis-v1.5.5/docs/triage-flow.md) for the triage statuses and SARIF annotations.

## Configure the workflow with graph YAML

The execution graph describes the workflow, not the source code's call graph. In `metis.yaml`, `metis_engine.execution` selects stages and the nodes that do work within them: `initialize` builds the CodeGraph; `review` combines `simple_llm_review` and `reachability`, then deduplicates findings; and `triage` checks the resulting SARIF findings. Input bindings pass data and establish dependencies, while `depends_on` controls ordering where no data is passed.

The exercises configure only the model provider and inherit the packaged execution graph. An explicit `execution` section replaces the whole packaged graph, rather than merging individual nodes. To customize it, start from the [Metis v1.5.5 execution-graph configuration](https://github.com/arm/metis/blob/metis-v1.5.5/docs/execution-graph.md#default-graph) and retain the stages and dependencies needed for your chosen review approach.

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

You have seen how simple LLM review and reachability analysis find candidates, how automated triage strengthens the evidence, and why human validation is still needed. Next, you will install the tested release and add your provider API key.
