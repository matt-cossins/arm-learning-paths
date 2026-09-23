---
title: Triage a libpng finding
description: Check a Metis report finding against source code, attacker control, and the Magma ground-truth diff.
weight: 6
layout: "learningpathall"
---

## List the reported findings

Metis reports findings, reasoning, source locations, and mitigations. This page adds a manual triage workflow: you compare a finding with source code, attacker control, build assumptions, and the Magma diff before treating it as confirmed.

Select the report you want to summarize:

{{< tabpane-normal >}}
  {{< tab header="Live report" >}}
Use this option if you ran the live review and want to inspect its results first:

```bash
REPORT=results/libpng-live.json
```
  {{< /tab >}}
  {{< tab header="Captured report" >}}
Use this option for the guided row-factor triage, or if your live review returned no findings:

```bash
REPORT=results/libpng-review-candidate.json
```
  {{< /tab >}}
{{< /tabpane-normal >}}

Print a compact summary:

```bash
python - "$REPORT" <<'PY'
import json
import sys
from pathlib import Path

data = json.loads(Path(sys.argv[1]).read_text())
for review_group in data["reviews"]:
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
            f"{finding['severity']:>6} {finding['cwe']}: "
            f"{finding['issue']} "
            f"({file_path}:{line})"
        )
PY
```

If you selected the captured report, the expected output is:

```output
Medium CWE-369: Externally controlled image dimensions can trigger division by zero in IDAT chunk length validation (pngrutil.c:3163)
```

The pre-provided report contains one medium-severity finding in `pngrutil.c`: a possible division by zero after a row-size value is narrowed. If the summary from your live report includes a similar row-factor or division-by-zero finding in `pngrutil.c`, you can continue with the live report. Otherwise, set `REPORT=results/libpng-review-candidate.json` and use the captured report for the guided triage.

## Triage the row-factor finding

DVCP taught the mechanics of running Metis and reading a report. The prepared libpng tree is the more realistic example: you need to inspect the reported source region, check whether values parsed from the PNG file can influence the operation (attacker-controlled values), and compare the region with the prepared-source diff.

For this finding, you are checking four things:

1. Does the reported source location contain the operation Metis described?
2. Can PNG-controlled fields influence the value?
3. Can the narrowing conversion produce a zero divisor?
4. Does the source region overlap a known vulnerability introduced by the Magma preparation?

First, display the reported source region:

```bash
sed -n '3155,3180p' libpng-review/pngrutil.c
```

Next, inspect the prepared-source diff around the same expression:

```bash
git -C libpng-review diff -U8 -- pngrutil.c | sed -n '/row_factor_l/,+24p'
```

Use the report, source region, and diff to decide whether this is a credible finding:

1. `png_ptr->width`, channel count, bit depth, and interlace state originate from the parsed PNG.
2. The arithmetic is performed in `size_t`, then narrowed to `png_uint_32`.
3. A sufficiently large row factor can wrap to zero during the narrowing conversion.
4. The narrowed value is used as a divisor before a zero check.
5. The changed lines overlap a Magma-introduced vulnerability in the prepared-source diff.

This is a strong match to the known vulnerable change in the prepared libpng target. Metis identified the relevant operation, explained attacker control, and proposed avoiding the narrowing conversion or checking the value before division. The triage decision is therefore **confirmed for this exercise target**.

## Triage additional live findings

Your live run might return no findings, the row-factor finding, or different findings. An empty report does not prove the target is safe. A finding outside the injected changes is not automatically false, but it is not evidence by itself that Metis discovered a new vulnerability.

Classify each additional finding as **unconfirmed** until you complete more work:

- Check the relevant file-format specification and API contracts.
- Trace callers and helper functions to find earlier validation or cleanup behavior.
- Check whether build configuration makes the code reachable.
- Create a focused reproducer and observe behavior under AddressSanitizer and UndefinedBehaviorSanitizer.
- Search upstream issues and security advisories before reporting a new vulnerability.

## Record a triage decision

For each finding, record at least:

- Status: confirmed, rejected, duplicate, accepted risk, or unconfirmed.
- Attacker-controlled input and the path to the operation.
- Relevant build and platform assumptions.
- Reproduction evidence or the missing evidence needed next.
- Proposed fix owner and test coverage.

Do not publish unverified findings against active open-source projects. Follow the project's security policy and coordinated-disclosure process if further investigation confirms an issue.

## What you've accomplished and what's next

You installed Metis, compared a review with known C defects, prepared a realistic benchmark target, and checked a Metis finding against source evidence. You can apply the same workflow to a bounded directory, file, or patch in your own C project, or for other languages.
