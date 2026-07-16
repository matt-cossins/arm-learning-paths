---
title: Get started with Conformer ASR and MLEK
description: Review the ASR flow, clone the Arm MLEK repository, and generate the ExecuTorch Conformer model resources used by the FVP application.
weight: 2

layout: "learningpathall"
---

## What is automatic speech recognition?

Automatic speech recognition (ASR) converts speech audio into text. The application you run first reads fixed 16 kHz audio, converts the samples into Mel spectrogram features, runs a Conformer model, and decodes the output tokens into text.

[Conformer](https://github.com/sooftware/conformer/) is a transformer-based neural network architecture used for speech tasks. It combines attention layers, which help the model use context from different parts of an utterance, with convolution layers, which help capture local audio patterns.

The Conformer model in this flow does not take raw audio directly. Preprocessing code creates an 80-bin Mel spectrogram using a 512-sample window and 160-sample hop. The postprocessing code then removes repeated tokens and maps token IDs to text using the SentencePiece vocabulary.

The SentencePiece vocabulary is the token list used by the decoder. The model outputs token IDs, not finished words, and the vocabulary maps each ID to a text piece such as a letter, word fragment, or word-start marker.

## The ML Embedded Evaluation Kit

The ML Embedded Evaluation Kit (MLEK) is a set of embedded machine learning examples, build scripts, model resources, and deployment flows for Arm-based microcontroller systems. 

Ethos-U85 is an Arm NPU for accelerating neural networks in high-performance microcontroller designs, and is a primary target for the MLEK. Conformer is a good fit for this target because ASR depends on both local sound patterns and longer-range speech context. In this flow, the model is exported as an ExecuTorch `.pte` file so supported operations can run on the Ethos-U85 NPU instead of only on the Cortex-M CPU.

Before using the physical Alif E8 DevKit, you run the ASR application on the Corstone-320 Fixed Virtual Platform (FVP). An FVP is a software model of an Arm system that can run the same baremetal firmware you later port and deploy to hardware. Corstone-320 includes an Ethos-U85 target, so you can prototype and debug the model, runtime, and application flow before porting the application to the Alif board.

## What you'll do in this section

You will review the ASR and MLEK flow, clone the Arm MLEK repository, initialize submodules, and run the ExecuTorch resource setup script that prepares the Conformer model assets.

## Clone the Arm MLEK repository

Clone the Arm ML Embedded Evaluation Kit repository:

```bash
git clone https://gitlab.arm.com/artificial-intelligence/ethos-u/ml-embedded-evaluation-kit.git
cd ml-embedded-evaluation-kit
git submodule update --init --recursive
```

{{% notice AUTHOR TODO %}}
This draft uses Arm MLEK commit `f2f6247a672794ecf9df0216d14c3a5c324537dd`. Before publication, consider pinning a commit if the generated model names or FVP build commands need to remain stable.
{{% /notice %}}

## Set up ExecuTorch resources

Run the setup script with ExecuTorch enabled:

```bash
python3 set_up_default_resources.py --ml-frameworks executorch
```

This step can take about 30-40 minutes.

## How are the ExecuTorch .pte files generated?

The setup script is a wrapper around the MLEK resource pipeline. For the ASR use case, it does three jobs:

1. Creates a Python virtual environment in `resources_downloaded/env`.
2. Downloads the Conformer checkpoint into `resources_downloaded/asr/`.
3. Runs the ASR lowering script to create ExecuTorch `.pte` files for the configured targets.

The ASR resource entry in `resources/use_case_resources.json` tells MLEK which checkpoint to download and which lowering script to run.

The `requirements.txt` file installs the Conformer Python package used by the generator. The generator then recreates the model architecture, loads the trained FP32 weights, and switches the model to inference mode:

```python
model = Conformer(
    num_classes=129,
    input_dim=NUM_MELS,
    encoder_dim=144,
    num_encoder_layers=16,
    num_attention_heads=4,
    # Other hyperparameters omitted.
)

checkpoint = torch.load(checkpoint_path, map_location=device, weights_only=True)
model.load_state_dict(checkpoint["model"])
model.eval()
```

The script creates example inputs with the same shape expected by the embedded application: one tensor for Mel spectrogram features, and one tensor for the input length:

```python
example_inputs = (
    torch.rand(1, CHUNK_SIZE, NUM_MELS),
    torch.tensor([CHUNK_SIZE], dtype=torch.int32),
)
```

Next, PyTorch exports the model with `torch.export`. This produces an exported program that ExecuTorch can lower:

```python
exported_program = export(
    load_model(checkpoint_path), example_inputs, strict=True
)
graph_module = exported_program.module(check_guards=False)
```

For Ethos-U targets, the script prepares the graph for post-training quantization using the ExecuTorch Arm backend's `EthosUQuantizer`. It calibrates the graph by running the model over the WAV files in `resources/asr/samples/`, using the same log Mel spectrogram preprocessing as the application:

```python
quantizer = EthosUQuantizer(compile_spec)
quantizer.set_global(get_symmetric_quantization_config(is_per_channel=True))

quantized_graph_module = prepare_pt2e(graph_module, quantizer)
for sample in list(audio_samples_dir.glob("*.wav")):
    audio_tensor = preprocess_audio(sample)
    quantized_graph_module(audio_tensor, chunk_tensor)

quantized_graph_module = convert_pt2e(quantized_graph_module)
```

After calibration and conversion, the generator exports the quantized graph again and creates an Ethos-U partitioner. The partitioner marks the parts of the graph that can be delegated to the Ethos-U backend:

```python
partitioner = EthosUPartitioner(compile_spec)
exported_program = export(quantized_graph_module, example_inputs, strict=True)
```

Finally, ExecuTorch lowers the exported program to the edge form, applies the Ethos-U partitioner, converts the result to an ExecuTorch program, and writes the `.pte` file:

```python
edge_program_manager = to_edge_transform_and_lower(
    exported_program,
    partitioner=[partitioner],
    compile_config=EdgeCompileConfig(_check_ir_validity=False),
)

save_pte_program(
    edge_program_manager.to_executorch(
        config=ExecutorchBackendConfig(extract_delegate_segments=False)
    ),
    str(output),
)
```

- The `.pte` model file contains the ExecuTorch program that runs the Conformer network.
- The `.pieces` vocabulary file contains the text tokens used to decode the model output.

At runtime, the application converts audio into Mel spectrogram features, runs the `.pte` model, and then uses the vocabulary file to turn model output IDs into text.

The vocab file is a line-by-line token list. During postprocessing, the decoder uses the model output value as an index into this list.

Each entry is a piece of text. Some pieces are single letters, some are word fragments, and some represent common words or word starts. SentencePiece uses the `▁` marker to represent a word boundary, so `▁the` means the token starts a new word.

## (Optional) Run these steps manually

If you want to run these steps manually, you can start from the original [FP32 implementation of the Conformer](https://github.com/sooftware/conformer/), train the model on a LibriSpeech dataset from torchaudio, and perform Post-Training Quantization (PTQ) to convert from FP32 to INT8, with instructions here: [PyTorch Conformer Train and Quantize](https://github.com/Arm-Examples/ML-examples/tree/main/pytorch-conformer-train-quantize). For more detail, check out the [End-to-end INT8 Conformer on Arm blog](https://developer.arm.com/community/arm-community-blogs/b/internet-of-things-blog/posts/end-to-end-int8-conformer-on-arm-training-quantization-and-deployment-on-ethos-u85).

Alternatively, you can use the exported INT8 Quantized Conformer model, provided by Arm on Hugging Face: [INT8 Conformer](https://huggingface.co/Arm/stt_en_conformer_executorch_small).

Once you have obtained an exported INT8 Conformer model, you will need to lower to ExecuTorch `.pte` format using the `to_edge_transform_and_lower` API. Instructions can be found at the Hugging Face link.

## What you have accomplished and what is next

You have reviewed how the Conformer ASR application fits into MLEK, cloned the Arm MLEK repository, and generated the ExecuTorch `.pte` model and vocabulary resources used by the FVP application.

Next, you will build and run the ASR application on the Corstone-320 FVP.
