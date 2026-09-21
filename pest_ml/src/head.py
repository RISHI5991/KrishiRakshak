from __future__ import annotations

import math

import torch
import torch.nn as nn
import torch.nn.functional as F


class ConvBNAct(nn.Module):
    def __init__(self, in_channels: int, out_channels: int, kernel_size: int = 1, groups: int = 1) -> None:
        super().__init__()
        if in_channels % groups != 0 or out_channels % groups != 0:
            raise ValueError("groups must divide channels")
        self.block = nn.Sequential(
            nn.Conv2d(
                in_channels,
                out_channels,
                kernel_size,
                padding=kernel_size // 2,
                groups=groups,
                bias=False,
            ),
            nn.BatchNorm2d(out_channels),
            nn.SiLU(inplace=True),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.block(x)


class SeparableTower(nn.Module):
    def __init__(self, channels: int, depth: int = 2) -> None:
        super().__init__()
        layers = []
        for _ in range(depth):
            layers.extend(
                [
                    ConvBNAct(channels, channels, 3, groups=channels),
                    ConvBNAct(channels, channels, 1),
                ]
            )
        self.block = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.block(x)


class M3DetectHead(nn.Module):
    """Independent YOLO26-inspired, DFL-free, P2/P3/P4 detector head.

    One shared prediction tower feeds both branches. Only the final box/class
    projections are separate. During training the one-to-one branch receives
    detached features; inference uses only the one-to-one branch.
    """

    def __init__(self, nc: int, channels: tuple[int, int, int] = (48, 96, 128)) -> None:
        super().__init__()
        self.nc = nc
        self.strides = (4, 8, 16)
        self.reg_max = 1

        self.towers = nn.ModuleList([SeparableTower(c, depth=2) for c in channels])
        self.box_many = nn.ModuleList([nn.Conv2d(c, 4, 1) for c in channels])
        self.cls_many = nn.ModuleList([nn.Conv2d(c, nc, 1) for c in channels])
        self.box_one = nn.ModuleList([nn.Conv2d(c, 4, 1) for c in channels])
        self.cls_one = nn.ModuleList([nn.Conv2d(c, nc, 1) for c in channels])

        self._init_biases()

    def _init_biases(self) -> None:
        prior = 0.01
        cls_bias = math.log(prior / (1 - prior))
        for heads in (self.cls_many, self.cls_one):
            for layer in heads:
                nn.init.constant_(layer.bias, cls_bias)
        for heads in (self.box_many, self.box_one):
            for layer in heads:
                # Initialize distance to ~2 pixels (better for tiny pests than 8)
                nn.init.constant_(layer.bias, math.log(math.expm1(2.0)))

    def _branch(
        self,
        features: list[torch.Tensor],
        box_heads: nn.ModuleList,
        cls_heads: nn.ModuleList,
    ) -> dict[str, list[torch.Tensor]]:
        boxes, scores = [], []
        for feat, box_head, cls_head, tower in zip(features, box_heads, cls_heads, self.towers):
            y = tower(feat)
            boxes.append(box_head(y))
            scores.append(cls_head(y))
        return {"boxes": boxes, "scores": scores, "features": features}

    def forward(self, features: list[torch.Tensor]) -> dict[str, dict[str, list[torch.Tensor]]]:
        one2many = self._branch(features, self.box_many, self.cls_many)
        detached = [x.detach() for x in features]
        one2one = self._branch(detached, self.box_one, self.cls_one)
        return {"one2many": one2many, "one2one": one2one}

    @staticmethod
    def points_for(
        h: int,
        w: int,
        stride: int,
        device: torch.device,
        dtype: torch.dtype,
    ) -> torch.Tensor:
        y, x = torch.meshgrid(
            torch.arange(h, device=device, dtype=dtype),
            torch.arange(w, device=device, dtype=dtype),
            indexing="ij",
        )
        return torch.stack(((x + 0.5) * stride, (y + 0.5) * stride), dim=-1).reshape(-1, 2)

    def decode_branch(
        self,
        branch: dict[str, list[torch.Tensor]],
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        boxes, scores, points, strides = [], [], [], []
        for level, (box_logits, cls_logits, stride) in enumerate(
            zip(branch["boxes"], branch["scores"], self.strides)
        ):
            b, _, h, w = box_logits.shape
            pts = self.points_for(h, w, stride, box_logits.device, box_logits.dtype)
            d = F.softplus(box_logits.permute(0, 2, 3, 1)).reshape(b, -1, 4) * stride
            cx, cy = pts[:, 0], pts[:, 1]
            decoded = torch.stack(
                [cx.view(1, -1) - d[..., 0], cy.view(1, -1) - d[..., 1],
                 cx.view(1, -1) + d[..., 2], cy.view(1, -1) + d[..., 3]],
                dim=-1,
            )
            boxes.append(decoded)
            scores.append(cls_logits.permute(0, 2, 3, 1).reshape(b, -1, self.nc).sigmoid())
            points.append(pts)
            strides.append(torch.full((pts.shape[0],), stride, device=box_logits.device, dtype=box_logits.dtype))
        return torch.cat(boxes, 1), torch.cat(scores, 1), torch.cat(points, 0), torch.cat(strides, 0)

    @torch.no_grad()
    def predict_from_outputs(
        self,
        outputs: dict[str, dict[str, list[torch.Tensor]]],
        conf: float = 0.05,
        max_det: int = 300,
    ) -> list[torch.Tensor]:
        branch = outputs["one2one"]
        boxes, scores, _, _ = self.decode_branch(branch)
        results = []
        for b in range(boxes.shape[0]):
            cls_scores, cls_ids = scores[b].max(dim=1)
            keep = cls_scores >= conf
            idx = torch.where(keep)[0]
            if idx.numel() > max_det:
                vals = cls_scores[idx]
                idx = idx[torch.topk(vals, max_det).indices]
            if idx.numel() == 0:
                results.append(torch.empty((0, 6), device=boxes.device, dtype=boxes.dtype))
                continue
            det = torch.cat(
                [boxes[b, idx], cls_scores[idx, None], cls_ids[idx, None].to(boxes.dtype)],
                dim=1,
            )
            results.append(det)
        return results

    @torch.no_grad()
    def predict(
        self,
        features: list[torch.Tensor],
        conf: float = 0.05,
        max_det: int = 300,
    ) -> list[torch.Tensor]:
        outputs = self.forward(features)
        return self.predict_from_outputs(outputs, conf=conf, max_det=max_det)
