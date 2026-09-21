from __future__ import annotations

import torch
import torch.nn as nn
import timm


MODEL_NAME = "mobilenetv4_conv_small.e2400_r224_in1k"


class DhurandharVision(nn.Module):

    def __init__(
        self,
        num_m1_classes: int = 15,
        num_m2_classes: int = 38,
        dropout: float = 0.30,
        pretrained: bool = True,
    ):
        super().__init__()

        self.backbone = timm.create_model(
            MODEL_NAME,
            pretrained=pretrained,
            num_classes=0,
        )

        # Verified empirically for this exact timm checkpoint:
        # backbone(x) -> [batch, 1280]
        self.feature_dim = 1280

        self.m1_head = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(
                self.feature_dim,
                num_m1_classes,
            ),
        )

        self.m2_head = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(
                self.feature_dim,
                num_m2_classes,
            ),
        )

    def forward(
        self,
        x: torch.Tensor,
    ):
        features = self.backbone(x)

        m1_logits = self.m1_head(features)
        m2_logits = self.m2_head(features)

        return m1_logits, m2_logits