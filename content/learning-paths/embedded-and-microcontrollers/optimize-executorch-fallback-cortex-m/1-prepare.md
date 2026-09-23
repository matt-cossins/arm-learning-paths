---
title: Prepare the ExecuTorch CMSIS environment
weight: 2
description: Set up the pinned ExecuTorch 1.4.0, CMSIS-NN, Ethos-U, Arm GNU, FVP, and Docker environment used by this Learning Path.

### FIXED, DO NOT MODIFY
layout: learningpathall
---

## Understand what you will build

Before preparing the environment, it helps to understand how the model will run.
You will use the ExecuTorch ahead-of-time export flow to divide one model across
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
  -> output
```

The three execution paths and the ExecuTorch CMSIS Pack have different roles:

| Technology | Role in this Learning Path | Expected performance |
| --- | --- | --- |
| Ethos-U | Runs supported graph regions on the NPU. | Expected to provide the best performance and energy efficiency for supported neural-network operations. |
| CMSIS-NN | Supplies optimized Cortex-M kernels for supported quantized CPU operations that remain outside the NPU delegate. | Preferred CPU fallback when a matching CMSIS-NN-backed operator is available. |
| ExecuTorch portable kernels | Supply general CPU implementations for operations without an accelerated backend implementation. | Compatibility fallback rather than the preferred performance path. |
| ExecuTorch CMSIS Pack | Supplies versioned, selectable runtime, backend, and operator source components. | Packages the implementation; it does not provide acceleration by itself. |

The intended order is Ethos-U first, CMSIS-NN second, and portable kernels
last. This is an expected hierarchy rather than a guaranteed benchmark result.
Operator shapes, graph boundaries, memory movement, and quantize and dequantize
operations can affect end-to-end performance.

You will install the published source-based `PyTorch::ExecuTorch` CMSIS Pack,
select the matching backend and operator components in a CMSIS-Toolbox project,
and run the resulting executable on a Corstone-300 Fixed Virtual Platform
(FVP). The FVP validates functional execution, but it does not provide final
latency, memory, or power measurements for a physical device.

The following setup creates the pinned export, build, and simulation
environment used for that workflow.

## Check the host requirements

This Learning Path uses an ExecuTorch CMSIS environment pinned to ExecuTorch
`1.4.0` and Python `3.12`. The published ExecuTorch CMSIS Pack and the Python
exporter must use the same ExecuTorch version.

Use an arm64 Linux computer with at least `30 GB` of free storage. The host runs
the exporter and FVP, while Docker provides the CMSIS build environment. Install
[Docker](/install-guides/docker/) before continuing.

Ubuntu 24.04 LTS on arm64 is a good host option because it provides Python
`3.12` packages and supports Docker Engine on `arm64`. Other arm64 Linux
distributions can also work if they provide the required versions and tools.

Install the required host packages:

```bash
sudo apt update
sudo apt install -y \
  build-essential \
  pkg-config \
  libzstd-dev \
  python3.12 \
  python3.12-dev \
  python3.12-venv \
  git \
  curl \
  unzip
```

Check the host architecture, Python version, Docker server, and available disk
space:

```bash
uname -m
python3.12 --version
docker version --format '{{.Server.Arch}} {{.Server.Version}}'
df -h "$HOME"
```

Confirm the following results before continuing:

- `uname -m` reports `aarch64`.
- Python reports version `3.12`.
- The Docker server architecture is `arm64`.
- The home filesystem has at least `30 GB` available.

## Clone ExecuTorch 1.4.0

The checkout directory must be named `executorch`. Define the paths used by the
remaining setup stages, then clone the release tag:

```bash
export ET_ROOT=$HOME/executorch-1.4.0/executorch
export LP_WORKSPACE=$HOME/executorch-cmsis-lp
export RUNNER_DIR=$LP_WORKSPACE/pack-runner
export LP_ASSETS=https://raw.githubusercontent.com/ArmDeveloperEcosystem/arm-learning-paths/main/content/learning-paths/embedded-and-microcontrollers/optimize-executorch-fallback-cortex-m/files

