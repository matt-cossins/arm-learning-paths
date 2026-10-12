---
title: Run and serve a GGUF model
description: Build llama.cpp on Arm, run a small GGUF language model directly, and expose it through llama-server.
weight: 6

### FIXED, DO NOT MODIFY
layout: learningpathall
---

You now have the information needed to choose the first implementation. This section uses `llama.cpp` because it can run GGUF language models directly and includes `llama-server` for HTTP access.

You will use the Qwen3 0.6B model with 4-bit quantization. The GGUF file is about 429 MB, which keeps this first service small enough for many Arm Linux systems. Model output is not deterministic, so your generated text will differ from the examples in this Learning Path.

## Confirm the Arm architecture

Confirm that the machine uses a 64-bit Arm processor:

```bash
uname -m
```

The expected output is:

```output
aarch64
```

## Install the build tools

Update the package index and install the compiler, CMake, Git, `curl`, and `jq`:

```bash
sudo apt update
sudo apt install -y build-essential cmake git curl jq
```

`jq` formats the JSON returned by the service. It is not part of the inference runtime.

## Build llama.cpp for Arm

Clone the `llama.cpp` repository:

```bash
git clone --depth 1 https://github.com/ggml-org/llama.cpp.git
cd llama.cpp
```

Configure an AArch64 build with Arm KleidiAI microkernels enabled, then build the command-line client and server:

```bash
cmake -S . -B build -DGGML_CPU_KLEIDIAI=ON -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release --parallel
```

Confirm that both programs were created:

```bash
ls build/bin/llama-cli build/bin/llama-server
```

The output is similar to:

```output
build/bin/llama-cli
build/bin/llama-server
```

Enabling KleidiAI makes compatible Arm CPU kernels available. `llama.cpp` still selects kernels at runtime according to the processor features, tensor type, operation shape, and active backend.

## Run the model directly

Use `llama-cli` to download the 4-bit GGUF file and run one prompt:

```bash
./build/bin/llama-cli \
  -hf ggml-org/Qwen3-0.6B-GGUF:Q4_0 \
  -p "Name three responsibilities of an inference runtime. /no_think" \
  -n 96
```

The first run downloads the model to the `llama.cpp` cache. Later runs reuse the cached file.

The terminal shows model-loading information followed by generated text and timing data. Look for a CPU backend line containing `CPU_KLEIDIAI`. This confirms that the model tensors use the KleidiAI CPU buffer.

This direct run has no service boundary. The command loads the model, performs inference, prints the result, and exits.

## Start the local service

Start `llama-server` with the same model:

```bash
./build/bin/llama-server \
  -hf ggml-org/Qwen3-0.6B-GGUF:Q4_0 \
  --host 127.0.0.1 \
  --port 8080 \
  --ctx-size 2048 \
  --metrics
```

The model remains loaded after startup. The service listens only on the local loopback interface, so another machine cannot connect to it.

Keep this terminal open. Use a second terminal for the remaining commands, and change to the `llama.cpp` directory there.

## Check service readiness

In the second terminal, request the health endpoint:

```bash
curl --fail --silent http://127.0.0.1:8080/health | jq
```

When the model is loaded, the expected response is:

```output
{
  "status": "ok"
}
```

The endpoint returns HTTP status `503` while the model is loading and status `200` when the server is ready. A client can use this distinction instead of sending generation requests to a service that is still starting.

## What you've accomplished

You have run the same GGUF model in two ways: directly through `llama-cli` and as a persistent process through `llama-server`. Next, you will use the server's API without exposing the model format or runtime command to the client.
