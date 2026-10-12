---
title: Send synchronous and streaming requests
description: Call the local generation service with synchronous and streaming HTTP requests and inspect the returned metadata.
weight: 7

### FIXED, DO NOT MODIFY
layout: learningpathall
---

`llama-server` provides OpenAI-compatible routes for common client operations. This compatibility covers useful request and response conventions, but it does not mean that every OpenAI API feature is supported.

Make sure the server from the previous section is still running before sending requests.

## Identify the loaded model

Ask the server which model it exposes:

```bash
curl --fail --silent http://127.0.0.1:8080/v1/models | jq '.data[] | {id, owned_by}'
```

The model identifier contains the repository and quantization used to start the server. A client can discover this value rather than assuming that a particular model is loaded.

## Send a synchronous request

Send a chat completion request and ask the server to return at most 96 generated tokens:

```bash
curl --fail --silent http://127.0.0.1:8080/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "ggml-org/Qwen3-0.6B-GGUF:Q4_0",
    "messages": [
      {
        "role": "user",
        "content": "Explain the difference between a model artifact and an inference runtime in two sentences. /no_think"
      }
    ],
    "max_tokens": 96,
    "temperature": 0.2,
    "stream": false
  }' | jq '{text: .choices[0].message.content, finish_reason: .choices[0].finish_reason, usage, timings}'
```

The response contains four kinds of information:

- `text` contains the generated answer.
- `finish_reason` reports why generation stopped.
- `usage` reports prompt, completion, and total token counts.
- `timings` separates prompt processing from token generation.

If `finish_reason` is `length`, the response reached `max_tokens`. This is different from the model producing a natural stop token.

## Send a streaming request

Set `stream` to `true` and use `curl --no-buffer` so that it prints each server-sent event as it arrives:

```bash
curl --no-buffer http://127.0.0.1:8080/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "ggml-org/Qwen3-0.6B-GGUF:Q4_0",
    "messages": [
      {
        "role": "user",
        "content": "List three reasons to put an HTTP service around an inference runtime. /no_think"
      }
    ],
    "max_tokens": 96,
    "temperature": 0.2,
    "stream": true
  }'
```

The output arrives as a sequence of lines beginning with `data:`. Each JSON event can contain a small piece of generated text. The final event is `data: [DONE]`.

Streaming changes how the client receives a result, not how the model generates tokens. The model still performs prefill before decoding its response one token at a time.

## Inspect service metrics

Because the server was started with `--metrics`, view selected Prometheus metrics:

```bash
curl --fail --silent http://127.0.0.1:8080/metrics | \
  grep -E '^llamacpp:(prompt_tokens_total|prompt_tokens_seconds|tokens_predicted_total|predicted_tokens_seconds|requests_processing|requests_deferred)'
```

The counters increase as the server handles requests. The processing and deferred gauges help distinguish active inference from queued work.

## What you've accomplished

You have used the same endpoint for complete and streamed responses, inspected usage and timing data, and checked service-level metrics. Next, you will measure client-visible latency and server memory separately.