mkdir -p "$(dirname "$ET_ROOT")" "$LP_WORKSPACE/artifacts"

git clone \
  --branch v1.4.0 \
  --depth 1 \
  --recurse-submodules \
  --shallow-submodules \
  https://github.com/pytorch/executorch.git \
  "$ET_ROOT"

git -C "$ET_ROOT" describe --tags --exact-match
```

The expected output is:

```output
v1.4.0
```

## Build the Python export environment

Create a Python `3.12` virtual environment inside the checkout:

```bash
cd "$ET_ROOT"
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools-scm
```

The exporter needs the Python backend modules and FlatBuffer schema tool. It
does not need a complete host runtime build, so the following options disable
unrelated backends, extensions, kernels, and tests.

```bash
export CMAKE_ARGS="\
-DEXECUTORCH_BUILD_COREML=OFF \
-DEXECUTORCH_BUILD_CUDA=OFF \
-DEXECUTORCH_BUILD_DEVTOOLS=OFF \
-DEXECUTORCH_BUILD_EXTENSION_DATA_LOADER=OFF \
-DEXECUTORCH_BUILD_EXTENSION_FLAT_TENSOR=OFF \
-DEXECUTORCH_BUILD_EXTENSION_LLM=OFF \
-DEXECUTORCH_BUILD_EXTENSION_LLM_RUNNER=OFF \
-DEXECUTORCH_BUILD_EXTENSION_MODULE=OFF \
-DEXECUTORCH_BUILD_EXTENSION_NAMED_DATA_MAP=OFF \
-DEXECUTORCH_BUILD_EXTENSION_RUNNER_UTIL=OFF \
-DEXECUTORCH_BUILD_EXTENSION_TENSOR=OFF \
-DEXECUTORCH_BUILD_EXTENSION_TRAINING=OFF \
-DEXECUTORCH_BUILD_KERNELS_CUSTOM_AOT=OFF \
-DEXECUTORCH_BUILD_KERNELS_LLM=OFF \
-DEXECUTORCH_BUILD_KERNELS_LLM_AOT=OFF \
-DEXECUTORCH_BUILD_KERNELS_OPTIMIZED=OFF \
-DEXECUTORCH_BUILD_KERNELS_QUANTIZED=OFF \
-DEXECUTORCH_BUILD_KERNELS_QUANTIZED_AOT=OFF \
-DEXECUTORCH_BUILD_MLX=OFF \
-DEXECUTORCH_BUILD_OPENVINO=OFF \
-DEXECUTORCH_BUILD_PORTABLE_OPS=OFF \
-DEXECUTORCH_BUILD_PYBIND=OFF \
-DEXECUTORCH_BUILD_QNN=OFF \
-DEXECUTORCH_BUILD_TESTS=OFF \
-DEXECUTORCH_BUILD_VULKAN=OFF \
-DEXECUTORCH_BUILD_XNNPACK=OFF \
-DEXECUTORCH_BUILD_CMSIS_NN_PYBINDS=OFF"
export CMAKE_BUILD_ARGS="--target flatbuffers_ep"

CMAKE_BUILD_PARALLEL_LEVEL=2 \
  ./install_executorch.sh --optional-dependency ethos_u

unset CMAKE_ARGS CMAKE_BUILD_ARGS
```

Install the CMSIS-NN Python binding at the revision pinned by ExecuTorch
`1.4.0`:

```bash
python -m pip install \
  "scikit-build-core<0.8" \
  pybind11 \
  pyproject-metadata \
  pathspec

python -m pip install --no-build-isolation \
  "git+https://github.com/ARM-software/CMSIS-NN.git@dbf45dbfcc515421dd6099037d3e2637b90748c8"
```

Confirm that the exporter dependencies can be imported:

```bash
python - <<'PY'
import cmsis_nn
import executorch.backends.arm
import executorch.backends.cortex_m
from executorch.exir import to_edge

