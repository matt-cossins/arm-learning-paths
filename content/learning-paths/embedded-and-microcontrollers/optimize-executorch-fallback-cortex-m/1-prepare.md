---
title: Prepare the Corstone-300 U55 project
weight: 2
description: Set up the reusable CMSIS-Executorch project and its pinned Python and Arm tool environments.

### FIXED, DO NOT MODIFY
layout: learningpathall
---

## Understand the execution plan

You will start with a small PyTorch model and export it as an ExecuTorch
program (`.pte`).

On the target, the Cortex-M CPU runs the ExecuTorch runtime and coordinates
the whole program. The CPU reads the `.pte` and dispatches different parts 
to either the Ethos-U NPU or to CPU kernels. You will use the ExecuTorch ahead-of-time export flow to divide one model across
three execution paths:

- A stride-one convolution that Ethos-U55 accepts.
- A stride-four convolution that Ethos-U55 rejects but CMSIS-NN supports.
- A `topk` operation that remains an ExecuTorch portable FP32 operation.

After Ethos-U partitioning and Cortex-M lowering, the graph follows this path:

```text
input
  -> Ethos-U55 delegated convolution
  -> Cortex-M quantized operator using CMSIS-NN
  -> portable FP32 topk
output
```

The three execution paths have different roles:

