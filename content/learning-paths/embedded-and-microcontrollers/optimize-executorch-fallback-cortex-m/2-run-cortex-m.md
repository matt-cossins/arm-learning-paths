---
title: Lower a model to the Cortex-M backend
weight: 3
description: Export a Cortex-M baseline and identify CMSIS-NN accelerated convolutions and a portable FP32 operation.

### FIXED, DO NOT MODIFY
layout: learningpathall
---

## Use a simple convolution example

With the ExecuTorch CMSIS environment and export workspace ready, start by
creating the simple model introduced at the start of the previous page. We will then lower to Cortex-M, without any Ethos-U backend. This use-case is for a device that does not contain an NPU.

The model contains two convolutions followed by `topk`:

```python
self.conv1 = torch.nn.Conv2d(3, 4, kernel_size=3, stride=1, padding=1, bias=False)
self.conv2 = torch.nn.Conv2d(4, 1, kernel_size=3, stride=4, padding=1, bias=False)

values, _ = torch.topk(
    self.conv2(torch.relu(self.conv1(inputs))),
    k=1,
    dim=-1,
)
```

## See how the exporter lowers the graph

The exporter first prepares and converts the model with `CortexMQuantizer`:

```python
quantizer = CortexMQuantizer()

prepared = prepare_pt2e(exported_program.module(), quantizer)
prepared(*example_inputs)
quantized_model = convert_pt2e(prepared)
quantized_exported_program = torch.export.export(quantized_model, example_inputs)
```

The prepared model is run once with the example input to calibrate activation
ranges. `convert_pt2e()` uses those ranges to choose quantization parameters and
insert the operations that move values between FP32 and INT8.

The exporter converts the quantized program to the ExecuTorch Edge dialect and
applies the Cortex-M pass manager:

```python
edge_program_manager = to_edge(
    quantized_exported_program,
    compile_config=EdgeCompileConfig(_check_ir_validity=False),
)

edge_program_manager._edge_programs["forward"] = CortexMPassManager(
    edge_program_manager.exported_program()
).transform()
```

This step rewrites supported patterns as `cortex_m.*` operators. Unsupported
operations, including `aten.topk`, remain in the portable graph.

The Cortex-M backend is broader than CMSIS-NN. In this model, the quantized
convolutions use CMSIS-NN, while quantize and dequantize use Cortex-M operators
with Arm Helium vector implementations. A `cortex_m.*` target therefore means
that the Cortex-M backend owns the operator, not necessarily that CMSIS-NN
implements it.

{{% notice Important %}}
The Cortex-M backend is not a delegate. Delegation replaces a graph region with
a call to a separately compiled backend. Cortex-M lowering instead rewrites
supported patterns as registered `cortex_m.*` operators that the ExecuTorch
runtime dispatches normally. You will not see an `executorch_call_delegate`
node until the Ethos-U partitioner is added on the next page.
{{% /notice %}}

## Export the model for Cortex-M

Run the exporter from the separate workspace:

```bash
source ~/executorch-cmsis-lp/env.sh
source "$ET_ROOT/.venv/bin/activate"
cd "$LP_WORKSPACE"

python export_cortex_m_fallback.py \
  --mode cortex-m \
  --output-dir artifacts
```

The relevant output is similar to:

```output
Relevant targets before Cortex-M lowering:
aten.convolution.default: 2
aten.topk.default: 1

Relevant targets after Cortex-M lowering:
aten.topk.default: 1
cortex_m.dequantize_per_tensor.default: 2
cortex_m.quantize_per_tensor.default: 2
cortex_m.quantized_conv2d.default: 2
```

Both convolutions become `cortex_m.quantized_conv2d` operations. The
`aten.topk` operation remains portable FP32. Quantize and dequantize operations
mark where tensors move between FP32 and INT8 regions. These optimized Cortex-M
boundary operations are part of the executable graph and can matter when
evaluating the cost of a fallback path.

## What you've accomplished and what's next

You have seen how Cortex-M lowering replaces supported patterns with optimized
Cortex-M operators. The convolutions use CMSIS-NN, quantize and dequantize use
Helium vector implementations, and `topk` remains an ExecuTorch portable
kernel.

Next, you will see how CMSIS-NN provides optimized CPU fallback when deploying a
model to an Ethos-U NPU. The resulting graph combines Ethos-U delegation,
CMSIS-NN-backed Cortex-M operators, and a portable CPU kernel.
