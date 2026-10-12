---
title: Inspect the published ExecuTorch CMSIS Pack
weight: 5
description: Download the published ExecuTorch 1.4.0 CMSIS Pack and inspect the runtime, backend, and operator components used by the model.

### FIXED, DO NOT MODIFY
layout: learningpathall
---

## Understand the ExecuTorch CMSIS Pack benefits

The ExecuTorch CMSIS Pack is a source pack rather than a prebuilt runtime
library. It supplies the ExecuTorch runtime, registration code, backends, and
operators as selectable CMSIS components.

A `.pack` file is a ZIP-compatible archive. Its Pack Description file, or
PDSC, records component names, source files, dependencies, versions, and
conditions. CMSIS-Toolbox reads this metadata to turn component selections in a
project into a concrete build.

A CMSIS project can select only the components required by its lowered graph
instead of maintaining one large source list. The selected source files then
compile with the application's target compiler and options.

The published pack also gives CMSIS-Toolbox and Keil Studio a versioned package
identifier: `PyTorch::ExecuTorch@1.4.0`. This allows the tools to download the
same package, resolve its dependencies, expose its components in an IDE, and
record the selected version without a local pack-building stage.

## Download the published pack

Download the pack attached to the ExecuTorch `1.4.0` release:

```bash
source ~/executorch-cmsis-lp/env.sh

PACK_DIR="$LP_WORKSPACE/packs"
PACK_FILE="$PACK_DIR/PyTorch.ExecuTorch.1.4.0.pack"

mkdir -p "$PACK_DIR"

curl --location --fail \
  --output "$PACK_FILE" \
  https://github.com/pytorch/executorch/releases/download/v1.4.0/PyTorch.ExecuTorch.1.4.0.pack

unzip -t "$PACK_FILE" >/dev/null && \
  echo "ExecuTorch CMSIS Pack archive passed"
```

The expected final output is:

```output
ExecuTorch CMSIS Pack archive passed
```

This copy is used only to inspect the archive and its component metadata. The
final build installs the same pack through the public pack index into a clean
pack root. That separate installation checks the normal CMSIS dependency and
component-resolution workflow.

## Inspect the components used by the model

Display the PDSC components that correspond to the partially delegated graph:

```bash
unzip -p "$PACK_FILE" PyTorch.ExecuTorch.pdsc | \
grep '<component ' | \
grep -E 'Csub="(Runtime|Kernel Utils|Kernel Registration|Backend EthosU|Cortex-M (quantize_per_tensor|dequantize_per_tensor|quantized_conv2d)|Portable topk)"' | \
sed -E 's/.*Csub="([^"]+)".*Cversion="([^"]+)".*/\1 \2/'
```

The output includes:

```output
Runtime 1.4.0
Kernel Utils 1.4.0
Kernel Registration 1.4.0
Portable topk 1.4.0
Cortex-M dequantize_per_tensor 1.4.0
Cortex-M quantize_per_tensor 1.4.0
Cortex-M quantized_conv2d 1.4.0
Backend EthosU 1.4.0
```

The pack contains the exact runtime, Ethos-U backend, CMSIS-NN-backed Cortex-M
operators, and portable operator needed by this model. The next page selects
these components in a CMSIS project. This graph-to-component mapping is the
main integration benefit: the exported targets tell you what the embedded build
must include.

## What you've accomplished and what's next

You have downloaded the published ExecuTorch CMSIS Pack and matched its
components to the lowered graph.

Next, you will prepare a Corstone-300 project that selects these components and
embeds the exported model.
