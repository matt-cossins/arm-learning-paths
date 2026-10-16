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

The captured v1.5.5 review used 1,770,160 model tokens. A live run can take several minutes and consume substantial API quota. Use the captured report option to avoid those model calls or if your run does not produce a finding you can triage.

```bash
cd "$HOME/metis-security-review/libpng-review"
metis \
  --interactive \
  --codebase-path . \
  --config "$HOME/metis-security-review/metis-review.yaml" \
  --output-file ../results/libpng-live.json
```

`--interactive` opens the command prompt instead of running the full configured graph. At the prompt, `review_file` runs the required Initialize prerequisites automatically, then reviews the file. This command omits `--triage`, so Metis does not run automated triage; you will validate a finding manually in the next section. Review the file, then exit after the review completes:

```console
review_file pngrutil.c
exit
```

Back in your shell, return to the exercise workspace:

```bash
cd "$HOME/metis-security-review"
```

This writes `results/libpng-live.json`.
  {{< /tab >}}
  {{< tab header="Use captured report" >}}
This option creates `results/libpng-review-candidate.json` from the Metis v1.5.5 review captured on October 15, 2026. The full run returned three findings; this file keeps the division-by-zero finding so the following manual triage exercise uses a repeatable example. The finding is unchanged from the live report, with the review group's source path made relative for portability.

```bash
cat > results/libpng-review-candidate.json <<'EOF'
{
  "_provenance": {
    "artifact_type": "Single finding extracted from a Metis review",
    "release_under_test": "metis-v1.5.5",
    "metis_commit": "a9f9bdbc9b0ee5c511e32c526fdbdd33719d0ace",
    "capture_date": "2026-10-15",
    "configured_model": "gpt-5.5",
    "reported_model": "gpt-5.5-2026-04-23",
    "magma_commit": "75d1ae7b180443a778b8830c79176ca5f93642ac",
    "libpng_commit": "a37d4836519517bdce6cb9d956092321eca3e73b",
    "prepared_source_sha256": "f628738930426bea4dccd718e5d90daaf012d5cef365880fa0f6adc4f936a78d",
    "command": "review_file pngrutil.c",
    "automatic_triage": false,
    "capture_note": "One finding extracted from the captured run; group source paths are relative for this exercise."
  },
  "reviews": [
    {
      "reviews": [
        {
          "id": "local-7a71cbab2664-0",
          "issue": "Attacker-controlled image width can make IDAT chunk-length validation divide by zero",
          "line_number": 3163,
          "anchor": {
            "file_path": "pngrutil.c",
            "start_line": 3163,
            "end_line": 3177,
            "start_col": 0,
            "end_col": 80,
            "start_byte": 97432,
            "end_byte": 97976,
            "symbol": "pngrutil.c::png_check_chunk_length",
            "kind": "range",
            "content_hash": "80d065e971b7d4ce",
            "confidence": "exact"
          },
          "primary_file": "pngrutil.c",
          "primary_function": "pngrutil.c::png_check_chunk_length",
          "analysis_type": "reachability_local",
          "path": [
            "pngread.c::png_read_png",
            "pngread.c::png_read_info",
            "pngrutil.c::png_read_chunk_header",
            "pngrutil.c::png_check_chunk_length"
          ],
          "code_snippet": "3161:    {\n3162:       png_alloc_size_t idat_limit = PNG_UINT_31_MAX;\n3163:       size_t row_factor_l =\n3164:          (size_t)png_ptr->width\n3165:          * (size_t)png_ptr->channels",
          "cwe": "CWE-369",
          "severity": "Medium",
          "confidence": 0.78,
          "reasoning": "For IDAT chunks, the code derives row_factor_l from attacker-controlled IHDR fields: width, channels, bit_depth, and interlace flag. It then truncates this size_t value through an explicit cast to png_uint_32 before using it as the divisor in PNG_UINT_32_MAX/row_factor and later idat_limit/row_factor. A valid 31-bit PNG width can make row_factor_l exactly 2^32; for example, an 8-bit RGB non-interlaced image has channels == 3, bit_depth <= 8, and interlaced == 0, so width 1431655765 yields width * 3 + 1 == 4294967296. After the cast, row_factor becomes 0, and the following divisions execute with a zero divisor. This gives a crafted PNG a parser-crash denial of service when an IDAT chunk length is checked. Exploitability depends on the active user/build width limits permitting such a large width; if a lower user_width_max/default limit is enforced before IDAT processing, that configuration would block this specific input. The vulnerable arithmetic itself is in this function and has no local zero check before division.",
          "mitigation": "Do not truncate row_factor_l before validating it. Keep the computation in a type wide enough for the maximum supported row size, reject values greater than PNG_UINT_32_MAX or otherwise outside allocation limits, and explicitly check row_factor != 0 before using it as a divisor. Prefer using checked multiplication/addition helpers for all dimension-derived row-size calculations."
        }
      ],
      "file": "pngrutil.c",
      "file_path": "pngrutil.c"
    }
  ]
}
EOF
```

This is a captured finding from the same release used in the exercises, not guaranteed output for every run. Its reasoning includes an important precondition: the configured image-width limits must permit the large input. The next section checks that condition against the source.
  {{< /tab >}}
{{< /tabpane-normal >}}

## What you've accomplished and what's next

You prepared production-like vulnerable libpng source without benchmark hints and selected a report for triage. Next, you will check a reported finding against the benchmark diff and decide how to handle additional live findings.
