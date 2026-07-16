---
title: Adapt the ASR application for the Alif E8 DevKit
description: Set up Alif MLEK, locate the `alif_asr` application, and compare the board-specific code with the ASR application you ran on FVP.
weight: 4

layout: "learningpathall"
---

Now we will continue from the Corstone-320 FVP run by setting up Alif MLEK and reviewing the `alif_asr` application. You will see which parts of the ASR flow stay the same and which parts change for the Alif Ensemble E8 DevKit.

## Clone the Alif MLEK repository

Clone the Alif ML Embedded Evaluation Kit repository:

```bash
git clone https://github.com/alifsemi/alif_ml-embedded-evaluation-kit.git
cd alif_ml-embedded-evaluation-kit
git submodule update --init --recursive
```

{{% notice AUTHOR TODO %}}
This draft uses Alif MLEK commit `0b6ce72c495265501f7a12eaed8e6ea71ef4bf15`. It would be helpful to confirm the supported host and tool versions before publication, and to pin a commit if the generated model names or build commands need to remain stable.
{{% /notice %}}

{{% notice AUTHOR TODO %}}
Potential extra detail from Alif: it would be helpful to clarify whether the default PDM microphone path uses the onboard E8 DevKit microphones, the I2S/PDM microphone ports, or either option depending on board configuration.
{{% /notice %}}

## Prepare the ExecuTorch model

As before, we run the setup script with ExecuTorch enabled to generate the model in `.pte` format:

```bash
python3 set_up_default_resources.py --ml-frameworks executorch
```

This prepares the Conformer checkpoint, vocabulary, and Ethos-U85 `.pte` model family in the Alif repository layout. The board build uses these generated resources when it builds `mlek_alif_asr`.

## Locate the ASR application in MLEK

The Alif ASR application lives in:

```output
source/app/use_case/alif_asr/
```

The main files are:

- `usecase.cmake`: selects the model, labels, memory settings, and generated assets.
- `src/MainLoop.cc`: initializes the ExecuTorch Conformer model, activation buffer, labels, profiler, and application context.
- `src/UseCaseHandlerEt.cc`: handles audio input, Conformer preprocessing, inference, postprocessing, and logs for the ExecuTorch path.
- `src/UseCaseHandlerTflm.cc`: handles the TensorFlow Lite Micro path.
- `include/UseCaseHandler.hpp`: declares the use-case handlers.

The MRAM flash configuration is in:

```output
alif_asr.json
```

## Read the Alif application startup code

For the ExecuTorch build, `MainLoop.cc` uses `ConformerModel` as the ASR model wrapper. It creates two memory regions before it enters the use-case handler:

- `modelMem`: points to the generated model data.
- `computeMem`: points to the activation buffer used while loading and running the model.

The startup code then initializes the model, checks the input and output tensor dimensions, loads the vocabulary labels, creates the profiler, adds the Conformer window and hop settings to the application context, and calls `ClassifyAudioHandler(caseContext)`.

The application context passes the model, labels, profiler, and Conformer parameters to the handler without making each helper own the full application state.

## Read the board inference handler

The ExecuTorch handler is:

```output
source/app/use_case/alif_asr/src/UseCaseHandlerEt.cc
```

The default board flow uses PDM microphone input and prints the decoded text to the terminal output. This changes from an FVP flow that processes a fixed audio file, to an application that requires button input to start capturing and processing audio. 

The handler does the following:

1. Gets the model input and output tensors.
2. Creates `ConformerPreProcess` for Mel spectrogram generation.
3. Creates `ConformerPostProcess` for token decoding.
4. Initializes Alif audio at 16 kHz.
5. Waits for `BOARD_BUTTON2`.
6. Captures audio chunks from the PDM microphone path while the button is held.
7. Clamps the audio length so it fits the model input tensor.
8. Runs preprocessing, inference, and postprocessing.
9. Prints `Decoded output: ...` to the UART log.

## Compare the FVP and board applications

