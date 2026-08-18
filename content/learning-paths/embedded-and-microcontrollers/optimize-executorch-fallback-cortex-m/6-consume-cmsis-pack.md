---
title: Build and run the ExecuTorch CMSIS Pack application
weight: 7
description: Build a Corstone-300 executable from ExecuTorch, CMSIS-NN, and Ethos-U CMSIS components, then run the model on an Ethos-U55 FVP.

### FIXED, DO NOT MODIFY
layout: learningpathall
---

## Build the executable from ExecuTorch CMSIS Pack components

Build the application in the arm64 AVH-MLOps container. The command:

- Mounts the ExecuTorch checkout as a read-only input.
- Activates the CMSIS-Toolbox utilities supplied by the container.
- Installs `PyTorch::ExecuTorch@1.4.0` from the pack index into a clean pack root.
- Runs `cbuild` for the Corstone-300 release context.

The temporary `CMSIS_PACK_ROOT` is intentionally empty at the start. A
successful build therefore shows that the project can resolve its declared
packs, rather than relying on packages left by an earlier build.

```bash
source ~/executorch-cmsis-lp/env.sh
cd "$RUNNER_DIR"

DOCKER_IMAGE="ghcr.io/arm-software/avh-mlops/arm-mlops-docker-licensed-community:latest-arm64"

chmod a+rwx "$RUNNER_DIR"

docker run --rm \
  -v "$RUNNER_DIR:/workspace" \
  -v "$ET_ROOT:/workspace/executorch:ro" \
  "$DOCKER_IMAGE" \
  bash -lc '
set -euo pipefail
cd /workspace

export Z_VCPKG_POSTSCRIPT="$(mktemp /tmp/vcpkg.XXXXXX.sh)"
vcpkg activate
source "$Z_VCPKG_POSTSCRIPT"

export CMSIS_PACK_ROOT=/tmp/cmsis-pack-root
cpackget init https://www.keil.com/pack/index.pidx
cpackget add --agree-embedded-license PyTorch::ExecuTorch@1.4.0

cbuild pack_runner.csolution.yml \
  --packs \
  --update-rte \
  --context pack_runner.Release+Corstone-300
'
```

In the command, `cpackget init` configures the public pack index and
`cpackget add` installs the selected ExecuTorch pack. `cbuild --packs` resolves
declared pack dependencies, `--update-rte` regenerates the run-time environment
files, and `--context` selects the project, build type, and target combination
defined by the solution.

{{% notice Note %}}
The generated `pack_runner.csolution.yml` and `pack_runner.cproject.yml` files
can also be opened with the Arm CMSIS Solution extension included in the
[Arm Keil Studio Pack](https://marketplace.visualstudio.com/items?itemName=Arm.keil-studio-pack)
for Visual Studio Code. Use the graphical view to inspect the selected target,
build context, packs, and software components.
{{% /notice %}}

The first build downloads the arm64 AVH-MLOps container, CMSIS-Toolbox compiler
tools, the ExecuTorch CMSIS Pack, and its dependent packs. The final build
summary is:

```output
Build summary: 1 succeeded, 0 failed
```

{{% notice Note %}}
GNU `ld` can print allocation warnings for the Corstone multi-segment linker
script before the successful build summary. The generated ELF is validated in
the next section on the FVP.
{{% /notice %}}

The executable is written to:

```text
$RUNNER_DIR/out/pack_runner/Corstone-300/Release/pack_runner.elf
```

## Confirm that the build used the pack

Run the verification helper against the generated compilation database. It
checks that the runtime, CMSIS-NN-backed Cortex-M operator, Ethos-U backend, and
portable `topk` sources came from the installed pack:

```bash
COMPILE_DB=out/pack_runner/Corstone-300/Release/compile_commands.json
python verify_pack_sources.py "$COMPILE_DB"
```

The expected output is:

```output
PASS: ExecuTorch runtime came from the ExecuTorch CMSIS Pack
PASS: CMSIS-NN Cortex-M convolution came from the ExecuTorch CMSIS Pack
PASS: Ethos-U backend came from the ExecuTorch CMSIS Pack
PASS: Portable topk came from the ExecuTorch CMSIS Pack
```

Each `PASS` confirms that one required ExecuTorch source file appears in the
compilation database under the installed pack path. The application
and Corstone platform sources come from the ExecuTorch checkout. A
successful build confirms that an ELF was produced; this additional check
confirms that the selected ExecuTorch components were resolved from the pack.

## Run the pack-built model on the FVP

Run the `cbuild` output on the Corstone-300 Ethos-U55 FVP:

```bash
source "$ET_ROOT/examples/arm/arm-scratch/setup_path.sh"

"$ET_ROOT/backends/arm/scripts/run_fvp.sh" \
  --elf="$RUNNER_DIR/out/pack_runner/Corstone-300/Release/pack_runner.elf" \
  --target=ethos-u55-128
```

The relevant output is:

```output
PTE Model data loaded. Size: 5476 bytes.
NPU delegations: 1 (1.00 per inference)
Output[0][0]: (float) 0.030337
Output[0][1]: (float) -0.034964
Program complete, exiting.
No problems found!
```

The graph summary from the export step identifies the stride-four convolution
as `cortex_m.quantized_conv2d` and `topk` as portable. The compilation database
shows that the matching Cortex-M and portable sources came from the ExecuTorch
CMSIS Pack. The FVP output confirms that the complete pack-built application
loaded and ran the same partially delegated program with one Ethos-U delegation.

## What you've accomplished

You have run an ExecuTorch model built from the ExecuTorch CMSIS Pack on a
Corstone-300 system. The application delegates the supported convolution to
Ethos-U55, executes the unsupported stride-four convolution through the
CMSIS-NN-backed Cortex-M operator, and finishes with a portable FP32 operator.

CMSIS-NN provides the optimized CPU implementation for the quantized fallback
convolution. The ExecuTorch CMSIS Pack provides versioned, component-based
integration for the matching runtime, backend, and operator sources. The clean
CMSIS build and compilation-database checks make that software composition
visible and repeatable.

For another model, inspect its lowered graph, select the matching components
from the ExecuTorch CMSIS Pack, regenerate `model_pte.h`, and rebuild the CMSIS
project.
