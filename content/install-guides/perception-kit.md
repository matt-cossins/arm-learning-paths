---
additional_search_terms:
- perception
- gstreamer
- raspberry pi
- edge ai
- physical ai


layout: installtoolsall
minutes_to_complete: 30
author: Matt Cossins
multi_install: false
multitool_install_part: false
official_docs: https://github.com/Arm-Debug/amp-dev-forge/tree/main/docs/public/how-to/quick-guides
test_maintenance: false

title: Arm Perception Pipeline Kit
tool_install: true
weight: 1
---

The [Arm Perception Pipeline Kit](https://github.com/Arm-Debug/amp-dev-forge) is a GStreamer-based framework for building AI-enabled media pipelines on Arm platforms.

This guide shows how to install and set up the Arm Perception Pipeline Kit for three supported environments:

- Raspberry Pi 5 (at least 32GB SD card or SSD recommended)
- macOS
- Ubuntu Linux / Windows Subsystem for Linux (WSL)

If using a Raspberry Pi 5, you should do so over SSH from a separate development machine. See [Raspberry Pi - Getting Started](https://www.raspberrypi.com/documentation/computers/getting-started.html#headless-setup) for how to create a headless setup. This should result in your Pi flashed with Raspberry Pi OS, and accessible over SSH from your development machine, via terminal.

## Set up your development environment

To use the Arm Perception Pipeline Kit, we must set up our development environment. If using Mac/Linux/WSL, install these directly. If using Raspberry Pi 5, install these on the development machine you use to access the Pi over SSH, and also install the Remote Access extension to perform SSH access to the Pi within VS Code:

- [Visual Studio Code](https://code.visualstudio.com/download)
- [VS Code Dev Containers Extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
- (Raspberry Pi 5 Route Only - Install on Development Machine) [VS Code Remote SSH Extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-ssh)

If using the Raspberry Pi 5, you can now use the Remote SSH Extension to connect to your Pi. See the [VS Code Remote SSH guide](https://code.visualstudio.com/docs/remote/ssh).

## Install platform prerequisites

We will now install various prerequisite packages on our development machine using the terminal.

If you are using a Pi, ensure that you run these commands on the Pi itself. Now that you have SSH'd into the Pi with VS Code, you can use the terminal within VS Code.

For macOS and Linux / WSL, run the commands on your development machine.

Use the tabs below to run the commands for your platform and install the remaining prerequisites:

{{< tabpane code=true >}}
	{{< tab header="Raspberry Pi 5" language="bash">}}
sudo apt update
sudo apt full-upgrade -y
sudo rpi-eeprom-update -a
sudo apt-get update
sudo apt-get install -y git v4l-utils raspi-utils-core raspi-utils-dt ca-certificates curl
sudo apt-get install rpicam-apps libcamera-dev libcamera-doc libcamera-tools \
  gstreamer1.0-tools gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly gstreamer1.0-gl \
  libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev libgstreamer-plugins-bad1.0-dev \
  gstreamer1.0-libcamera \
  code  libcairo2-dev libssl-dev

sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] \
https://download.docker.com/linux/debian \
$(. /etc/os-release && echo $VERSION_CODENAME) stable" | \
sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update

sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

sudo usermod -aG docker $USER
	{{< /tab >}}
	{{< tab header="macOS" language="bash">}}
brew update
brew install git
brew install --cask docker
	{{< /tab >}}
    {{< tab header="Linux / WSL (Ubuntu)" language="bash">}}
sudo apt-get update
sudo apt-get install -y git v4l-utils ca-certificates curl

sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] \
https://download.docker.com/linux/ubuntu \
$(. /etc/os-release && echo $VERSION_CODENAME) stable" | \
sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

sudo usermod -aG docker $USER
    {{< /tab >}}
{{< /tabpane >}}

At this point, your platform has the required base tooling and Docker setup.

{{% notice Note %}}
For Linux/WSL or Raspberry Pi, after running the `usermod` command, you must log out and log back in (or reboot) for the docker group changes to take effect. Alternatively, you can run `newgrp docker` to apply the change in the current session.

For macOS, make sure to run Docker Desktop in the background.
{{% /notice %}}

## (Optional) Hailo Accelerator Setup

If you intend to use a Hailo Accelerator (e.g. Raspberry Pi AI Hat + or AI Hat+ 2), you must assemble the hardware and install additional dependencies.

To assemble the hardware:
1. Attach spacers to the Raspberry Pi 5.
2. Mount the AI Hat onto the GPIO header.
3. Connect the PCIe ribbon cable from the Raspberry Pi 5 PCIe port to the Hat (copper contacts should face up on the HAT side)
4. Connect the power supply.

Enable PCIe Gen 3 - run the following on the Pi terminal:

```bash
sudo raspi-config
```
Select `Advanced Options - PCIe Speed - Enable Gen 3`

This maximizes performance by doubling the available bandwidth between the Raspberry Pi 5 and the AI Hat.

Then install the dependencies below on your Raspberry Pi 5, selecting the appropriate Hailo accelerator:

{{< tabpane code=true >}}
	{{< tab header="Hailo8" language="bash">}}
sudo apt-get update
sudo apt-get install dkms
sudo apt-get install hailo-all
sudo reboot
	{{< /tab >}}
	{{< tab header="Hailo10" language="bash">}}
sudo apt-get update
sudo apt-get install dkms
sudo apt-get install hailo-h10-all
sudo reboot
	{{< /tab >}}
{{< /tabpane >}}

After reboot, reconnect to the Raspberry Pi over SSH before continuing.

Verify Hailo setup by running the following in the terminal:
```bash
hailortcli fw-control identify
```

The expected output will appear similar to the following (adjusted for your specific device):

```output
Executing on device: 0001:03:00.0
Identifying board
Control Protocol Version: 2
Firmware Version: 4.23.0 (release,app,extended context switch buffer)
Logger Version: 0
Board Name: Hailo-8
Device Architecture: HAILO8
```

If this command returns board and firmware information, Hailo setup is complete.

## Set up the Perception Kit

Clone the repository into your chosen device:

```bash
git clone https://github.com/Arm-Debug/amp-dev-forge.git
cd amp-dev-forge
```

After cloning the repository, open the `amp-dev-forge` folder in VS Code. It is important you open this specific directory for the following steps to work.

Open the Command Palette with `Cmd + Shift + P` or `Ctrl + Shift + P`, depending on macOS vs Linux / WSL.

Run `Dev Containers: Reopen in Container`

![Screenshot of `Dev Containers: Reopen in Container` in Command Palette #center](/install-guides/_images/dev_container.png "Dev Containers: Reopen in Container")

You will be presented with several container options. For development work directly on Mac or Linux / WSL machines, select the `PC` option. For Raspberry Pi 5, select `RPI5 H8` if you intend to use CPU or Hailo8, or `RPI5 H10` if you intend to use CPU or Hailo10.

![Screenshot of Container Options in Command Palette #center](/install-guides/_images/container_opts.png "Container Options")

Wait until this completes - it may take some time. Once completed, your terminal in VS Code should appear as follows:

```output
╔═════════════════════════════════════════════════════════════════════════════╗
║ AMP repo ready                                                              ║
╠═════════════════════════════════════════════════════════════════════════════╣
║ Build cmd       ./scripts/build-elements.sh debug                           ║
║ Build task      00 Build Project                                            ║
║ Launch cmd      /work/tools/amp-menu -l                                     ║
║ Launch task     99 Launch Without Debug                                     ║
║ Docs gen        ./scripts/gen-doc.sh                                        ║
║ Docs serve      ./scripts/serve-docs.sh                                     ║
╟─────────────────────────────────────────────────────────────────────────────╢
║ Web UI          http://raspberrypi.local:9999                               ║
║ Docs            http://raspberrypi.local:8080/index.html                    ║
╟─────────────────────────────────────────────────────────────────────────────╢
║ Ref             /work/docs/public/index.md                                  ║
╚═════════════════════════════════════════════════════════════════════════════╝

devgoblin@amp-dev-forge:/work$  source /work/tools/.venv/bin/activate
(.venv) devgoblin@amp-dev-forge:/work$ 
```

This confirms your Dev Container environment is ready.

## Verify correct installation with a demo pipeline

To verify the installation, we will build the project and run a demo pipeline.

Reopen the Command Palette

Run `Tasks: Run Task`

![Screenshot of `Tasks: Run Task` in Command Palette #center](/install-guides/_images/task_run_task.png "Tasks: Run Task")

Run `00 Build Project`

![Screenshot of `00 Build Project` in Command Palette #center](/install-guides/_images/build_project.png "00 Build Project")

Once the build has successfully completed, reopen the Command Palette.

Run `Tasks: Run Task`

Run `00 Run project and select pipeline` 

![Screenshot of `00 Run project and select pipeline` in Command Palette #center](/install-guides/_images/run_pipeline.png "00 Run project and select pipeline")

Choose `01-full-onnx`

![Screenshot of pipeline options in Command Palette #center](/install-guides/_images/pipeline_opts.png "Pipeline Options")

Navigate to `http://localhost:9999` on your browser (Microsoft Edge and Firefox are recommended).

You should see a WebRTC view showing a static image. You have the option to enable/disable AI models and view their inference overlaid on the image.

![Screenshot of the ampsink WebRTC page showing demo pipeline#center](/install-guides/_images/demo_pipeline.png "WebRTC page showing demo pipeline")

## (Optional) Verify Hailo accelerator setup

To verify the Hailo accelerator setup, try running a Hailo specific pipeline (e.g., `02-full-onnx-hailo8` if you are using Hailo8). You should see the same as above, now running on the Hailo accelerator. Enable the performance overlay to observe differences in performance between CPU and Accelerator mode.

## What have you completed?

You now have the Arm Perception Kit installed and verified for your platform. You are ready to move onto learning paths to build your own custom pipeline, and to develop applications using the pipelines.
