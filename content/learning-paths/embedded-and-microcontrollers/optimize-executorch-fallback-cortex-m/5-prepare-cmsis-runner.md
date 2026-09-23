---
title: Prepare a Corstone-300 runner with the ExecuTorch CMSIS Pack
weight: 6
description: Generate the embedded model and Corstone-300 linker assets for an executable built from components in the ExecuTorch CMSIS Pack.

### FIXED, DO NOT MODIFY
layout: learningpathall
---

## Create the CMSIS runner workspace

The ExecuTorch CMSIS Pack supplies the runtime, Ethos-U backend, CMSIS-NN
operators, portable operators, and registration sources. The application still
needs a model, a board memory map, and Corstone-300 platform support.

CMSIS describes the build in two files. The solution file selects the target,
compiler, build type, packs, and project. The project file selects software
components and combines them with application and platform sources. Separating
these concerns lets the same project be reused with another solution context.

Create a runner directory and download the pack-source verification helper:

```bash
source ~/executorch-cmsis-lp/env.sh

mkdir -p "$RUNNER_DIR"
cd "$RUNNER_DIR"

curl -O "$LP_ASSETS/verify_pack_sources.py"

cp "$ET_ROOT/backends/arm/cmsis_pack/test/smoke/vcpkg-configuration.json" .
```

Create `uart_config.h` with the Corstone-300 UART settings used by the runner:

```bash
cat > uart_config.h <<'EOF'
#pragma once

#define UART0_BASE        (0x49303000)
#define UART0_BAUDRATE    (115200)
#define SYSTEM_CORE_CLOCK (25000000)
EOF
```

## Define the CMSIS solution and project

Create `pack_runner.csolution.yml`. This file selects the compiler, target,
build type, project, and pack versions:

```bash
cat > pack_runner.csolution.yml <<'YAML'
solution:
  created-for: CMSIS-Toolbox@2.13.0
  cdefault:
  compiler: GCC@14.3.1

  packs:
    - pack: ARM::CMSIS@>=6.0.0
    - pack: ARM::CMSIS-NN@7.0.0
    - pack: ARM::Cortex_DFP@>=1.1.0
    - pack: ARM::ethos-u-core-driver@1.26.2
    - pack: PyTorch::ExecuTorch@1.4.0

  target-types:
    - type: Corstone-300
      device: ARM::ARMCM55

  build-types:
    - type: Release
      optimize: speed

  projects:
    - project: ./pack_runner.cproject.yml
YAML
```

Create `pack_runner.cproject.yml`. The `components` section selects the
ExecuTorch, CMSIS-NN, Ethos-U, Cortex-M, and portable components used by the
lowered model. These selections come directly from the target names observed on
the previous pages. The remaining sections configure and build the runner
around those components:

```bash
cat > pack_runner.cproject.yml <<'YAML'
project:
  packs:
    - pack: PyTorch::ExecuTorch@1.4.0

  output:
    base-name: pack_runner
    type:
      - elf
      - map

  linker:
    - script: ./platform.ld
      for-compiler: GCC

  components:
    - component: ARM::CMSIS:CORE
    - component: ARM::CMSIS:NN Lib
    - component: ARM::Machine Learning:NPU Support:Ethos-U Driver&Generic U55
    - component: Machine Learning:ExecuTorch:Runtime
    - component: Machine Learning:ExecuTorch:Kernel Utils
    - component: Machine Learning:ExecuTorch:Kernel Registration
    - component: Machine Learning:ExecuTorch:Backend EthosU
    - component: Machine Learning:ExecuTorch Operators:Cortex-M quantize_per_tensor
    - component: Machine Learning:ExecuTorch Operators:Cortex-M dequantize_per_tensor
    - component: Machine Learning:ExecuTorch Operators:Cortex-M quantized_conv2d
    - component: Machine Learning:ExecuTorch Operators:Portable topk

  add-path:
    - .
    - ./executorch/examples/arm/executor_runner
    - ./executorch/examples/arm/arm-scratch/ethos-u/core_platform/targets/common/include
    - ./executorch/examples/arm/arm-scratch/ethos-u/core_platform/drivers/mpu/include
    - ./executorch/examples/arm/arm-scratch/ethos-u/core_platform/drivers/timing_adapter/include
    - ./executorch/examples/arm/arm-scratch/ethos-u/core_platform/drivers/uart/include
    - ./executorch/examples/arm/arm-scratch/ethos-u/core_platform/drivers/mailbox/include
    - ./executorch/examples/arm/arm-scratch/ethos-u/core_platform/drivers/mhu_dummy/include
    - ./executorch/examples/arm/arm-scratch/ethos-u/core_software/Cortex_DFP/Device/ARMCM55/Include
    - ./executorch/examples/arm/arm-scratch/ethos-u/core_software/cmsis_6/CMSIS/Core/Include

  define:
    - ETHOSU
    - ETHOSU55
    - ETHOSU_HAS_TA
    - ET_COMPILED_PTE
    - ET_LOG_DUMP_OUTPUT

  misc:
    - for-compiler: GCC
      C-CPP:
        - -includeARMCM55.h
        - -DARM_NN_ENABLE_F16=0
        - -DARM_NN_ENABLE_F32=0
        - -DCMSIS_VER=6
        - -DETHOSU_ARENA=1
        - -DETHOSU_MACS=128
        - -DETHOSU_MODEL=1
        - -DET_ARM_BAREMETAL_SCRATCH_TEMP_ALLOCATOR_POOL_SIZE=0x200000
        - -DET_NUM_INFERENCES=1
      C:
        - -std=gnu11
      CPP:
        - -std=gnu++17
        - -fno-unwind-tables
        - -fno-rtti
        - -fno-exceptions
      Link:
        - -Wl,-u,_printf_float

  groups:
    - group: Application
      files:
        - file: ./executorch/examples/arm/executor_runner/arm_executor_runner.cpp
        - file: ./executorch/examples/arm/executor_runner/arm_memory_allocator.cpp
        - file: ./executorch/examples/arm/executor_runner/arm_perf_monitor.cpp
        - file: ./executorch/extension/runner_util/inputs.cpp
        - file: ./executorch/extension/runner_util/inputs_portable.cpp
    - group: Corstone-300
      files:
        - file: ./executorch/examples/arm/arm-scratch/ethos-u/core_platform/targets/common/src/init.cpp
        - file: ./executorch/examples/arm/arm-scratch/ethos-u/core_platform/targets/corstone-300/target.cpp
        - file: ./executorch/examples/arm/arm-scratch/ethos-u/core_platform/targets/corstone-300/retarget.c
        - file: ./executorch/examples/arm/arm-scratch/ethos-u/core_platform/drivers/mpu/src/mpu.cpp
        - file: ./executorch/examples/arm/arm-scratch/ethos-u/core_platform/drivers/timing_adapter/src/timing_adapter.c
        - file: ./executorch/examples/arm/arm-scratch/ethos-u/core_platform/drivers/uart/src/uart_cmsdk_apb.c
        - file: ./executorch/examples/arm/arm-scratch/ethos-u/core_platform/drivers/mailbox/src/mailbox.cpp
        - file: ./executorch/examples/arm/arm-scratch/ethos-u/core_platform/drivers/mhu_dummy/src/mhu_dummy.cpp
        - file: ./executorch/examples/arm/arm-scratch/ethos-u/core_software/Cortex_DFP/Device/ARMCM55/Source/system_ARMCM55.c
        - file: ./executorch/examples/arm/arm-scratch/ethos-u/core_software/Cortex_DFP/Device/ARMCM55/Source/startup_ARMCM55.c
YAML
```