The Arm `asr` application you ran on FVP and the Alif `alif_asr` application use the same Conformer-specific pieces:

- Conformer preprocessing, which converts audio samples into Mel spectrogram input.
- Conformer postprocessing, which converts output logits and output lengths into decoded text.
- The ExecuTorch `ConformerModel` wrapper.
- The SentencePiece vocabulary in `resources/asr/labels/librispeech_sp.pieces`.

The Alif application keeps those ASR stages, but changes how the application is built, how audio enters the system, where the model is stored, and how terminal output is routed. The board-specific pieces for the first board run are:

- HP subsystem build with `TARGET_SUBSYSTEM=RTSS-HP`.
- E8 DevKit board selection with `TARGET_BOARD=DevKit-e8`.
- The same Ethos-U85 NPU target selection used on FVP, with Alif-specific board, subsystem, memory, and console settings.
- PDM microphone input with `TARGET_MICS=PDM`.
- UART4 logs with `CONSOLE_UART=4`.
- External OSPI flash placement for the Conformer model.
- MRAM boot configuration for the HP Cortex-M55 core.

The table shows the key changes:

| FVP application | E8 DevKit application | Why it changes |
| --- | --- | --- |
| Model data built into the application image | Model data linked to external OSPI flash | The Conformer model does not fit in Alif MRAM |
| WAV files compiled into firmware | PDM microphone input | The E8 DevKit can capture live voice input on the board |
| Console output | UART4 logs | The board needs a physical terminal output path |
| Corstone-320 FVP memory layout | E8 HP subsystem linker layout | Firmware, activation buffers, temporary ExecuTorch memory, and model storage must fit the board memory map |

{{% notice AUTHOR TODO %}}
Potential extra detail from Alif: this would be a good place for any E8 DevKit-specific notes that are easy to miss when moving from FVP to board, such as boot core selection, UART routing, memory regions, cache settings, or external flash access.
{{% /notice %}}

## Configure memory and model placement

The `alif_asr` CMake file enables external flash model placement by default:

```cmake
USER_OPTION(${use_case}_MODEL_IN_EXT_FLASH "Run model from external flash"
    ON
    BOOL)
```

When this option is enabled, MLEK places model data in the `nn_model_ext_flash` section and generates a separate `ext_flash.bin` file. The MLEK documentation states that `alif_asr` uses external OSPI flash because the model does not fit in MRAM.

For the ExecuTorch Conformer model, `alif_asr` uses:

- Model: `resources_downloaded/asr/conformer_fp32_cln_wer_6_47_arm_delegate_ethos-u85-256.pte`
- Labels: `resources/asr/labels/librispeech_sp.pieces`
- Activation buffer: `0x00108000`
- Temporary ExecuTorch memory in the E8 build command: `0x002C0000`

ExecuTorch uses two memory areas in this flow: the method allocator pool controlled by `alif_asr_ACTIVATION_BUF_SZ`, and the temporary allocation pool controlled by `ML_FWK_TMP_MEM_SIZE`.

## Configure microphone input

Use PDM microphone input for the first board deployment. This matches the default `alif_asr` flow: the application captures live 16 kHz audio, converts it into Mel spectrogram features, runs Conformer inference, and prints decoded text.

LVGL display output is a useful demo addition, but it adds UI code and display setup. Add display output after the microphone-to-terminal flow is working.

{{% notice AUTHOR TODO %}}
Potential extra detail from Alif: it would be useful to clarify whether the E8 DevKit microphone path works out of the box with `TARGET_MICS=PDM`, and to mention any jumper, port, or board revision notes that affect this step.
{{% /notice %}}

{{% notice AUTHOR TODO %}}
Potential extra detail from Alif: a short note on how capture length maps to the Conformer input tensor would help learners who want to use a different microphone path.
{{% /notice %}}

## What you have accomplished and what is next

You have cloned the Alif MLEK repository, prepared its ExecuTorch resources, located the `alif_asr` application, and compared its board-specific code with the FVP application.

Next, you will build the ASR firmware for the E8 DevKit.
