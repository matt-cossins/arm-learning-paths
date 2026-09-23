#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


class ThreePathModel:
    def __new__(cls) -> Any:
        import torch

        class Model(torch.nn.Module):
            def __init__(self) -> None:
                super().__init__()
                self.conv1 = torch.nn.Conv2d(
                    in_channels=3,
                    out_channels=4,
                    kernel_size=3,
                    stride=1,
                    padding=1,
                    bias=False,
                )
                self.conv2 = torch.nn.Conv2d(
                    in_channels=4,
                    out_channels=1,
                    kernel_size=3,
                    stride=4,
                    padding=1,
                    bias=False,
                )

            def forward(self, inputs: torch.Tensor) -> torch.Tensor:
                values, _ = torch.topk(
                    self.conv2(torch.relu(self.conv1(inputs))),
                    k=1,
                    dim=-1,
                )
                return values

        return Model()


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Export a Cortex-M baseline or a partially delegated Ethos-U55, "
            "CMSIS-NN, and portable-kernel model."
        )
    )
    parser.add_argument(
        "--mode",
        choices=("cortex-m", "ethos-u-fallback"),
        required=True,
        help="Select Cortex-M-only lowering or Ethos-U55 followed by Cortex-M lowering.",
    )
    parser.add_argument(
        "--target",
        default="ethos-u55-128",
        help="Ethos-U target used by fallback mode and the Corstone FVP runner.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("artifacts"),
        help="Directory for the bundled program and graph summary.",
    )
    args = parser.parse_args()

    import torch
    from executorch.backends.cortex_m.passes.cortex_m_pass_manager import (
        CortexMPassManager,
    )
    from executorch.exir import (
        EdgeCompileConfig,
        ExecutorchBackendConfig,
        to_edge,
        to_edge_transform_and_lower,
    )
    from executorch.extension.export_util.utils import save_pte_program
    from torchao.quantization.pt2e.quantize_pt2e import convert_pt2e, prepare_pt2e

    torch.manual_seed(0)
    model = ThreePathModel().eval().to(memory_format=torch.channels_last)
    example_inputs = (
        torch.ones(1, 3, 8, 8, dtype=torch.float32).to(
            memory_format=torch.channels_last
        ),
    )
    exported_program = torch.export.export(model, example_inputs)

    if args.mode == "cortex-m":
        from executorch.backends.cortex_m.quantizer.quantizer import CortexMQuantizer

        quantizer = CortexMQuantizer()
    else:
        from executorch.backends.arm.ethosu import EthosUCompileSpec
        from executorch.backends.arm.quantizer import (
            EthosUQuantizer,
            get_symmetric_quantization_config,
        )

        compile_spec = EthosUCompileSpec(target=args.target)
        quantizer = EthosUQuantizer(compile_spec)
        quantizer.set_global(get_symmetric_quantization_config(is_per_channel=True))

    prepared = prepare_pt2e(exported_program.module(), quantizer)
    prepared(*example_inputs)
    quantized_model = convert_pt2e(prepared)
    quantized_exported_program = torch.export.export(quantized_model, example_inputs)
    reference_output = quantized_exported_program.module()(*example_inputs)

    if args.mode == "cortex-m":
        edge_program_manager = to_edge(
            quantized_exported_program,
            compile_config=EdgeCompileConfig(_check_ir_validity=False),
        )
    else:
        from executorch.backends.arm.ethosu import EthosUPartitioner

        edge_program_manager = to_edge_transform_and_lower(
            quantized_exported_program,
            partitioner=[EthosUPartitioner(compile_spec)],
            compile_config=EdgeCompileConfig(_check_ir_validity=False),
        )

    targets_before_cortex_m = count_targets(
        edge_program_manager.exported_program().graph_module.graph
    )

    edge_program_manager._edge_programs["forward"] = CortexMPassManager(
        edge_program_manager.exported_program()
    ).transform()

    targets_after_cortex_m = count_targets(
        edge_program_manager.exported_program().graph_module.graph
    )
    executorch_program = edge_program_manager.to_executorch(
        config=ExecutorchBackendConfig(extract_delegate_segments=False)
    )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    artifact_name = args.mode.replace("-", "_")
    artifact_path = args.output_dir / f"stride4_{artifact_name}.pte"
    save_pte_program(executorch_program, str(artifact_path))

    summary = {
        "mode": args.mode,
        "target": args.target,
        "artifact": str(artifact_path),
        "artifact_size_bytes": artifact_path.stat().st_size,
        "reference_output": reference_output.detach().flatten().tolist(),
        "targets_before_cortex_m": targets_before_cortex_m,
        "targets_after_cortex_m": targets_after_cortex_m,
    }
    summary_path = artifact_path.with_suffix(".json")
    summary_path.write_text(json.dumps(summary, indent=2) + "\n")

    print(f"Wrote {artifact_path}")
    print(f"Wrote {summary_path}")
    print("\nRelevant targets before Cortex-M lowering:")
    print_relevant_targets(targets_before_cortex_m)
    print("\nRelevant targets after Cortex-M lowering:")
    print_relevant_targets(targets_after_cortex_m)


def count_targets(graph: Any) -> dict[str, int]:
    counts: dict[str, int] = {}
    for node in graph.nodes:
        if node.op != "call_function":
            continue
        target = display_target(str(node.target))
        if target.startswith("<") and hasattr(node.target, "__name__"):
            target = node.target.__name__
        counts[target] = counts.get(target, 0) + 1
    return dict(sorted(counts.items()))


def print_relevant_targets(targets: dict[str, int]) -> None:
    found = False
    for target, count in targets.items():
        if (
            "cortex_m" in target
            or "delegate" in target
            or "convolution" in target
            or "topk" in target
        ):
            print(f"{display_target(target)}: {count}")
            found = True
    if not found:
        print("No delegate or Cortex-M targets found.")


def display_target(target: str) -> str:
    if target.startswith("<EdgeOpOverload: "):
        return target.removeprefix("<EdgeOpOverload: ").split(">", 1)[0]
    return target


if __name__ == "__main__":
    main()