### How the CMSIS project file is structured

The CMSIS project file combines components installed from packs with application
and platform sources from the ExecuTorch checkout:

| YAML section | Purpose |
| --- | --- |
| `packs` | Pins the project to `PyTorch::ExecuTorch@1.4.0`. |
| `output` and `linker` | Select the ELF and map outputs and the generated Corstone-300 linker script. |
| `components` | Select CMSIS Core, CMSIS-NN, the Ethos-U55 driver, ExecuTorch runtime support, and only the operators required by the lowered graph. |
| `add-path` | Adds headers for the runner and Corstone-300 platform sources mounted from the ExecuTorch checkout. |
| `define` and `misc` | Configure the Ethos-U55 target, embedded `.pte` data, logging, memory allocation, inference count, and compiler options. |
| `groups` | Adds the runner and Corstone-300 source files that form the application around the pack components. |

The `components` section connects the lowered graph to the embedded build. It
selects the required CPU and NPU implementations from the pinned ExecuTorch
`1.4.0` pack instead of maintaining a source list manually. The entries under
`groups` remain application and platform code; they are not supplied by the
pack.

## Embed the exported program

Convert the partially delegated `.pte` file to a C array. The linker places this
array in the Corstone-300 DDR model section:

```bash
cd "$RUNNER_DIR"
source "$ET_ROOT/.venv/bin/activate"

python "$ET_ROOT/examples/arm/executor_runner/pte_to_header.py" \
  --pte "$LP_WORKSPACE/artifacts/stride4_ethos_u_fallback.pte" \
  --outdir "$RUNNER_DIR"
```

The expected output includes:

```output
Section: network_model_sec.
```

The `.pte` file is the serialized ExecuTorch program produced by the exporter.
Converting it to `model_pte.h` makes the program part of the firmware image, so
the bare-metal runner does not need a filesystem or external model loader.

## Generate the Corstone-300 linker script

Preprocess the ExecuTorch linker template with the Arm GNU compiler:

```bash
source "$ET_ROOT/examples/arm/arm-scratch/setup_path.sh"

arm-none-eabi-gcc -E -x c -P \
  -o "$RUNNER_DIR/platform.ld" \
  "$ET_ROOT/examples/arm/executor_runner/Corstone-300.ld"

ls -lh "$RUNNER_DIR/model_pte.h" "$RUNNER_DIR/platform.ld"
```

`model_pte.h` embeds the model. `platform.ld` places code, the model, the method
allocator, and the CMSIS-NN scratch arena in memory regions available on the
Corstone-300 FVP. Preprocessing is required because the linker template uses C
preprocessor directives to produce the final GNU linker script.

The CMSIS project mounts the v1.4.0 checkout read-only to compile the existing
runner and Corstone platform sources. ExecuTorch runtime, backend, registration,
and operator sources come from the installed ExecuTorch CMSIS Pack.

## What you've accomplished and what's next

You have prepared a Corstone-300 CMSIS project containing the exported model
and the platform files needed to execute it. The project selects the versioned
ExecuTorch, CMSIS-NN, Ethos-U, and portable components that match the graph.

Next, you will build the application from the selected pack components, verify
their source paths, and run the model on the FVP.
