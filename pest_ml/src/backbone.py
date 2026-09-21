from __future__ import annotations

import torch
import torch.nn as nn
import timm


class MobileNetV4Backbone(nn.Module):
    """MobileNetV4-ConvSmall feature extractor exposing P2/P3/P4."""

    def __init__(
        self,
        model_name: str = "mobilenetv4_conv_small.e2400_r224_in1k",
        pretrained: bool = True,
    ) -> None:
        super().__init__()
        self.backbone = timm.create_model(
            model_name,
            pretrained=pretrained,
            features_only=True,
        )

        reductions = list(self.backbone.feature_info.reduction())
        channels = list(self.backbone.feature_info.channels())

        indices = {}
        for idx, reduction in enumerate(reductions):
            if reduction in (4, 8, 16):
                indices[reduction] = idx

        missing = [r for r in (4, 8, 16) if r not in indices]
        if missing:
            raise RuntimeError(
                f"MobileNetV4 backbone is missing reductions {missing}; "
                f"available reductions={reductions}"
            )

        self.p2_index = indices[4]
        self.p3_index = indices[8]
        self.p4_index = indices[16]

        self.p2_channels = int(channels[self.p2_index])
        self.p3_channels = int(channels[self.p3_index])
        self.p4_channels = int(channels[self.p4_index])

    @property
    def feature_channels(self) -> tuple[int, int, int]:
        return self.p2_channels, self.p3_channels, self.p4_channels

    def forward(
        self, x: torch.Tensor
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        features = self.backbone(x)
        return (
            features[self.p2_index],
            features[self.p3_index],
            features[self.p4_index],
        )
