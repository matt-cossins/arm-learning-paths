# Copyright 2026 Arm Limited and/or its affiliates.
# SPDX-License-Identifier: Apache-2.0
"""TinyCNN variant with Ethos-U, CMSIS-NN, and portable execution paths."""

import torch
from torch import nn

# NHWC, the layout of a camera frame, which the Ethos-U reads as it is. An NCHW
# input costs one more NPU operation that reorders it before the first
# convolution.
INPUT_SHAPE = (1, 16, 16, 3)


class TinyCNN(nn.Module):
    def __init__(self, input_shape: tuple[int, ...] = INPUT_SHAPE, num_classes: int = 10) -> None:
        super().__init__()
        channels = input_shape[-1]
        self.conv1 = nn.Conv2d(
            channels, 4, kernel_size=3, stride=1, padding=1, bias=False
        )
        self.conv2 = nn.Conv2d(
            4, num_classes, kernel_size=3, stride=4, padding=1, bias=False
        )

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        # Camera input is NHWC; convolutions use NCHW.
        values = inputs.permute(0, 3, 1, 2)
        values = torch.relu(self.conv1(values))
        values = self.conv2(values)

        # Keep one maximum spatial response for each of the ten output channels.
        values = torch.flatten(values, start_dim=2)
        values, _ = torch.topk(values, k=1, dim=-1)
        return values.squeeze(-1)


def get_model(input_shape: tuple[int, ...] = INPUT_SHAPE) -> nn.Module:
    # Fixed seed: the example uses untrained (random) weights, and a fixed seed
    # keeps the exported program identical from one export to the next (the
    # C array also embeds the Vela options, so the same working directory is
    # part of that guarantee).
    torch.manual_seed(0)
    return TinyCNN(input_shape).eval()


def get_calibration_inputs(
    input_shape: tuple[int, ...] = INPUT_SHAPE, calibration_samples: int = 2
) -> list[torch.Tensor]:
    """Float samples for quantization calibration; the first one is also the export example.

    Fixed values keep the quantization parameters, and with them the output
    logits in the README, the same from one export to the next. Replace them
    with representative, preprocessed data when calibrating a trained model.
    """
    samples = [torch.full(input_shape, 0.5), torch.full(input_shape, -0.5)][:calibration_samples]
    for i in range(len(samples), calibration_samples):
        samples.append(torch.randn(input_shape, generator=torch.Generator().manual_seed(i)))
    return samples
