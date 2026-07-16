---
title: Verify ASR inference on the E8 DevKit
description: Run the ASR application on the Alif E8 DevKit and verify that the Conformer model executes on the Ethos-U85 NPU.
weight: 6

layout: "learningpathall"
---

Now, we will run the flashed ASR application and verify that it captures microphone input, runs Conformer inference, and prints decoded text.

## Connect to application output

The `alif_asr` build command selects UART4:

```output
-DCONSOLE_UART=4
```

Connect a serial terminal to the M55-HP debug console selected by the E8 DevKit jumpers. Use the UART settings specified by the Alif board documentation.

{{% notice AUTHOR TODO %}}
Potential extra detail from Alif: it would be helpful to include the UART connection details for the E8 DevKit used in this demo, such as jumper or connector requirements, baud rate, serial device naming examples, and whether RTT or another log path is also supported.
{{% /notice %}}

## Run an ASR input

The board run uses PDM microphone input. Speak a short phrase so you can verify the capture, preprocessing, inference, and decoding path.

To run a test:

1. Reset the board.
2. Connect to the terminal output.
3. Press and hold `BOARD_BUTTON2`.
4. Speak a short phrase.
5. Release the button.

The application captures audio while the button is held, preprocesses it into a Mel spectrogram, runs the Conformer model, decodes the output tokens, and prints the result.

On the UART log, look for a line like:

```output
Decoded output: <recognized text>
```

## Confirm the Ethos-U85 path executed

{{% notice AUTHOR TODO %}}
Potential extra detail from Alif: a concrete board-side check would be useful here, such as a specific log line, profiler output, PMU counter, or expected timing range for the published model and board configuration.
{{% /notice %}}

## Troubleshooting

Check these symptoms:

- No UART output: confirm the M55-HP debug UART and `CONSOLE_UART=4` connection.
- Model load failure: confirm `ext_flash.bin` was flashed to `0xC0000000`.
- Boot failure: confirm `mram.bin` was flashed with `alif_asr.json` and `M55_HP`.
- Empty or silent audio: confirm `TARGET_MICS=PDM`, the microphone path, and that `BOARD_BUTTON2` is held while speaking.
- Allocation failure: confirm `ML_FWK_TMP_MEM_SIZE=0x002C0000` and the default `alif_asr_ACTIVATION_BUF_SZ=0x00108000`.

## What you have accomplished and what is next

You have run the ASR application on the E8 DevKit and verified that the Conformer model executes on the Ethos-U85 NPU.

Next, you can add display output to turn the terminal-based application into a board demo.
