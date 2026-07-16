---
title: Build and run ASR on a Corstone-320 FVP
description: Build the Arm MLEK Conformer ASR application and run it on a Corstone-320 FVP to validate the model, runtime, and file-based audio path.
weight: 3

layout: "learningpathall"
---

Now we will build the Arm MLEK `asr` application and run it on the Corstone-320 FVP. This checks the Conformer model, ExecuTorch runtime, audio preprocessing, and token decoding before you move to the Alif E8 DevKit.

## Understand the FVP ASR application

The `asr` application uses WAV files that are compiled into the firmware. This gives you a repeatable input before you introduce board microphones, buttons, display output, and external flash setup.

The FVP application runs the same core ASR stages used later on the E8 DevKit:

1. Read 16 kHz audio samples from the built-in sample set.
2. Convert the samples into Mel spectrogram features.
3. Run the Conformer model through ExecuTorch and the Ethos-U85 delegate.
4. Decode the output token scores with the SentencePiece vocabulary.
5. Print the decoded text to the FVP console.

## Build the FVP ASR application

Configure the `asr` build for the MLEK Corstone-320 target. In MLEK, `TARGET_PLATFORM=mps4` and `TARGET_SUBSYSTEM=sse-320` select the platform support used by the Corstone-320 FVP.

Activate the Python environment created by the resource setup script:

```bash
source resources_downloaded/env/bin/activate
```

```bash
cmake -B build_fvp_asr \
  -DTARGET_PLATFORM=mps4 \
  -DTARGET_SUBSYSTEM=sse-320 \
  -DCMAKE_TOOLCHAIN_FILE=scripts/cmake/toolchains/bare-metal-gcc.cmake \
  -DML_FRAMEWORK=executorch \
  -DUSE_CASE_BUILD=asr \
  -DETHOS_U_NPU_ID=U85 \
  -DETHOS_U_NPU_CONFIG_ID=Z256 \
  -DETHOS_U_NPU_MEMORY_MODE=Dedicated_Sram
```

Build only the ASR target:

```bash
cmake --build build_fvp_asr --target mlek_asr -j4
```

The output application is:

```output
build_fvp_asr/bin/mlek_asr.axf
```

## Run the application on the FVP

The MLEK resource setup script does not install the Corstone-320 FVP. Install the FVP before you run the built `mlek_asr.axf` application.

Use the [Arm IoT FVPs download page](https://developer.arm.com/tools-and-software/fixed-virtual-platforms/iot-fvps) and the [Arm Ecosystem FVPs install guide](/install-guides/fm_fvp/eco_fvp/) for the current installation steps. The host requirements differ by operating system: Linux can use the native Corstone-320 package, while macOS uses the FVPs for macOS flow with Docker.

After installation, make sure you can start the Corstone-320 FVP using the command or wrapper provided by your FVP installation.

For a native Linux installation, you can check that `FVP_Corstone_SSE-320` is on your `PATH`:

```bash
command -v FVP_Corstone_SSE-320
```

Run the ASR application:

```bash
FVP_Corstone_SSE-320 \
  -a build_fvp_asr/bin/mlek_asr.axf
```

For a headless run, disable visualization and send UART0 output to standard output:

```bash
FVP_Corstone_SSE-320 \
  -C mps4_board.visualisation.disable-visualisation=1 \
  -C vis_hdlcd.disable_visualisation=1 \
  -C mps4_board.telnetterminal0.start_telnet=0 \
  -C mps4_board.uart0.out_file='-' \
  -a build_fvp_asr/bin/mlek_asr.axf
```

The application uses audio samples compiled into the firmware at build time. By default, the `asr` use case reads WAV files from:

```output
resources/asr/samples/
```

## Use a custom audio sample

To test a known phrase, place one or more 16 kHz WAV files in a directory and set `asr_FILE_PATH` when configuring the build:

```bash
mkdir /tmp/asr_wavs
cp my_clip.wav /tmp/asr_wavs/

cmake -B build_fvp_asr \
  -DTARGET_PLATFORM=mps4 \
  -DTARGET_SUBSYSTEM=sse-320 \
  -DCMAKE_TOOLCHAIN_FILE=scripts/cmake/toolchains/bare-metal-gcc.cmake \
  -DML_FRAMEWORK=executorch \
  -DUSE_CASE_BUILD=asr \
  -DETHOS_U_NPU_ID=U85 \
  -DETHOS_U_NPU_CONFIG_ID=Z256 \
  -DETHOS_U_NPU_MEMORY_MODE=Dedicated_Sram \
  -Dasr_FILE_PATH=/tmp/asr_wavs/

cmake --build build_fvp_asr --target mlek_asr -j4
```

The CMake configure step converts the WAV files into generated C/C++ files and compiles them into the firmware.

## What you have accomplished and what is next

You have built the Arm MLEK Conformer ASR application, and run it on the Corstone-320 FVP.

Next, you will map the same application concepts into the Alif MLEK project structure.