| Technology | Role in this Learning Path | Expected performance |
| --- | --- | --- |
| Ethos-U | Runs supported graph regions on the NPU. (eg: Stride-1 convolution) | Expected to provide the best performance and energy efficiency for supported neural-network operations. |
| [CMSIS-NN](https://arm-software.github.io/CMSIS-NN/latest/index.html) | Supplies optimized Cortex-M kernels for quantized CPU operations that are unsupported by the NPU. (eg: Stride-4 convolution) | Preferred CPU fallback when a matching CMSIS-NN-backed operator is available. |
| ExecuTorch portable kernels | Supply general CPU implementations for operations without an accelerated backend implementation. (eg: `topk` operation) | Compatibility fallback rather than the preferred performance path. |

Fallback here is planned during export. It isn't recovery from an NPU failure
at runtime. The exporter determines which regions the target Ethos-U delegate
supports, then assigns known remaining patterns to the Cortex-M backend.

{{% notice Why this example uses Ethos-U55 %}}
Ethos-U55 is used because its unsupported stride-four convolution creates a
predictable fallback region. Ethos-U85 supports more operator configurations,
so it will typically have less CPU fallback than U55. The same workflow still
applies when a model contains operations that remain outside the U85 delegate.
{{% /notice %}}

In this Learning Path, you will clone a CMSIS-Executorch example that already contains the needed board support,
runner, memory configuration, and Fixed Virtual Platform (FVP) settings. You
will then inspect and modify that to observe Cortex-M fallback using optimized CMSIS-NN microkernels.

## Clone the example project

Clone the CMSIS-Executorch project used by this Learning Path:

```console
git clone --branch add-corstone-300-u55 https://github.com/Kwash45/CMSIS-Executorch.git
cd CMSIS-Executorch
git checkout 173c251496446b8f564c178c415e6f7f28081070
```

The explicit checkout pins the project to a revision that has been tested and validated.

## Install vcpkg and Activate the project tools

The repository's `vcpkg-configuration.json` declares CMSIS-Toolbox, Arm
Compiler for Embedded, and the Arm FVP.  Install `vcpkg` with the command for your host:

{{< tabpane code=true >}}
  {{< tab header="Linux" language="bash">}}
. <(curl https://github.com/microsoft/vcpkg-tool/releases/download/2026-04-08/vcpkg-init.sh -L)
  {{< /tab >}}
  {{< tab header="Windows PowerShell" language="powershell">}}
iex (iwr -useb https://github.com/microsoft/vcpkg-tool/releases/download/2026-04-08/vcpkg-init.ps1)
  {{< /tab >}}
{{< /tabpane >}}

Initialize `vcpkg`, then activate it from the repository root. Repeat these commands in each new terminal you open.

{{< tabpane code=true >}}
  {{< tab header="Linux" language="bash">}}
. ~/.vcpkg/vcpkg-init
vcpkg-shell activate
  {{< /tab >}}
  {{< tab header="Windows PowerShell" language="powershell">}}
. "$env:USERPROFILE\.vcpkg\vcpkg-init.ps1"
vcpkg-shell activate
  {{< /tab >}}
{{< /tabpane >}}

The first activation downloads any missing tools. Later activations reuse the
installed versions.

If you don't already have a suitable Arm Compiler for Embedded license,
activate the free, non-commercial Keil MDK Community license:

```console
armlm activate -product KEMDK-COM0 -server https://mdk-preview.keil.arm.com
```

## Create the Python environment

Use the repository's setup wrapper to create `.venv` and install its pinned
export dependencies:

{{< tabpane code=true >}}
  {{< tab header="Linux" language="bash">}}
./setup_venv.sh
  {{< /tab >}}
  {{< tab header="Windows PowerShell" language="powershell">}}
.\setup_venv.bat
  {{< /tab >}}
{{< /tabpane >}}

## Verify the environment

The Python package and CMSIS Pack versions must match because the embedded
runtime loads the program produced by the exporter. Check the host tools, Arm
build tools, and Python packages:

{{< tabpane code=true >}}
  {{< tab header="Linux" language="bash">}}
git --version
python3 --version
cbuild --version
armclang --version
.venv/bin/python -c "from importlib.metadata import version; print('ExecuTorch', version('executorch')); print('PyTorch', version('torch'))"
  {{< /tab >}}
  {{< tab header="Windows PowerShell" language="powershell">}}
git --version
python --version
cbuild --version
armclang --version
.\.venv\Scripts\python.exe -c "from importlib.metadata import version; print('ExecuTorch', version('executorch')); print('PyTorch', version('torch'))"
  {{< /tab >}}
{{< /tabpane >}}

Your Git version can vary. Confirm that Python is between 3.10 and 3.13,
`cbuild` reports 2.14.0, Arm Compiler for Embedded reports 6.24, and the final
two lines are:

```output
ExecuTorch 1.5.1
PyTorch 2.14.0
```

## Download the Learning Path assets

Download the fallback model, focused integration patch, and two inspection
helpers into the repository root:

{{< tabpane code=true >}}
  {{< tab header="Linux" language="bash">}}
LP_ASSETS=https://raw.githubusercontent.com/ArmDeveloperEcosystem/arm-learning-paths/main/content/learning-paths/embedded-and-microcontrollers/optimize-executorch-fallback-cortex-m/files

curl -fLO "$LP_ASSETS/mixed_backend_cnn.py"
curl -fLO "$LP_ASSETS/enable_cortex_m_fallback.patch"
curl -fLO "$LP_ASSETS/export_cortex_m_fallback.py"
curl -fLO "$LP_ASSETS/verify_pack_sources.py"
  {{< /tab >}}
  {{< tab header="Windows PowerShell" language="powershell">}}
$lpAssets = "https://raw.githubusercontent.com/ArmDeveloperEcosystem/arm-learning-paths/main/content/learning-paths/embedded-and-microcontrollers/optimize-executorch-fallback-cortex-m/files"

curl.exe -fLO "$lpAssets/mixed_backend_cnn.py"
curl.exe -fLO "$lpAssets/enable_cortex_m_fallback.patch"
curl.exe -fLO "$lpAssets/export_cortex_m_fallback.py"
curl.exe -fLO "$lpAssets/verify_pack_sources.py"
  {{< /tab >}}
{{< /tabpane >}}

Each file will be explained in greater detail in subsequent pages.

## What you've accomplished and what's next

You now have a pinned Corstone-300 U55 project, its matching Python packages,
and its versioned Arm tools. The project already owns the board and application
integration that previously needed many manual setup steps.

Next, you will establish a CPU-only baseline before adding
Ethos-U delegation on the U55 demonstration target.
