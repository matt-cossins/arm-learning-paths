---
title: Analyze ExecuTorch artifacts with Corstone

weight: 6

### FIXED, DO NOT MODIFY
layout: "learningpathall"
---

## Understand the ExecuTorch routes

The previous sections used TensorFlow Lite and TOSA artifacts with Vela. You can also use MLIA if you are working with a PyTorch / ExecuTorch flow.

A `.pte` file is a portable ExecuTorch executable: the packaged artifact that ExecuTorch can load and run. A `.pt2` file is a PyTorch exported program. It is useful earlier in the workflow, before the model has been packaged for a specific ExecuTorch runtime path.

In this section, you first compare two packaged `.pte` artifacts with Corstone backends. Then you briefly look at the `.pt2` converter route that MLIA can use earlier in an ExecuTorch-oriented workflow.

## Compare prebuilt .pte artifacts

The model artifacts repository includes prebuilt Ethos-U `.pte` files:

```output
pte/toy_conditional_select_int8_ethos_u55_256.pte
pte/toy_conditional_select_int8_ethos_u85_256.pte
```

These are synthetic learning artifacts, not benchmark models. They use a small convolution plus a conditional selection pattern to make target-dependent delegation easier to see. A model can be packaged for different Ethos-U targets and show different delegation and runtime-counter behavior.

For supported `.pte` workloads, MLIA performance analysis uses a Corstone backend. In this context, Corstone refers to an Arm reference subsystem platform, and the backend uses an FVP, or Fixed Virtual Platform. An FVP is a software model of a hardware platform. It lets you run a packaged artifact in a target-like environment and collect performance counters without needing a physical board on your desk.

For `.pte` artifacts, MLIA currently supports performance advice only. The artifact has already been packaged for an ExecuTorch deployment path, so Corstone is used to run the packaged program on an FVP and collect NPU counters. Use compatibility checks earlier in the flow, before packaging, when you are still asking whether operators and tensors can map to the target.

Install the Corstone backends used in this section:

```bash
mlia backend install corstone-320
mlia backend install corstone-300
```

{{% notice Note %}}
Corstone backend installation requires accepting a license. You will be prompted in the terminal to agree.
{{% /notice %}}

If you do not install a Corstone backend before running the check command, MLIA can prompt you to install it during the check.

{{% notice Note %}}
The Corstone FVP used by this backend may require the Python 3.9 shared library on the host. Install it before running the `.pte` checks:

```bash
sudo apt install -y libpython3.9
```

If your Ubuntu package repositories do not include `libpython3.9`, add the deadsnakes PPA and try again:

```bash
sudo apt install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y libpython3.9
```
{{% /notice %}}

Run the Ethos-U55 artifact with the Corstone-300 backend:

```bash
mlia check pte/toy_conditional_select_int8_ethos_u55_256.pte \
  --target-profile ethos-u55-256 \
  --performance \
  --backend corstone-300
```

Then run the Ethos-U85 artifact with the Corstone-320 backend:

```bash
mlia check pte/toy_conditional_select_int8_ethos_u85_256.pte \
  --target-profile ethos-u85-256 \
  --performance \
  --backend corstone-320
```

The reports should show Corstone running each `.pte` artifact and collecting NPU performance counters. Read the Corstone report as runtime counter evidence:

| Field | What it tells you |
| --- | --- |
| `NPU active cycles` | Cycles where the NPU was doing work. |
| `NPU idle cycles` | Cycles where the NPU was present but not active. A very small value means this run kept the NPU busy once work was issued. |
| `NPU total cycles` | Active plus idle cycles for the NPU portion of the run. |
| `NPU AXI0 RD/WR data beat` | Memory traffic on the AXI0 port, configured as SRAM for this target profile. |
| `NPU AXI1 RD/WR data beat` | Memory traffic on the AXI1 port, configured as DRAM for this target profile. |

Use the reports to compare the NPU counters for each packaged artifact:

| Artifact | Target profile | Backend | NPU total cycles |
| --- | --- | --- | --- |
| `toy_conditional_select_int8_ethos_u55_256.pte` | `ethos-u55-256` | `corstone-300` | `273,088` |
| `toy_conditional_select_int8_ethos_u85_256.pte` | `ethos-u85-256` | `corstone-320` | `19,056` |

