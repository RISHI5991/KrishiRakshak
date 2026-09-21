"""ESP32-S3 Production Pest Detector.

Architecture: Inverted-Residual backbone + Lightweight PAN neck + Anchor-free head.
All ops: Conv2d, DepthwiseConv2d, BatchNorm2d, ReLU6, Add, Concat, Resize(nearest).
No SiLU, no Softplus, no exp(), no sigmoid in feature path.
Sigmoid only in final classification output (TFLite natively supports it).

Target: 192×192 input, ~150-250K params, <300KB INT8, <200KB peak activations.
"""
from __future__ import annotations

import math
import torch
import torch.nn as nn
import torch.nn.functional as F


# ─── Building blocks ─────────────────────────────────────────────────────────

class ConvBNReLU6(nn.Module):
    """Standard Conv + BN + ReLU6. ESP32-S3 native via TFLite Micro."""
    def __init__(self, c_in: int, c_out: int, k: int = 3, s: int = 1, g: int = 1):
        super().__init__()
        self.conv = nn.Conv2d(c_in, c_out, k, s, k // 2, groups=g, bias=False)
        self.bn = nn.BatchNorm2d(c_out)
        self.act = nn.ReLU6(inplace=True)

    def forward(self, x):
        return self.act(self.bn(self.conv(x)))


class InvertedResidual(nn.Module):
    """MobileNetV2-style inverted residual — fully TFLite compatible."""
    def __init__(self, c_in: int, c_out: int, stride: int = 1, expand: int = 4):
        super().__init__()
        hidden = c_in * expand
        self.use_res = (stride == 1 and c_in == c_out)
        layers = []
        if expand != 1:
            layers.append(ConvBNReLU6(c_in, hidden, 1))        # expand
        layers.append(ConvBNReLU6(hidden, hidden, 3, stride, g=hidden))  # depthwise
        layers.extend([                                          # project (no activation)
            nn.Conv2d(hidden, c_out, 1, bias=False),
            nn.BatchNorm2d(c_out),
        ])
        self.block = nn.Sequential(*layers)

    def forward(self, x):
        out = self.block(x)
        return x + out if self.use_res else out


class DWSepConv(nn.Module):
    """Depthwise-separable conv with ReLU6."""
    def __init__(self, c_in: int, c_out: int, stride: int = 1):
        super().__init__()
        self.dw = ConvBNReLU6(c_in, c_in, 3, stride, g=c_in)
        self.pw = ConvBNReLU6(c_in, c_out, 1)

    def forward(self, x):
        return self.pw(self.dw(x))


# ─── Backbone ────────────────────────────────────────────────────────────────

class MCUBackbone(nn.Module):
    """Production MCU backbone with inverted residuals.

    Output strides: P3=8, P4=16, P5=32.
    At 192×192 input → P3: 24×24, P4: 12×12, P5: 6×6.
    """
    def __init__(self, width_mult: float = 1.0):
        super().__init__()
        def ch(c):
            return max(8, int(c * width_mult + 0.5) // 8 * 8)  # round to nearest 8

        c0, c1, c2, c3, c4 = ch(16), ch(24), ch(32), ch(64), ch(96)

        # stride 2: 192→96
        self.stem = ConvBNReLU6(3, c0, 3, 2)
        # stride 4: 96→48
        self.stage1 = nn.Sequential(
            InvertedResidual(c0, c1, stride=2, expand=1),
            InvertedResidual(c1, c1, expand=3),
        )
        # stride 8: 48→24 — P3 output
        self.stage2 = nn.Sequential(
            InvertedResidual(c1, c2, stride=2, expand=3),
            InvertedResidual(c2, c2, expand=3),
            InvertedResidual(c2, c2, expand=3),
        )
        # stride 16: 24→12 — P4 output
        self.stage3 = nn.Sequential(
            InvertedResidual(c2, c3, stride=2, expand=4),
            InvertedResidual(c3, c3, expand=4),
            InvertedResidual(c3, c3, expand=4),
        )
        # stride 32: 12→6 — P5 output
        self.stage4 = nn.Sequential(
            InvertedResidual(c3, c4, stride=2, expand=4),
            InvertedResidual(c4, c4, expand=4),
        )

        self.p3_ch = c2
        self.p4_ch = c3
        self.p5_ch = c4

    @property
    def channels(self) -> tuple[int, int, int]:
        return (self.p3_ch, self.p4_ch, self.p5_ch)

    def forward(self, x) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        x = self.stem(x)
        x = self.stage1(x)
        p3 = self.stage2(x)
        p4 = self.stage3(p3)
        p5 = self.stage4(p4)
        return p3, p4, p5


# ─── Neck (Lightweight PAN) ─────────────────────────────────────────────────

class LitePAN(nn.Module):
    """Tiny bidirectional PAN using depthwise-separable convs.

    Top-down: P5→P4→P3 (upsample + add).
    Bottom-up: P3→P4→P5 (downsample + add).
    All lateral convs are 1×1 to align channels.
    """
    def __init__(self, c3: int, c4: int, c5: int, out3: int, out4: int, out5: int):
        super().__init__()
        # Lateral 1×1 convs to unify channels
        self.lat3 = ConvBNReLU6(c3, out3, 1)
        self.lat4 = ConvBNReLU6(c4, out4, 1)
        self.lat5 = ConvBNReLU6(c5, out5, 1)

        # Top-down fusion
        self.td_5to4 = ConvBNReLU6(out5, out4, 1)  # channel align P5→P4
        self.td_4to3 = ConvBNReLU6(out4, out3, 1)  # channel align P4→P3
        self.td_fuse4 = DWSepConv(out4, out4)
        self.td_fuse3 = DWSepConv(out3, out3)

        # Bottom-up fusion
        self.bu_3to4 = DWSepConv(out3, out4, stride=2)  # downsample P3→P4
        self.bu_4to5 = DWSepConv(out4, out5, stride=2)  # downsample P4→P5
        self.bu_fuse4 = DWSepConv(out4, out4)
        self.bu_fuse5 = DWSepConv(out5, out5)

    def forward(self, p3, p4, p5):
        # Lateral
        p3 = self.lat3(p3)
        p4 = self.lat4(p4)
        p5 = self.lat5(p5)

        # Top-down
        td4 = self.td_fuse4(p4 + F.interpolate(self.td_5to4(p5), size=p4.shape[-2:], mode="nearest"))
        td3 = self.td_fuse3(p3 + F.interpolate(self.td_4to3(td4), size=p3.shape[-2:], mode="nearest"))

        # Bottom-up
        bu4 = self.bu_fuse4(td4 + self.bu_3to4(td3))
        bu5 = self.bu_fuse5(p5 + self.bu_4to5(bu4))

        return td3, bu4, bu5


# ─── Detection Head ─────────────────────────────────────────────────────────

class MCUDetHead(nn.Module):
    """Anchor-free detection head for MCU deployment.

    Classification: sigmoid (TFLite native).
    Box regression: ReLU activation → distance decoding (no exp/softplus).
    """
    STRIDES = (8, 16, 32)

    def __init__(self, nc: int, channels: tuple[int, ...]):
        super().__init__()
        self.nc = nc
        self.strides = self.STRIDES

        self.cls_heads = nn.ModuleList()
        self.box_heads = nn.ModuleList()
        for c in channels:
            self.cls_heads.append(nn.Sequential(
                DWSepConv(c, c),
                nn.Conv2d(c, nc, 1),
            ))
            self.box_heads.append(nn.Sequential(
                DWSepConv(c, c),
                nn.Conv2d(c, 4, 1),
            ))

        # Bias init for stable early training
        for m in self.cls_heads:
            nn.init.constant_(m[-1].bias, -math.log((1 - 0.01) / 0.01))

    def forward(self, features: list[torch.Tensor]):
        cls_outs, box_outs = [], []
        for feat, cls_h, box_h in zip(features, self.cls_heads, self.box_heads):
            cls_outs.append(cls_h(feat))
            box_outs.append(box_h(feat))
        return {
            "one2many": {"boxes": box_outs, "scores": cls_outs},
            "one2one": {"boxes": box_outs, "scores": cls_outs},
        }

    @staticmethod
    def _grid(h: int, w: int, stride: int, device, dtype):
        yv, xv = torch.meshgrid(
            torch.arange(h, device=device, dtype=dtype),
            torch.arange(w, device=device, dtype=dtype),
            indexing="ij",
        )
        return torch.stack(((xv + 0.5) * stride, (yv + 0.5) * stride), -1).reshape(-1, 2)

    def decode(self, branch):
        """Decode raw outputs → [x1, y1, x2, y2] boxes + class scores."""
        all_boxes, all_scores = [], []
        for box_raw, cls_raw, stride in zip(branch["boxes"], branch["scores"], self.strides):
            b, _, h, w = box_raw.shape
            grid = self._grid(h, w, stride, box_raw.device, box_raw.dtype)
            # ReLU distance decode: distances must be non-negative
            dist = F.relu(box_raw.permute(0, 2, 3, 1).reshape(b, -1, 4)) * stride
            cx, cy = grid[:, 0], grid[:, 1]
            boxes = torch.stack([
                cx.unsqueeze(0) - dist[..., 0],
                cy.unsqueeze(0) - dist[..., 1],
                cx.unsqueeze(0) + dist[..., 2],
                cy.unsqueeze(0) + dist[..., 3],
            ], dim=-1)
            scores = cls_raw.permute(0, 2, 3, 1).reshape(b, -1, self.nc).sigmoid()
            all_boxes.append(boxes)
            all_scores.append(scores)
        return torch.cat(all_boxes, 1), torch.cat(all_scores, 1)

    @torch.no_grad()
    def predict_from_outputs(self, outputs, conf=0.25, max_det=100):
        boxes, scores = self.decode(outputs["one2one"])
        results = []
        for bi in range(boxes.shape[0]):
            cls_sc, cls_id = scores[bi].max(dim=1)
            keep = cls_sc >= conf
            idx = torch.where(keep)[0]
            if idx.numel() > max_det:
                idx = idx[torch.topk(cls_sc[idx], max_det).indices]
            if idx.numel() == 0:
                results.append(torch.empty((0, 6), device=boxes.device))
                continue
            results.append(torch.cat([
                boxes[bi, idx], cls_sc[idx, None], cls_id[idx, None].float()
            ], dim=1))
        return results


# ─── Complete Model ──────────────────────────────────────────────────────────

class StudentPestDetector(nn.Module):
    """Production ESP32-S3 pest detector.

    Architecture: MCUBackbone (inverted residuals) + LitePAN + MCUDetHead.
    All activations: ReLU6 / ReLU (no SiLU, no Softplus, no exp).
    Designed for 192×192 input.

    ESP32-S3 resource budget:
        Flash: model weights INT8 ≈ 200-300 KB  (budget: 4 MB)
        PSRAM: peak activations   ≈ 100-200 KB  (budget: 2 MB)
        Operators: Conv2D, DepthwiseConv2D, Add, ReLU6, Sigmoid — all in TFLite Micro.
    """
    def __init__(self, num_classes: int = 24, width_mult: float = 1.0):
        super().__init__()
        self.backbone = MCUBackbone(width_mult)
        c3, c4, c5 = self.backbone.channels
        # Neck output channels: keep small
        o3, o4, o5 = max(8, c3 // 2), max(8, c4 // 2), max(8, c5 // 2)
        # Round to multiples of 8 for hardware efficiency
        o3 = (o3 + 7) // 8 * 8
        o4 = (o4 + 7) // 8 * 8
        o5 = (o5 + 7) // 8 * 8
        self.neck = LitePAN(c3, c4, c5, o3, o4, o5)
        self.head = MCUDetHead(num_classes, (o3, o4, o5))
        self.num_classes = num_classes

    def forward(self, x):
        p3, p4, p5 = self.backbone(x)
        f3, f4, f5 = self.neck(p3, p4, p5)
        return self.head([f3, f4, f5])
