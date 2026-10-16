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

Clone the Metis repository at the tested [v1.5.5 release](https://github.com/arm/metis/releases/tag/metis-v1.5.5):

```bash
git clone --branch metis-v1.5.5 --depth 1 \
  https://github.com/arm/metis.git \
  "$HOME/metis-security-review/metis"

cd "$HOME/metis-security-review/metis"

uv sync --no-dev --python 3.12
source "$HOME/metis-security-review/metis/.venv/bin/activate"

command -v metis
metis --version
git rev-parse HEAD

cd "$HOME/metis-security-review"
```

`uv sync --no-dev --python 3.12` installs only the runtime dependencies needed to run the Metis CLI, using Python 3.12. It creates `metis/.venv` and installs Metis there. Activating the environment makes the `metis` command and the matching Python interpreter available in the current terminal.

The expected output from `metis --version` for this tag is:

```output
Metis 1.5.0
```

The `metis-v1.5.5` tag points to commit [`a9f9bdbc9b0ee5c511e32c526fdbdd33719d0ace`](https://github.com/arm/metis/commit/a9f9bdbc9b0ee5c511e32c526fdbdd33719d0ace). This tag retains stale package and CLI version metadata of `1.5.0`; the tag and full Git commit identify the tested v1.5.5 release. Record them alongside the reported package version when comparing runs.

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
```

Do not add secrets to `.metis.md`, `metis-review.yaml`, shell history, source control, or report files.

Create a provider configuration outside the review targets:

```bash
cat > "$HOME/metis-security-review/metis-review.yaml" <<'EOF'
llm_provider:
  name: openai
  model: gpt-5.5
  base_url: https://api.openai.com/v1
EOF
```

The review commands select this file explicitly with `--config`. Set `model` to a model available to your account; `gpt-5.5` is the packaged OpenAI default in Metis v1.5.5. Metis reads the API key from `OPENAI_API_KEY`. This provider-only configuration inherits the packaged execution graph.

For an OpenAI-compatible endpoint, set `llm_provider.base_url` to its URL. The endpoint must support the OpenAI Responses API.

For custom CA certificates, follow the [HTTPX `SSL_CERT_FILE` guidance](https://www.python-httpx.org/environment_variables/#ssl_cert_file). Keep certificate verification enabled.

For other providers, follow the [Metis v1.5.5 provider setup instructions](https://github.com/arm/metis/blob/metis-v1.5.5/README.md#2-set-up-llm-provider).

## Confirm that the command starts

Display the command help without starting a model-backed review. This verifies the CLI before you spend tokens on a review:

```bash
metis --help
```

The help output should include options such as `--codebase-path`, `--config`, `--interactive`, and `--output-file`. Metis v1.5.5 runs the configured graph by default; the packaged graph includes Initialize, Review, and Triage. Use `--interactive` to open the prompt for the exercises. Their direct review commands run Initialize prerequisites automatically, and omitting `--triage` keeps the results review-only so you can assess the findings manually afterward.

## What you've accomplished and what's next

You installed the tested Metis v1.5.5 release and set it up with your model provider. Next, you will review a small C program and compare the report with defects that are intentionally present in its source.
