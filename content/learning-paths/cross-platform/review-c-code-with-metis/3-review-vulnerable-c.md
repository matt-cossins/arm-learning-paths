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

Change into the review directory and run `review_code`. Save JSON for detailed inspection and SARIF for code-scanning tools:

```bash
cd "$HOME/metis-security-review/dvcp-review"
metis \
  --codebase-path . \
  --non-interactive \
  --command "review_code" \
  --output-file ../results/dvcp.json \
  --output-file ../results/dvcp.sarif
cd "$HOME/metis-security-review"
```

The run sends source-derived evidence to your configured model provider. Runtime, token use, and findings depend on the model, provider, and Metis version.

It can take a couple of minutes to complete.

## Summarize the JSON report

Use the Python interpreter from the active Metis environment to print the issue type and source location for each finding:

```bash
python - <<'PY'
import json
from pathlib import Path

data = json.loads(Path("results/dvcp.json").read_text())
findings = [
    finding
    for review_group in data["reviews"]
    for finding in review_group["reviews"]
]

print(f"Finding count: {len(findings)}")
for finding in findings:
    anchor = finding.get("anchor") or {}
    file_path = (
        anchor.get("file_path")
        or finding.get("primary_file")
        or finding.get("file")
    )
    line = anchor.get("start_line") or finding.get("line_number")
    print(
        f"- {finding['cwe']} {finding['issue']} "
        f"({file_path}:{line})"
    )
PY
```

The output is similar to:

```output
Finding count: 9
- CWE-190 Image width and height read from the file are added in a signed int without validation, allowing overflow before the result is used as an allocation size. (dvcp.c:54)
- CWE-120 The code copies the full img.data array into buff1 without ensuring that the allocated size1 buffer is at least sizeof(img.data). (dvcp.c:58)
- CWE-415 buff1 is freed unconditionally and then freed again when size1 is even. (dvcp.c:62)
- CWE-416 After buff1 is freed, an alternate branch can write to buff1 when size1 is divisible by 3. (dvcp.c:67)
- CWE-191 Image dimensions read from the file are subtracted and offset in a signed int without validation, allowing underflow or negative values before allocation. (dvcp.c:74)
- CWE-120 The code copies the full img.data array into buff2 without ensuring that the allocated size2 buffer is at least sizeof(img.data). (dvcp.c:79)
- CWE-787 The code copies the full img.data array into buff4 even though buff4 was allocated with attacker-controlled size3 and may be smaller than sizeof(img.data). (dvcp.c:87)
- CWE-125 The computed size3 value is used as an index into a 10-byte stack buffer without bounds checking. (dvcp.c:90)
- CWE-674 stack_operation recursively calls itself in an infinite loop with a large stack buffer, causing stack exhaustion. (dvcp.c:25)
```

Your exact count and wording can differ. A valid report can contain zero findings. An empty report means that this run did not report any findings; it does not mean the program is safe. If you expected findings, check the provider reachability test and any Metis log output before judging the result.

## Compare the report with known defects

Display four source regions that the program identifies as deliberately vulnerable:

```bash
sed -n '20,28p' dvcp-review/dvcp.c
sed -n '51,68p' dvcp-review/dvcp.c
sed -n '72,83p' dvcp-review/dvcp.c
sed -n '89,108p' dvcp-review/dvcp.c
```

Check whether your report covers these concrete cases:

- Signed image dimensions are combined and passed to `malloc()` without overflow or range checks.
- `buff1` is freed, then freed again when `size1` is even or written after free when it is divisible by three.
- `img.height` is used as a divisor without a zero check.
- `size3` is used as an index into fixed-size and heap buffers without bounds checks.
- Attacker-controlled dimensions can select recursive stack exhaustion or repeated heap allocation.

During validation for this Learning Path, Metis v1.5.0 reported nine findings. This table shows how that run compared with the known defects in the teaching program:

| Source issue | Tested-run outcome |
| --- | --- |
| `size1` signed overflow before `malloc()` and `memcpy()` | Reported as `CWE-190` at `dvcp.c:54` |
| `memcpy()` into `buff1` without checking `size1` against `sizeof(img.data)` | Reported as `CWE-120` at `dvcp.c:58` |
| `buff1` double free | Reported as `CWE-415` at `dvcp.c:62` |
| `buff1` use-after-free write | Reported as `CWE-416` at `dvcp.c:67` |
| `size2` signed underflow or negative allocation size before `memcpy()` | Reported as `CWE-191` at `dvcp.c:74` |
| `memcpy()` into `buff2` without checking `size2` against `sizeof(img.data)` | Reported as `CWE-120` at `dvcp.c:79` |
| `buff4` allocation smaller than `memcpy()` length | Reported as `CWE-787` at `dvcp.c:87` |
| `size3` out-of-bounds stack-buffer read | Reported as `CWE-125` at `dvcp.c:90` |
| Recursive `stack_operation()` with a large stack buffer | Reported as `CWE-674` at `dvcp.c:25` |
| Divide by zero, indexed heap out-of-bounds read/write, indexed stack out-of-bounds write, memory leak, and heap exhaustion | Not reported in that run |

For each reported finding, verify the source location, attacker control, and operation. Also record known source defects that the run omitted. The goal is to practice reviewing Metis output, not to turn the finding count into a coverage score.

The same review is also available in `results/dvcp.sarif`. SARIF allows code-hosting services and security tools to associate findings with source locations. Keep JSON when you want the complete Metis reasoning and SARIF when you want to integrate results into an existing code-scanning workflow.

This shows that Metis can report several issues, but it is not guaranteed to find everything. Runs are non-deterministic and also depend on the model used.

## What you've accomplished and what's next

You ran a complete Metis review, exported two report formats, and compared the reported findings with known defects. Next, you will prepare a realistic libpng target without leaving benchmark canaries or fixes in its source.
