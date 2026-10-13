---
title: Compare a Metis report with vulnerable C code
description: Run a Metis review, inspect JSON and SARIF output, and compare the report with known defects in a small C program.
weight: 4
layout: "learningpathall"
---

## Prepare the example program

The [Damn Vulnerable C Program](https://github.com/hardik05/Damn_Vulnerable_C_Program) contains vulnerabilities intentionally placed and labeled in one C file. Use it first to learn the Metis review process: prepare a small target, run `review_code`, save JSON and SARIF, summarize findings, and compare source locations.

In your terminal, clone the repository and copy `dvcp.c` into a separate review directory. The copy keeps the review target small and avoids sending the rest of the repository to Metis:

```bash
git clone --depth 1 https://github.com/hardik05/Damn_Vulnerable_C_Program.git
mkdir -p dvcp-review
cp Damn_Vulnerable_C_Program/dvcp.c dvcp-review/
```

Add a short threat-model note for the review. Metis reads `.metis.md` as project context:

```bash
cat > dvcp-review/.metis.md <<'EOF'
# Project security context

This command-line C program parses an image file supplied by an untrusted user.
Treat file contents, dimensions, offsets, and derived allocation sizes as
attacker-controlled. Review memory safety, integer arithmetic, resource
exhaustion, input validation, and cleanup on error paths.
EOF
```

The note tells Metis how to treat inputs and security boundaries. The source file still contains teaching comments, which is acceptable here because this step teaches the review workflow. You will use libpng for a more realistic triage example.

## Run the review

Change into the review directory and start the Metis interactive prompt with the provider configuration you created. Save JSON for detailed inspection and SARIF for code-scanning tools:

```bash
cd "$HOME/metis-security-review/dvcp-review"
metis \
  --interactive \
  --codebase-path . \
  --config "$HOME/metis-security-review/metis-review.yaml" \
  --output-file ../results/dvcp.json \
  --output-file ../results/dvcp.sarif
```

At the Metis prompt, run the review, then exit after it completes. The review command runs its Initialize prerequisites automatically, then combines simple LLM and reachability review findings:

```console
review_code
exit
```

Metis prints review progress and detailed findings under `File:`, with an `Identified issue` heading. Finding fields include `Snippet`, `Line number`, `CWE`, `Severity`, `Why`, `Mitigation`, and `Confidence`. After the findings, the export and token-usage output is similar to:

```output
Results saved to ../results/dvcp.json
SARIF report saved to ../results/dvcp.sarif
Token usage (review_code)
Current (input: 20,526 · output: 9,687 · total: 30,213)
```

Back in your shell, return to the exercise workspace:

```bash
cd "$HOME/metis-security-review"
```

The run sends source-derived evidence to your configured model provider. Runtime, token use, and findings depend on the model, provider, and Metis version.

It can take a couple of minutes to complete.

## Summarize the JSON report

The JSON report stores findings in `reviews[].reviews`. Source locations can appear in an `anchor`, in `primary_file` and `line_number`, or in the enclosing review group's `file` field. Use the Python interpreter from the active Metis environment to count the findings and print their issue types and source locations:

```bash
python - <<'PY'
import json
from pathlib import Path

data = json.loads(Path("results/dvcp.json").read_text())
review_groups = data["reviews"]
count = sum(len(group["reviews"]) for group in review_groups)
print(f"Finding count: {count}")
for review_group in review_groups:
    for finding in review_group["reviews"]:
        anchor = finding.get("anchor") or {}
        file_path = (
            anchor.get("file_path")
            or finding.get("primary_file")
            or finding.get("file")
            or review_group.get("file")
        )
        line = anchor.get("start_line") or finding.get("line_number")
        print(
            f"- {finding['cwe']} {finding['issue']} "
            f"({file_path}:{line})"
        )
PY
```

This example was captured on October 15, 2026 using the `metis-v1.5.5` tag ([`a9f9bdb`](https://github.com/arm/metis/commit/a9f9bdbc9b0ee5c511e32c526fdbdd33719d0ace)), with `gpt-5.5` through an OpenAI-compatible endpoint and DVCP commit [`8dcbd20`](https://github.com/hardik05/Damn_Vulnerable_C_Program/commit/8dcbd202887f587783952a320a2301de701be529). The provider reported the model version as `gpt-5.5-2026-04-23`. Automated triage was not enabled.

The output is similar to:

```output
Finding count: 11
- CWE-125 Untrusted image fields are printed as NUL-terminated strings, causing out-of-bounds reads (dvcp.c:48)
- CWE-190 Integer overflow in allocation size leads to undersized allocation and heap buffer overflow (dvcp.c:54)
- CWE-415 Allocated pointer is freed twice on attacker-controlled path (dvcp.c:58)
- CWE-416 Use-after-free write to heap allocation (dvcp.c:59)
- CWE-191 Integer underflow/unchecked allocation size causes heap buffer overflow or NULL-pointer write (dvcp.c:74)
- CWE-369 Attacker-controlled division by zero (dvcp.c:81)
- CWE-122 Unchecked quotient controls allocation size and fixed-size copy, causing heap buffer overflow (dvcp.c:82)
- CWE-125 Out-of-bounds reads using attacker-controlled index (dvcp.c:89)
- CWE-787 Out-of-bounds writes to stack and heap buffers using attacker-controlled index (dvcp.c:93)
- CWE-401 Attacker-controlled memory leak on repeated records causes denial of service (dvcp.c:97)
- CWE-400 Attacker-controlled multiplication overflow and unbounded recursion/allocations cause denial of service (dvcp.c:104)
```

Your exact count and wording can differ. A valid report can contain zero findings. An empty report means that this run did not report any findings; it does not mean the program is safe. If you expected findings, check your provider connection and any Metis log output before judging the result.

## Compare the report with known defects

Display four source regions that the program identifies as deliberately vulnerable:

```bash
sed -n '14,28p' dvcp-review/dvcp.c
sed -n '42,69p' dvcp-review/dvcp.c
sed -n '72,87p' dvcp-review/dvcp.c
sed -n '89,115p' dvcp-review/dvcp.c
```

Check whether your report covers these concrete cases:

- Signed image dimensions are combined and passed to `malloc()` without overflow or range checks.
- `buff1` is freed, then freed again when `size1` is even or written after free when it is divisible by three.
- `img.height` is used as a divisor without a zero check.
- `size3` is used as an index into fixed-size and heap buffers without bounds checks.
- Attacker-controlled dimensions can select recursive stack exhaustion or repeated heap allocation.

The captured v1.5.5 JSON and SARIF reports contain 11 findings. Source anchors can span multiple lines, so the table maps their reported regions to the known source defects rather than treating each anchor's first line as the exact faulty operation:

| Source issue | Tested-run outcome |
| --- | --- |
| Non-NUL-terminated image fields passed to `%s` | `CWE-125` at `dvcp.c:48` |
| `size1` and `size2` arithmetic before allocations and fixed-size copies | `CWE-190` at `dvcp.c:54–58`; `CWE-191` at `dvcp.c:74–79` |
| `buff1` double free and use-after-free | `CWE-415` at `dvcp.c:58–63`; `CWE-416` at `dvcp.c:59–69` |
| Division by zero and an unchecked quotient used for the `buff4` allocation | `CWE-369` at `dvcp.c:81–82`; `CWE-122` at `dvcp.c:82–87` |
| Indexed reads and writes outside stack and heap buffers | `CWE-125` at `dvcp.c:89–91`; `CWE-787` at `dvcp.c:93–95` |
| `buff4` allocation lost without being freed | `CWE-401` at `dvcp.c:97–103` |
| Multiplication overflow, recursive stack exhaustion, and repeated heap allocation | `CWE-400` at `dvcp.c:104–115` |

For each reported finding, verify the source location, attacker control, and operation. Also record known source defects that the run omitted. The goal is to practice reviewing Metis output, not to turn the finding count into a coverage score.

The same review is also available in `results/dvcp.sarif`. SARIF allows code-hosting services and security tools to associate findings with source locations. Keep JSON when you want the complete Metis reasoning and SARIF when you want to integrate results into an existing code-scanning workflow.

This shows that Metis can report several issues, but it is not guaranteed to find everything. Runs are non-deterministic and also depend on the model used.

## What you've accomplished and what's next

You ran a complete Metis review, exported two report formats, and compared the reported findings with known defects. Next, you will prepare a realistic libpng target without leaving benchmark canaries or fixes in its source.
