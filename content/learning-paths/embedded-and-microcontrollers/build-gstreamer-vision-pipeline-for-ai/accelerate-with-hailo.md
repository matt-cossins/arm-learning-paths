---
title: (Optional) Adapt for use with Hailo Accelerator
weight: 4

### FIXED, DO NOT MODIFY
layout: learningpathall
---

## Run the same workflow on a Hailo accelerator

For this optional step, you need a Hailo accelerator (for example, Raspberry Pi AI Hat+ or AI Hat+ 2). This step assumes you have setup your Pi with an AI Hat and completed the optional steps in the [Install Guide](https://learn.arm.com/install-guides/perception-kit/)

In the previous step, you built a pipeline to leverage the Raspberry Pi 5 CPU. The YOLOv8n model used was in the `.onnx` format, to leverage the ONNX Runtime. The Arm Perception Pipeline Kit also supports other runtimes, including HailoRT, allowing the pipeline to run inference on Hailo accelerators. 

Swapping a pipeline from using the CPU to using a Hailo accelerator is simple to do. You keep the same pipeline structure and switch inference to a Hailo model variant:

1. In your model folder, you swap your `.onnx` model for a `.hef` (Hailo Executable Format) version, and point `model.json` towards it

2. You change the `ampinfer opchain-path=...` to the supported `amp-hailort-ops/Inference`, instead of `amp-onnx-ops/Inference`

3. Postprocess settings can differ for Hailo outputs. For example, YOLO Hailo opchains can use `outputFormat: HailoYoloNMS` and `applyNms: false` because NMS (Non-Maximum Suppression - a post-processing step for object detection models to clean-up overlapping predictions) is already handled in the Hailo output format.

Everything else in your pipeline can remain the same. We run through an example below:

## Obtain a Hailo model

Create a new model folder called `custom-detector-hailo`:

```bash
mkdir -p /work/config/models/custom-detector-hailo
```

The [Hailo Model Zoo](https://github.com/hailo-ai/hailo_model_zoo/tree/master) includes many different models pre-compiled in the `.hef` format, for different Hailo accelerator variants. This learning path will use the Hailo8L variant (present in the 13 TOPs version of the Raspberry Pi AI Hat+), but you can swap this for your variant, e.g. Hailo8, Hailo10, Hailo15.

If needed (i.e. a particular model is not provided in `.hef` already), you can use the Hailo Dataflow Compiler to convert models to `.hef` format.

YOLOv8n, pre-trained for the COCO (Common Objects in Context) dataset can be downloaded in `.hef` [here](https://github.com/hailo-ai/hailo_model_zoo/blob/master/docs/public_models/HAILO8L/HAILO8L_object_detection.rst).

Place it in your `/work/config/models/custom-detector-hailo` folder.

## Create new model.json and opchain.json files

These files are almost entirely unchanged from the CPU variant.

Use the commands below to create Hailo variants in `/work/config/models/custom-detector-hailo`.

Create `model.json`:

```bash
cat > /work/config/models/custom-detector-hailo/model.json <<'EOF'
{
  "name": "custom-detector-hailo",
  "modelFamily": "yolo-obj",
  "modelFile": "yolov8n.hef",
  "dynamicOutput": true,
  "maxDetectionCount": 100,
  "confidenceThreshold": 0.4,
  "iouThreshold": 0.45,
  "inputTensors": [
    {
      "shape": [1, 3, 640, 640],
      "dataKind": "ImageRgbChw"
    }
  ]
}
EOF
```

Create `opchain.json`:

```bash
cat > /work/config/models/custom-detector-hailo/opchain.json <<'EOF'
{
  "name": "Custom detector Hailo",
  "description": "Custom YOLOv8n HEF detector opchain.",
  "ops": [
    {
      "id": "amp-std-ops/InferenceController",
      "attributes": {}
    },
    {
      "id": "amp-std-ops/GenericImagePreprocess",
      "attributes": {
        "inputImageTensorIndex": 0,
        "inputImageSourceName": "pipelineVideoFrame"
      }
    },
    {
      "id": "amp-hailort-ops/Inference",
      "attributes": {
        "modelDescriptor": "/work/config/models/custom-detector-hailo/model.json"
      }
    },
    {
      "id": "amp-std-ops/GenericPostprocess",
      "attributes": {
        "parser": "YoloParser",
        "applyNms": false,
        "outputFormat": "HailoYoloNMS",
        "normalizeOutputCoordinates": false,
        "coordinatesAreNormalized": true,
        "confidenceThreshold": 0.4,
        "maxDetections": 50,
        "classCount": 80,
        "maxBboxesPerClass": 100,
        "coordOrder": "yxyx",
        "debug": false
      }
    }
  ]
}
EOF
```

Compared to the CPU version, the required changes are:

- `modelFile` points to `.hef` instead of `.onnx`.
- Inference op changes to `amp-hailort-ops/Inference`.
- Postprocess uses Hailo NMS output settings.

## Create a Hailo pipeline variant

Create a second pipeline JSON so you can keep the CPU version unchanged:

```bash
cat > /work/config/pipelines/06-custom-detector-hailo.json <<EOF
{
  "description": "Custom detector pipeline using Hailo acceleration.",
  "pipeline": [
    "v4l2src device=/dev/video0 !",
    "videoconvert ! video/x-raw,format=BGRA !",
    "ampinfer opchain-path=/work/config/models/custom-detector-hailo/opchain.json active=true !",
    "amptracker content-type=genericObject !",
    "amposd enabled=true !",
    "ampsink name=sink"
  ]
}
EOF
```

This keeps your pipeline topology identical to CPU mode. The only functional change is the Hailo opchain path.

## Run inference

```bash
./tools/amp-menu 06-custom-detector-hailo
```

Open `http://127.0.0.1:9999` to verify. You should see the same as previously, now running on the Hailo accelerator. Enable the performance overlay to observe differences in performance between CPU and Accelerator mode.

## What you've learned and what's next

You learned the minimal changes needed to move from CPU ONNX inference to Hailo acceleration: use a Hailo model directory and switch to a Hailo opchain path while keeping the rest of the pipeline structure consistent.

Now you will look at integrating pipelines into simple python applications.
