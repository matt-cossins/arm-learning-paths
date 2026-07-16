---
title: Build and flash the ASR firmware
description: Build the Alif MLEK `alif_asr` firmware and flash the model assets and firmware image to the Alif Ensemble E8 DevKit.
weight: 5

layout: "learningpathall"
---

## Configure the firmware build

From the Alif MLEK repository root, create a build directory:

```bash
mkdir build_alif_asr
cd build_alif_asr
```

Configure the firmware build:

This command builds the microphone-input, terminal-output board run. Display output is added later.

```bash
cmake -DML_FWK_TMP_MEM_SIZE=0x002C0000 -DTARGET_PLATFORM=alif \
-DUSE_CASE_BUILD=alif_asr -DTARGET_SUBSYSTEM=RTSS-HP -DTARGET_BOARD=DevKit-e8 \
-DCMAKE_TOOLCHAIN_FILE=scripts/cmake/toolchains/bare-metal-gcc.cmake \
-DGLCD_UI=OFF -DLINKER_SCRIPT_NAME=RTSS-HP -DCMAKE_BUILD_TYPE=Release \
-DMLEK_LOG_LEVEL=MLEK_LOG_LEVEL_INFO -DETHOS_U_NPU_ID=U85 -DCONSOLE_UART=4 \
-DTARGET_MICS=PDM -DML_FRAMEWORK=ExecuTorch ..
```

The key options are:

- `USE_CASE_BUILD=alif_asr`
- `TARGET_SUBSYSTEM=RTSS-HP`
- `TARGET_BOARD=DevKit-e8`
- `ML_FRAMEWORK=ExecuTorch`
- `ML_FWK_TMP_MEM_SIZE=0x002C0000`
- `ETHOS_U_NPU_ID=U85`
- `CONSOLE_UART=4`
- `TARGET_MICS=PDM`
- `GLCD_UI=OFF`

`alif_asr` selects the Conformer model, vocabulary, and activation buffer from `source/app/use_case/alif_asr/usecase.cmake`.

{{% notice AUTHOR TODO %}}
Potential extra detail from Alif: it would be useful to add context for the build options that may not be obvious from CMake alone: why `RTSS-HP` is used, why UART4 is selected, how `ML_FWK_TMP_MEM_SIZE` and the activation buffer size were chosen, and how `TARGET_MICS=PDM` maps to the E8 DevKit microphone hardware. To explain what choices were important and any where alternative options could easily have been made.
{{% /notice %}}

## Build the target

Build the ASR target:

```bash
make mlek_alif_asr -j4
```

## Inspect the output binaries

Inspect the generated sector binaries:

```bash
ls -lh bin/sectors/alif_asr/
```

You should see:

```output
ext_flash.bin
mram.bin
```

- `ext_flash.bin`: model and other large assets flashed to external OSPI flash.
- `mram.bin`: application firmware flashed to MRAM.

## Flash external OSPI flash

Use SEGGER J-Link with J-Flash to flash `ext_flash.bin` to external OSPI flash.

In J-Flash, load:

```output
bin/sectors/alif_asr/ext_flash.bin
```

Use external flash start address:

```output
0xC0000000
```

{{% notice AUTHOR TODO %}}
Potential extra detail from Alif: it would be helpful to confirm the external flash workflow that is easiest for learners to follow. If J-Link/J-Flash is the preferred path, the final version could include the device selection, connection settings, erase requirements, and expected success output. If the SD-to-OSPI or USB-to-OSPI flow is preferred, that flow could replace the J-Link/J-Flash steps.
{{% /notice %}}

## Flash MRAM

The repository includes `alif_asr.json` for the HP ASR application:

```bash
cp ../alif_asr.json /path/to/app-release-exec-linux/build/config/alif_asr.json
cp bin/sectors/alif_asr/mram.bin /path/to/app-release-exec-linux/build/images/
```

The JSON file uses:

```json
{
    "HP_asr": {
        "binary": "mram.bin",
        "version": "1.0.0",
        "mramAddress": "0x80008000",
        "cpu_id": "M55_HP",
        "flags": ["boot"],
        "signed": false
    },
    "DEVICE": {
        "disabled": false,
        "binary": "app-device-config.json",
        "version": "0.5.00",
        "signed": true
    }
}
```

From the SETOOLS directory, generate the application table of contents and write MRAM:

```bash
./app-gen-toc -f build/config/alif_asr.json
sudo ./app-write-mram -p
```

The `-p` option pads binaries to a 16-byte boundary if needed.

{{% notice AUTHOR TODO %}}
Potential extra detail from Alif: Any recovery tips for an incorrect boot flag, stale device configuration, or failed MRAM write would be useful.
{{% /notice %}}

## Reset and boot the application

Reset or power-cycle the E8 DevKit after flashing MRAM and external OSPI flash.

## Troubleshooting

Check these items if the application does not boot or cannot load the model:

- `ext_flash.bin` was flashed at `0xC0000000`.
- `mram.bin` came from `bin/sectors/alif_asr/`.
- `alif_asr.json` uses `cpu_id` `M55_HP`.
- `alif_asr.json` uses `mramAddress` `0x80008000`.
- The `DEVICE` entry points to the correct `app-device-config.json` for your board.
- The board enumerates on the expected SEUART port for SETOOLS.

## What you have accomplished and what is next

You have built `mlek_alif_asr` and flashed the Conformer model assets and application firmware to the E8 DevKit.

Next, you will verify the application output.
