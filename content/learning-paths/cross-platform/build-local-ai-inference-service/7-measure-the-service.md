---
title: Measure latency, throughput, and memory
description: Measure model readiness, client-visible time to first token, generation speed, and server memory use.
weight: 8

### FIXED, DO NOT MODIFY
layout: learningpathall
---

One timing value cannot describe the complete service. Measure startup, prompt processing, token generation, end-to-end latency, and memory separately.

## Measure time to readiness

Stop the foreground server with **Ctrl+C**. Then start it in the background while recording the time until the health endpoint reports readiness:

```bash
start_ms=$(date +%s%3N)

./build/bin/llama-server \
  -hf ggml-org/Qwen3-0.6B-GGUF:Q4_0 \
  --host 127.0.0.1 \
  --port 8080 \
  --ctx-size 2048 \
  --metrics \
  > llama-server.log 2>&1 &

server_pid=$!
printf '%s\n' "$server_pid" > llama-server.pid

until curl --fail --silent http://127.0.0.1:8080/health > /dev/null; do
  if ! kill -0 "$server_pid" 2>/dev/null; then
    tail -n 30 llama-server.log
    exit 1
  fi
  sleep 0.2
done

end_ms=$(date +%s%3N)
printf 'Time to readiness: %s ms\n' "$((end_ms - start_ms))"
```

The measurement begins when the process starts and ends when the model is ready to accept a request. Because the earlier direct run cached the model, it does not normally include a model download.

Run the measurement several times before comparing changes. Filesystem caching and other system activity can affect startup.

## Measure time to first token

Create a Python virtual environment and install the `requests` HTTP library:

```bash
python3 -m venv inference-client
source inference-client/bin/activate
python -m pip install requests
```

Create a file named `measure_stream.py` with the following content:

```python
import json
import time

import requests

URL = "http://127.0.0.1:8080/v1/chat/completions"
PAYLOAD = {
    "model": "ggml-org/Qwen3-0.6B-GGUF:Q4_0",
    "messages": [
        {
            "role": "user",
            "content": "Explain prefill and decode in three short sentences. /no_think",
        }
    ],
    "max_tokens": 96,
    "temperature": 0.2,
    "stream": True,
}

start = time.perf_counter()
first_text_at = None
parts = []

with requests.post(URL, json=PAYLOAD, stream=True, timeout=120) as response:
    response.raise_for_status()

    for line in response.iter_lines(decode_unicode=True):
        if not line or not line.startswith("data: "):
            continue

        event = line[6:]
        if event == "[DONE]":
            break

        data = json.loads(event)
        text = data["choices"][0]["delta"].get("content", "")
        if text:
            if first_text_at is None:
                first_text_at = time.perf_counter()
            parts.append(text)

end = time.perf_counter()

if first_text_at is None:
    raise RuntimeError("The stream ended without generated text")

print("".join(parts))
print(f"\nTTFT: {(first_text_at - start) * 1000:.1f} ms")
print(f"End-to-end time: {(end - start) * 1000:.1f} ms")
```

Run the client:

```bash
python measure_stream.py
```

The output contains the generated text followed by TTFT and total client-visible time. TTFT includes HTTP handling and prompt processing as observed by this client.

## Read prompt and generation rates

Send another synchronous request and select the server timing fields:

```bash
curl --fail --silent http://127.0.0.1:8080/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "ggml-org/Qwen3-0.6B-GGUF:Q4_0",
    "messages": [
      {
        "role": "user",
        "content": "Explain why a KV cache uses memory. /no_think"
      }
    ],
    "max_tokens": 96,
    "temperature": 0.2
  }' | jq '.timings | {
    prompt_tokens: .prompt_n,
    prompt_ms,
    prompt_tokens_per_second: .prompt_per_second,
    generated_tokens: .predicted_n,
    generation_ms: .predicted_ms,
    generated_tokens_per_second: .predicted_per_second
  }'
```

Prompt rate describes prefill. Generated tokens per second describes decode. Do not combine the two rates: they measure different phases of language-model inference.

## Check server memory

Display the resident memory used by `llama-server`:

```bash
ps -C llama-server -o pid,rss,cmd
```

The `RSS` column reports resident memory in KiB on Linux. Record it after loading, after the first request, and after changing context size or concurrency.

The model weights are only part of this value. The process also stores the KV cache, runtime code, input and output tensors, and temporary calculations.

## Keep comparisons controlled

When comparing results, record:

- Processor and available memory
- `llama.cpp` revision
- Model and quantization
- Context size
- Prompt and maximum output length
- Thread and concurrency settings
- Whether the request is cold or warm

Change one setting at a time. Otherwise, a faster result cannot be attributed to one model, runtime, or service change.

To stop the background server after completing the Learning Path, run:

```bash
kill "$(cat llama-server.pid)"
```

## What you've accomplished

You have measured service readiness, TTFT, prompt rate, generation rate, end-to-end time, and resident memory. These measurements provide a baseline for comparing another model, quantization, runtime, or Arm system.
