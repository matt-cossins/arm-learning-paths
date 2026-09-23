---
title: Install and configure Metis
description: Install a tested Metis release and configure a model provider with an API key.
weight: 3
layout: "learningpathall"
---

## Install system tools

The commands in this Learning Path use a Unix-like shell. Use Terminal on macOS, a Linux terminal, or an existing Ubuntu/Debian terminal running under WSL2 on Windows. Native Windows PowerShell and Command Prompt are not covered.

Select your platform and install the compiler, Git, and command-line utilities used to fetch code, apply patches, and inspect reports:

{{< tabpane code=true >}}
  {{< tab header="macOS" language="bash">}}
xcode-select --install
  {{< /tab >}}
  {{< tab header="Ubuntu Linux or WSL2" language="bash">}}
sudo apt-get update
sudo apt-get install -y build-essential ca-certificates curl git grep patch sed
  {{< /tab >}}
{{< /tabpane >}}

If the Xcode Command Line Tools are already installed, macOS reports that no installation is needed. On WSL2, use the Linux filesystem for this exercise and avoid creating the workspace under `/mnt/c`.

## Install uv and Python

Metis is a Python project. Use `uv` to install Python 3.12 and create an isolated Metis environment:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Load the shell environment created by the installer and confirm that `uv` is available:

```bash
source "$HOME/.local/bin/env"
uv --version
```

Install Python 3.12 using `uv`:

```bash
uv python install 3.12
uv python find 3.12
```

The second command prints the path to the managed Python 3.12 executable.

Check that all command-line tools used by the exercises are available:

```bash
for tool in curl git grep patch sed uv; do
  command -v "$tool" >/dev/null || echo "Missing: $tool"
done
```

The command prints nothing when all required tools are available. Install any tools that are missing.

## Create the exercise workspace

Create one workspace in your home directory for Metis, the review targets, and generated reports. On WSL2, `$HOME` is inside the Linux filesystem:

```bash
mkdir -p "$HOME/metis-security-review/results"
cd "$HOME/metis-security-review"
```

## Clone and install Metis

Clone the Metis repository at the 1.5.0 release:

```bash
git clone --branch metis-v1.5.0 --depth 1 \
  https://github.com/arm/metis.git \
  "$HOME/metis-security-review/metis"

cd "$HOME/metis-security-review/metis"

uv sync --no-dev
source "$HOME/metis-security-review/metis/.venv/bin/activate"

command -v metis
metis --version

cd "$HOME/metis-security-review"
```

`uv sync --no-dev` installs only the runtime dependencies needed to run the Metis CLI. It selects a Python version that satisfies the Metis project requirements, creates `metis/.venv`, and installs Metis there. Activating the environment makes the `metis` command and the matching Python interpreter available in the current terminal.

The version command should report:

```output
Metis 1.5.0
```

If you open a new terminal, return to the exercise workspace and reactivate the Metis environment before continuing:

```bash
cd "$HOME/metis-security-review"
source "$HOME/metis-security-review/metis/.venv/bin/activate"
command -v metis
```

The path printed by `command -v` should end with `metis-security-review/metis/.venv/bin/metis`. If it points elsewhere, open a new terminal or run `deactivate`, then run the activation command again.

## Configure the model provider

Metis supports several hosted and local model providers. The following commands use OpenAI as an example. Export your API key in the same terminal that will run Metis:

```bash
export OPENAI_API_KEY="your-api-key"
# Optional: set this if your organization uses an OpenAI-compatible proxy.
# export OPENAI_BASE_URL="https://your-openai-compatible-endpoint/v1"
```

Do not add secrets to `.metis.md`, shell history, source control, or report files.

If your organization provides an OpenAI-compatible endpoint, export `OPENAI_BASE_URL` before running Metis. Additionally, remember to install any certificates required by your organization so Python can verify the endpoint. Otherwise, the examples use the public OpenAI API endpoint.

For other model providers, follow the [Metis provider instructions](https://github.com/arm/metis#2-set-up-llm-provider).

Check that Python inside the active Metis environment can reach the configured OpenAI endpoint:

```bash
python - <<'PY'
import os
import httpx

base_url = (
    os.environ.get("OPENAI_BASE_URL")
    or os.environ.get("OPENAI_API_BASE")
    or "https://api.openai.com/v1"
)
response = httpx.get(
    base_url.rstrip("/") + "/models",
    headers={"Authorization": "Bearer " + os.environ["OPENAI_API_KEY"]},
    timeout=20,
)
print(f"status: {response.status_code}")
response.raise_for_status()
PY
```

The expected output is:

```output
status: 200
```

If this check reports `401` or `403`, check the API key and model access. If it reports `404`, check the base URL. If it reports a certificate verification error or timeout, check your network, proxy, and Python certificate configuration before running a review.

The endpoint you use can affect runtime, rate limits, retry behavior, response formatting, and the set of reported findings.

## Confirm that the command starts

Display the command help without starting a model-backed review. This verifies the CLI before you spend tokens on a review:

```bash
metis --help
```

The help output should include options such as `--codebase-path`, `--command`, `--non-interactive`, and `--output-file`.

## What you've accomplished and what's next

You installed Metis v1.5.0 and set it up with your model provider. Next, you will review a small C program and compare the report with defects that are intentionally present in its source.