The comparison uses `ethos-u55-256` and `ethos-u85-256`, so both target profiles use 256 MACs per cycle. However, Ethos-U85 is a newer and higher performance NPU than Ethos-U55, and the target information in the reports also shows other platform differences, such as accelerator clock and memory configuration.

The U55 report shows `271,725` NPU active cycles and `1,363` NPU idle cycles. The U85 report shows `18,183` NPU active cycles and `873` NPU idle cycles, for `19,056` total NPU cycles. This difference reflects the combined effect of improvements in the U85 over the U55.

The Corstone report focuses on NPU counters. If part of the graph runs outside the NPU delegate, the CPU-side cost is not fully represented by the NPU cycle table. Corstone output is different from the earlier Vela estimates. Vela gave compiler-estimated layer-level advice before deployment. Corstone runs the packaged `.pte` artifact on an FVP and reports runtime-oriented NPU counters. For `.pte` inputs, the advice can be less detailed at the layer level, but the counter values are useful for comparing packaged artifacts under the same target profile and backend.

## Use Model Explorer for graph structure

Across this Learning Path, you used MLIA with TensorFlow Lite, TOSA, ExecuTorch `.pte`, and PyTorch exported program artifacts. MLIA answers target-aware questions about compatibility, estimated performance, runtime counters, and advice. To see how these artifacts can be visualized as graphs in Model Explorer, continue with the [Explore model artifacts with Model Explorer](/learning-paths/cross-platform/explore-model-artifacts-with-model-explorer/) Learning Path, which uses many of the same files from the model artifacts repository.

Model Explorer can open some formats directly, while other formats use adapters. Use it alongside MLIA when you want to connect target advice with the graph structure that produced it.

In the example above, not only is the U85 expected to perform better due to its platform differences, there is also a difference in the way the model delegates to the U85 vs U55.

The model pattern is:

```output
convolution / activation
conditional select
convolution / activation / convolution
```

On Ethos-U55, the conditional select part is not kept inside the Ethos-U delegate path. The partitioning therefore looks like this:

```output
EthosUBackend region
aten::gt / aten::where outside delegate
EthosUBackend region
```

On Ethos-U85, that pattern is handled more cleanly by this target/backend flow, so the packaged artifact has one `EthosUBackend` region. This will provide further performance benefit, as there is reduced fragmentation between CPU and NPU. To visualize the delegation of models to different backends, we can use the Model Explorer tool, with Arm adapters.

{{% notice Note %}}
An ExecuTorch `.pte` file can contain work outside an accelerator delegate, but there is no guarantee that every non-delegated operator can run on the CPU runtime you deploy. CPU execution depends on the kernel libraries linked into that runtime and the operators, dtypes, layouts, and shapes they support. Cortex-M bare-metal runtimes are usually built with a smaller, more selective kernel set than Cortex-A runtimes, because Cortex-M systems have tighter memory and storage constraints. In both cases, actual CPU fallback support depends on which kernels are included in the runtime build.
{{% /notice %}}

## Use the .pt2 converter route

To analyze `.pt2` inputs, you need the PyTorch converter plugin:

```bash
pip install mlia-converters-pytorch
```

This plugin registers transformer names used by MLIA, including:

```output
pt2_to_tosa
pt2_to_pte
pte_to_delegate
```

These transformer names describe how MLIA can prepare PyTorch or ExecuTorch artifacts for downstream analysis. For example, when you give MLIA a `.pt2` file, the converter plugin can prepare the exported program for a target-specific analysis route instead of treating the `.pt2` file as a final deployment artifact.

The model artifacts repository includes a PyTorch exported program:

```output
pt2/toy_conditional_select_fp32.pt2
```

This artifact contains the same small model pattern used by the packaged `.pte` examples. 

Run MLIA on the `.pt2` file:

```bash
mlia check pt2/toy_conditional_select_fp32.pt2 \
  --target-profile ethos-u85-256 \
  --performance \
  --backend vela
```

{{% notice TODO %}}
Confirm installation and what the above does
{{% /notice %}}

With `mlia-converters-pytorch` installed, MLIA can use the converter route to prepare the PyTorch exported program for the requested target analysis.

## What you have learned

You have learned how `.tflite`, `.tosa`, `.pte`, and `.pt2` fit into MLIA workflows. You have also seen why PTE is useful for ExecuTorch artifact analysis, where TOSA can fit as an intermediate handoff, and why Model Explorer remains useful for graph structure.

Next, you will use the Python API to integrate MLIA into another workflow.
