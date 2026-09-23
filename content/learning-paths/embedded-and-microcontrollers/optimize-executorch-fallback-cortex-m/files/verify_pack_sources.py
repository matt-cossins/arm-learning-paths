#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


EXPECTED_SOURCES = {
    "ExecuTorch runtime": "src/runtime/executor/program.cpp",
    "CMSIS-NN Cortex-M convolution": "src/backends/cortex_m/ops/op_quantized_conv2d.cpp",
    "Ethos-U backend": "src/backends/arm/runtime/EthosUBackend.cpp",
    "Portable topk": "src/kernels/portable/cpu/op_topk.cpp",
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("compile_database", type=Path)
    args = parser.parse_args()

    entries = json.loads(args.compile_database.read_text())
    source_files = {
        entry["file"].replace("\\", "/")
        for entry in entries
        if "file" in entry
    }

    missing = []
    for label, source_path in EXPECTED_SOURCES.items():
        pack_source = f"/PyTorch/ExecuTorch/1.4.0/{source_path}"
        if any(source_file.endswith(pack_source) for source_file in source_files):
            print(f"PASS: {label} came from the ExecuTorch CMSIS Pack")
        else:
            missing.append(label)

    if missing:
        raise SystemExit(f"Missing pack sources: {', '.join(missing)}")


if __name__ == "__main__":
    main()
