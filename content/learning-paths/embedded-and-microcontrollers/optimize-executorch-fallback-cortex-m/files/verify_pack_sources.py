#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


EXPECTED_SOURCES = (
    (
        "ExecuTorch runtime",
        "src/runtime/executor/program.cpp",
        ("/PyTorch/ExecuTorch/1.5.1/", "PyTorch_Machine_Learning_ExecuTorch_"),
    ),
    (
        "ExecuTorch Cortex-M convolution wrapper",
        "src/backends/cortex_m/ops/op_quantized_conv2d.cpp",
        ("/PyTorch/ExecuTorch/1.5.1/", "PyTorch_Machine_Learning_ExecuTorch_"),
    ),
    (
        "CMSIS-NN convolution kernel",
        "Source/ConvolutionFunctions/arm_convolve_s8.c",
        ("/ARM/CMSIS-NN/8.0.0/", "ARM_CMSIS_NN_Lib_8_0_0"),
    ),
    (
        "Ethos-U backend",
        "src/backends/arm/runtime/EthosUBackend.cpp",
        ("/PyTorch/ExecuTorch/1.5.1/", "PyTorch_Machine_Learning_ExecuTorch_"),
    ),
    (
        "ExecuTorch portable topk kernel",
        "src/kernels/portable/cpu/op_topk.cpp",
        ("/PyTorch/ExecuTorch/1.5.1/", "PyTorch_Machine_Learning_ExecuTorch_"),
    ),
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("compile_database", type=Path)
    args = parser.parse_args()

    entries = json.loads(args.compile_database.read_text())
    missing = []
    for label, source_path, pack_markers in EXPECTED_SOURCES:
        matched = False
        for entry in entries:
            source_file = entry.get("file", "").replace("\\", "/")
            command = entry.get("command", " ".join(entry.get("arguments", []))).replace(
                "\\", "/"
            )
            if source_file.endswith(source_path) and any(
                marker in f"{source_file} {command}" for marker in pack_markers
            ):
                matched = True
                break
        if matched:
            print(f"PASS: {label} was compiled from its declared CMSIS Pack")
        else:
            missing.append(label)

    if missing:
        raise SystemExit(f"Missing pack sources: {', '.join(missing)}")


if __name__ == "__main__":
    main()