print("ExecuTorch 1.4.0 CMSIS Python imports passed")
PY
```

The expected output is:

```output
ExecuTorch 1.4.0 CMSIS Python imports passed
```

## Install the Arm tools

The ExecuTorch Arm setup installs the Arm GNU toolchain, Ethos-U software, and
Corstone-300 FVP. Review the Arm license terms before using the acceptance
option:

```bash
cd "$ET_ROOT"
source .venv/bin/activate
examples/arm/setup.sh --i-agree-to-the-contained-eula
source examples/arm/arm-scratch/setup_path.sh
```

Confirm that the compiler and FVP are available:

```bash
arm-none-eabi-gcc --version | head -n 1
command -v FVP_Corstone_SSE-300_Ethos-U55
```

## Fetch the Corstone platform sources

The ExecuTorch CMSIS Pack supplies the runtime, backends, and operators. The
runner also needs the Corstone target, UART, mailbox, timing, and startup
sources from the Ethos-U SDK. These are board and simulator support files, not
ExecuTorch runtime components.

Fetch the `26.02` Ethos-U release used by ExecuTorch `1.4.0`, then apply the
platform patches supplied in the ExecuTorch checkout. `fetch_externals.py`
retrieves the SDK repositories listed by that release, while `patch_repo`
applies the compatibility changes expected by the ExecuTorch example:

```bash
cd "$ET_ROOT"
source .venv/bin/activate

ETHOS_SDK="$ET_ROOT/examples/arm/arm-scratch/ethos-u"
PATCH_DIR="$ET_ROOT/examples/arm/ethos-u-setup"

if [ ! -d "$ETHOS_SDK/.git" ]; then
  git clone \
    --branch 26.02 \
    --depth 1 \
    https://git.gitlab.arm.com/artificial-intelligence/ethos-u/ethos-u.git \
    "$ETHOS_SDK"
fi

source backends/arm/scripts/utils.sh
patch_repo "$ETHOS_SDK" 26.02 "$PATCH_DIR"

cd "$ETHOS_SDK"
python fetch_externals.py -c 26.02.json fetch

cd "$ET_ROOT"
patch_repo "$ETHOS_SDK/core_software" 26.02 "$PATCH_DIR"
patch_repo "$ETHOS_SDK/core_platform" 26.02 "$PATCH_DIR"

test -f "$ETHOS_SDK/core_platform/targets/corstone-300/target.cpp"
test -f "$ETHOS_SDK/core_software/Cortex_DFP/Device/ARMCM55/Source/startup_ARMCM55.c"
echo "Ethos-U Corstone platform sources prepared"
```

The expected final output is:

```output
Ethos-U Corstone platform sources prepared
```

This stage downloads platform support only. The embedded application still
compiles the ExecuTorch runtime, Ethos-U backend, and selected operators from
the published ExecuTorch CMSIS Pack.

## Save the workspace settings

Save the paths so each later page can restore them in a new shell:

```bash
cat > "$LP_WORKSPACE/env.sh" <<'EOF'
export ET_ROOT="$HOME/executorch-1.4.0/executorch"
export LP_WORKSPACE="$HOME/executorch-cmsis-lp"
export RUNNER_DIR="$HOME/executorch-cmsis-lp/pack-runner"
export LP_ASSETS="https://raw.githubusercontent.com/ArmDeveloperEcosystem/arm-learning-paths/main/content/learning-paths/embedded-and-microcontrollers/optimize-executorch-fallback-cortex-m/files"
EOF

source "$LP_WORKSPACE/env.sh"
cd "$LP_WORKSPACE"
curl -O "$LP_ASSETS/export_cortex_m_fallback.py"
```

## What you've accomplished and what's next

You have prepared the pinned ExecuTorch CMSIS environment and a separate model
export workspace.

Next, you will inspect how CMSIS-NN and portable kernels divide Cortex-M work
before adding the Ethos-U delegate.
