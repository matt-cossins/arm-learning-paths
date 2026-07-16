---
title: (Optional) Add display output
description: Extend the Alif E8 Conformer ASR application with optional LVGL display output.
weight: 7

layout: "learningpathall"
---

## Connect a display

Use the display supported by the Alif LVGL port for the E8 DevKit. The board provides a MIPI LCD display flat-flex connector, and the MLEK LVGL port initializes the display through the Alif `LCD_Panel` and `CDC200` driver path.

The application uses the display for output only: spectrogram, timing, progress, and decoded text.

{{% notice AUTHOR TODO %}}
Potential extra detail from Alif: it would be helpful to name the recommended display module for the E8 DevKit, including part number, cable orientation, connector name, jumper settings, and whether the display needs separate power or backlight setup.
{{% /notice %}}

## Enable the display build

The earlier board build disables the display:

```output
-DGLCD_UI=OFF
```

To try the LVGL display path, rebuild with display output enabled:

```output
-DGLCD_UI=ON
```

Keep the other ASR options the same, including `TARGET_SUBSYSTEM=RTSS-HP`, `TARGET_BOARD=DevKit-e8`, `CONSOLE_UART=4`, `TARGET_MICS=PDM`, and `ML_FRAMEWORK=ExecuTorch`.

## Review the display code

The ExecuTorch ASR handler already contains the display update path:

```output
source/app/use_case/alif_asr/src/UseCaseHandlerEt.cc
```

The handler initializes `ScreenLayout`, writes the header `Conformer ASR (ExecuTorch)`, and updates LVGL objects after each inference.

The display output includes:

- Mel spectrogram image.
- Input duration.
- Inference time.
- Preprocessing and postprocessing time.
- Decoded text.

The shared layout helper is in:

```output
source/lib/mlek/use_case/alif_ui/
```

The Alif LVGL display port is in:

```output
source/hal/source/components/lvgl_port/source/alif/
```

For the default display layout, you should not need to add a new output path. The ASR code already calls:

```cpp
alif::app::ScreenLayoutInit(lvgl_image, sizeof(lvgl_image), LIMAGE_X, LIMAGE_Y, LV_ZOOM, true);
lv_label_set_text_static(alif::app::ScreenLayoutHeaderObject(), "Conformer ASR (ExecuTorch)");
```

After inference, the handler updates the display labels and decoded text:

```cpp
lv_label_set_text_fmt(alif::app::ScreenLayoutLabelObject(1), "Inference time: %.2f ms", ...);
lv_label_set_text(alif::app::ScreenLayoutLabelObject(result_label_idx), decodedResult.c_str());
```

Change this file if you want to alter the text, metrics, progress bar behavior, or spectrogram rendering.

Keep UART logs enabled while modifying display output. The UART line `Decoded output: ...` is the simplest way to check whether the ASR path still works when changing LVGL code.

{{% notice AUTHOR TODO %}}
Potential extra detail from Alif: it would be useful to know whether the current `alif_asr` display code builds and runs as-is when display output is enabled. If any code changes are needed, this section could include a small patch, especially around `ScreenLayoutInit`, `lv_port_disp_init`, display buffer placement, and the LVGL lock usage.
{{% /notice %}}
