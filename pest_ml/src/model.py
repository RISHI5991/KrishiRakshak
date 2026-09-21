from __future__ import annotations

import torch
import torch.nn as nn

from .backbone import MobileNetV4Backbone
from .neck import LitePicoPAN
from .head import M3DetectHead


class DhurandharM3(nn.Module):
    """M3: MobileNetV4 + lightweight Pico/CSPPAN-style neck + YOLO26-inspired head."""

    def __init__(self, num_classes: int = 24, pretrained_backbone: bool = True) -> None:
        super().__init__()
        self.backbone = MobileNetV4Backbone(pretrained=pretrained_backbone)
        self.neck = LitePicoPAN(*self.backbone.feature_channels, 48, 96, 128)
        self.head = M3DetectHead(num_classes, (48, 96, 128))
        self.num_classes = num_classes

    def forward(self, x: torch.Tensor):
        p2, p3, p4 = self.backbone(x)
        f2, f3, f4 = self.neck(p2, p3, p4)
        return self.head([f2, f3, f4])
