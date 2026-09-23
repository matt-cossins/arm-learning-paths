---
title: CMSIS-NN provides optimized fallback for Ethos-U NPUs
weight: 4
description: Partition the model for Ethos-U55, then lower the remaining supported convolution to CMSIS-NN.

### FIXED, DO NOT MODIFY
layout: learningpathall
---

## Deploying across Cortex-M and Ethos-U NPU

We can re-use the same script as on the previous page, this time using 'Fallback mode'. This uses `EthosUPartitioner` to
create an Ethos-U55 delegate region, represented by `executorch_call_delegate`.
The exporter then applies `CortexMPassManager` to operations left outside that
delegate, lowering its supported convolution to a registered Cortex-M operator
implemented by CMSIS-NN.

This is planned fallback, not recovery from a runtime NPU error. During export,
the partitioner checks operator support and assigns graph regions to Ethos-U.
Known unsupported operations remain in the graph for another implementation.
Here, the stride-four convolution is deliberately used to demonstrate that
path.

{{% notice Why this example uses Ethos-U55 %}}
Ethos-U55 is used because its unsupported stride-four convolution creates a
predictable fallback region. Ethos-U85 supports more operator configurations,
so will typically have less CPU fallback than U55. The same workflow still
applies when a model contains operations that remain outside the U85 delegate.
{{% /notice %}}

For supported neural-network operations, the expected order is Ethos-U NPU,
then CMSIS-NN on the Cortex-M CPU, then a portable CPU kernel. This keeps as much
work as possible on the NPU and gives unsupported quantized work an optimized
CPU route before using a general implementation. Measure the complete graph on
the target device because tensor conversions and graph boundaries can change
the end-to-end result.

The exporter first creates an Ethos-U55 compile specification and configures
the target-specific quantizer:

```python
compile_spec = EthosUCompileSpec(target=args.target)
quantizer = EthosUQuantizer(compile_spec)
quantizer.set_global(
    get_symmetric_quantization_config(is_per_channel=True)
)
```

After quantization, `EthosUPartitioner` identifies supported regions and lowers
them into an Ethos-U delegate:

```python
edge_program_manager = to_edge_transform_and_lower(
    quantized_exported_program,
    partitioner=[EthosUPartitioner(compile_spec)],
    compile_config=EdgeCompileConfig(_check_ir_validity=False),
)
```

The exporter then applies Cortex-M lowering to the operations that remain
outside the delegate:

```python
edge_program_manager._edge_programs["forward"] = CortexMPassManager(
    edge_program_manager.exported_program()
).transform()
```

The order is important: Ethos-U partitioning runs first, so
`CortexMPassManager` only transforms the non-delegated remainder.

## Export the partially delegated program

Run the exporter in Ethos-U fallback mode:

```bash
source ~/executorch-cmsis-lp/env.sh
source "$ET_ROOT/.venv/bin/activate"
cd "$LP_WORKSPACE"

python export_cortex_m_fallback.py \
  --mode ethos-u-fallback \
  --target ethos-u55-128 \
  --output-dir artifacts
```

The relevant output is similar to:

```output
Relevant targets before Cortex-M lowering:
aten.convolution.default: 1
aten.topk.default: 1
executorch_call_delegate: 1

Relevant targets after Cortex-M lowering:
aten.topk.default: 1
cortex_m.dequantize_per_tensor.default: 2
cortex_m.quantize_per_tensor.default: 2
cortex_m.quantized_conv2d.default: 1
executorch_call_delegate: 1
```

The final graph contains all three execution paths:

- `executorch_call_delegate` contains the stride-one convolution accepted by
  Ethos-U55.
- `cortex_m.quantized_conv2d` is the stride-four convolution rejected by
  Ethos-U55 and lowered to CMSIS-NN.
- `aten.topk` remains a portable FP32 operation.

The graph contains two quantize and two dequantize operations because values
cross between delegated INT8 work, Cortex-M INT8 work, and portable FP32 work.
Keeping these conversions visible helps you judge the whole fallback region,
rather than considering only the convolution kernel.

The lowered targets determine which components the CMSIS project needs:

| Model operation | Lowered graph target | CMSIS project component | Execution engine |
| --- | --- | --- | --- |
| Stride-one convolution | `executorch_call_delegate` | `Backend EthosU` and `Ethos-U Driver Generic U55` | Ethos-U55 |
| Stride-four convolution | `cortex_m.quantized_conv2d` | `Cortex-M quantized_conv2d` and `CMSIS:NN Lib` | Cortex-M55 with CMSIS-NN |
| Quantized boundaries | `cortex_m.quantize_per_tensor` and `cortex_m.dequantize_per_tensor` | Matching Cortex-M operator components | Cortex-M55 |
| Output selection | `aten.topk` | `Portable topk` | Cortex-M55 portable FP32 kernel |

The CMSIS project also needs the ExecuTorch runtime, kernel utilities, and
operator registration components. You will inspect these components when you
open the published pack.

## What you've accomplished and what's next

You have exported a program that distributes work across Ethos-U55,
CMSIS-NN, and a portable FP32 kernel. The unsupported convolution does not need
to fall back to a general FP32 implementation: it remains quantized and uses a
CMSIS-NN-backed Cortex-M operator. This is designed to reduce the CPU cost of
known unsupported NPU work, although performance must still be measured on the
target device, including quantize and dequantize boundaries.

Next, you will download and inspect the published ExecuTorch CMSIS Pack that
supplies these runtime, backend, and operator components.
