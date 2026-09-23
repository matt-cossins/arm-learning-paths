---
title: Prepare a realistic Magma libpng target
description: Build a reviewable libpng source tree from Magma while removing benchmark canaries and fix branches.
weight: 5
layout: "learningpathall"
---

## Why prepare a Magma libpng target?

The previous section used a small labeled program to teach the Metis review process. This section prepares a larger C codebase so you can see how a Metis finding is triaged against source that looks closer to real project code.

[Magma](https://hexhive.epfl.ch/magma/) gives you a repeatable way to prepare that target. Magma is a benchmark for evaluating fuzzers against real programs with documented vulnerabilities. A fuzzer is a testing tool that repeatedly runs a program with generated or mutated inputs to trigger crashes, hangs, memory errors, or other unexpected behavior.

You use Magma here only to create a prepared libpng source tree for review. You are not using Magma to benchmark Metis. You also do not give Metis the benchmark metadata, bug names, fuzzing harnesses, canaries, or fix branches, because those details would give a review model clues that a normal codebase would not contain.

The preparation script creates the review target in four steps:

1. Checks out the libpng revision selected by Magma.
2. Applies Magma patches that introduce known vulnerable code.
3. Removes benchmark controls so the source looks closer to a normal libpng tree.
4. Writes neutral Metis context for the review.

The result is a deliberately vulnerable example target. Do not use it outside this exercise.

## Download the preparation script

Download [the Magma libpng preparation script](https://github.com/ArmDeveloperEcosystem/arm-learning-paths/blob/main/content/learning-paths/cross-platform/review-c-code-with-metis/files/prepare_magma_libpng.py) into the exercise workspace:

```bash
curl -L \
  https://raw.githubusercontent.com/ArmDeveloperEcosystem/arm-learning-paths/main/content/learning-paths/cross-platform/review-c-code-with-metis/files/prepare_magma_libpng.py \
  -o prepare_magma_libpng.py
```

Clone Magma, then check out the commit tested for this Learning Path:

```bash
git clone https://github.com/HexHive/magma.git
git -C magma checkout 75d1ae7b180443a778b8830c79176ca5f93642ac
```

Run the script to create `libpng-review`:

```bash
python prepare_magma_libpng.py \
  --magma-dir magma \
  --output-dir libpng-review
```

The output is similar to:

```output
Prepared libpng commit a37d4836519517bdce6cb9d956092321eca3e73b
Applied 7 Magma vulnerability-introducing patches
Output: /Users/you/metis-security-review/libpng-review
```

## Inspect the prepared source

The preparation script removes Magma benchmark controls from the prepared source tree. This keeps the review target closer to a normal libpng checkout instead of a benchmark harness.

Confirm that the prepared tree has local changes:

```bash
git -C libpng-review status --short
git -C libpng-review diff --stat
```

The diff summary shows that the script applied patches that introduce known vulnerable code to libpng. You will inspect the relevant `pngrutil.c` changes during triage. Do not send patch names, benchmark descriptions, or known vulnerability lists to Metis.

## Choose a libpng report option

You need a Metis report before you can triage a finding. Choose one of these options:

- Run a live Metis review if you have enough API quota and want to compare your model configuration.
- Use the pre-captured report if you are interested to try Metis, but want to minimize your API usage.

{{< tabpane-normal >}}
  {{< tab header="Run live review" >}}
This option asks Metis to review only `pngrutil.c`, because the triage exercise focuses on a finding in that file.

The live libpng review can run for many minutes, and consume substantial model tokens. Use the pre-captured report option if a live run is too costly or does not produce a finding you can triage.

```bash
cd "$HOME/metis-security-review/libpng-review"
metis \
  --codebase-path . \
  --non-interactive \
  --command "review_file pngrutil.c" \
  --output-file ../results/libpng-live.json
cd "$HOME/metis-security-review"
```

This writes `results/libpng-live.json`.
  {{< /tab >}}
  {{< tab header="Use captured report" >}}
This option creates `results/libpng-review-candidate.json` from a captured Metis report. Use it when you want the next triage section to match the source region and explanation shown in this Learning Path.

```bash
cat > results/libpng-review-candidate.json <<'EOF'
{
  "_provenance": {
    "artifact_type": "Captured Metis report finding",
    "release_under_test": "metis-v1.5.0",
    "capture_note": "Use this artifact to study report structure and triage; do not treat it as guaranteed output for every run."
  },
  "reviews": [
    {
      "reviews": [
        {
          "issue": "Externally controlled image dimensions can trigger division by zero in IDAT chunk length validation",
          "code_snippet": "size_t row_factor_l =\n         (size_t)png_ptr->width\n         * (size_t)png_ptr->channels\n         * (png_ptr->bit_depth > 8? 2: 1)\n         + 1\n         + (png_ptr->interlaced? 6: 0);\n\n\n      size_t row_factor = (png_uint_32)row_factor_l;\n      if (png_ptr->height > PNG_UINT_32_MAX/row_factor)",
          "start_line": 3163,
          "end_line": 3172,
          "reasoning": "For IDAT chunks, row_factor_l is derived from PNG IHDR-controlled fields stored in png_ptr (width, channels/color type, bit depth, and interlace). On platforms where size_t is wider than png_uint_32, row_factor_l can exceed 32 bits for very large but 31-bit-valid PNG dimensions. It is then truncated by the cast to png_uint_32 and stored back in size_t. Certain valid arithmetic combinations can truncate to 0 (for example, an RGB 8-bit non-interlaced row factor of width*3+1 can equal 2^32). The next line divides by row_factor without checking for zero, so a crafted PNG can crash the decoder during chunk header validation, causing denial of service.",
          "mitigation": "Do not truncate row_factor_l before using it as a divisor. Keep the computation in png_alloc_size_t/size_t, explicitly check row_factor_l != 0 and row_factor_l <= PNG_UINT_32_MAX where required, or clamp oversized row factors to a safe maximum before division. Prefer overflow-checked helpers for all dimension-derived arithmetic.",
          "confidence": 0.86,
          "cwe": "CWE-369",
          "severity": "Medium",
          "anchor": {
            "file_path": "pngrutil.c",
            "start_line": 3163,
            "end_line": 3172,
            "start_col": 0,
            "end_col": 55,
            "start_byte": 97432,
            "end_byte": 97734,
            "symbol": "pngrutil.c::png_check_chunk_length",
            "kind": "range",
            "content_hash": "d4fcc275896c8895",
            "confidence": "exact"
          },
          "line_number": 3163
        }
      ],
      "file": "pngrutil.c",
      "file_path": "pngrutil.c"
    }
  ]
}
EOF
```

The captured report demonstrates the Metis report structure and provides a stable triage exercise. It is not expected output for every run.
  {{< /tab >}}
{{< /tabpane-normal >}}

## What you've accomplished and what's next

You prepared production-like vulnerable libpng source without benchmark hints and selected a report for triage. Next, you will check a reported finding against the benchmark diff and decide how to handle additional live findings.
