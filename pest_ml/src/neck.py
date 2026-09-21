from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F


class ConvBNAct(nn.Module):
    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        kernel_size: int = 1,
        stride: int = 1,
        groups: int = 1,
    ) -> None:
        super().__init__()
        if in_channels % groups != 0 or out_channels % groups != 0:
            raise ValueError("groups must divide both channel counts")
        self.block = nn.Sequential(
            nn.Conv2d(
                in_channels,
                out_channels,
                kernel_size,
                stride,
                kernel_size // 2,
                groups=groups,
                bias=False,
            ),
            nn.BatchNorm2d(out_channels),
            nn.SiLU(inplace=True),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.block(x)


class DepthwiseSeparable(nn.Module):
    def __init__(self, channels: int, expansion: int = 1) -> None:
        super().__init__()
        hidden = channels * expansion
        self.expand = ConvBNAct(channels, hidden, 1) if expansion != 1 else nn.Identity()
        self.dw = ConvBNAct(hidden, hidden, 3, groups=hidden)
        self.project = ConvBNAct(hidden, channels, 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        y = self.project(self.dw(self.expand(x)))
        return x + y


class DownsampleDW(nn.Module):
    def __init__(self, in_channels: int, out_channels: int) -> None:
        super().__init__()
        self.dw = ConvBNAct(in_channels, in_channels, 3, stride=2, groups=in_channels)
        self.pw = ConvBNAct(in_channels, out_channels, 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.pw(self.dw(x))


class LitePicoPAN(nn.Module):
    """Lightweight bidirectional P2/P3/P4 feature fusion."""

    def __init__(
        self,
        p2_channels: int,
        p3_channels: int,
        p4_channels: int,
        f2_channels: int = 48,
        f3_channels: int = 96,
        f4_channels: int = 128,
    ) -> None:
        super().__init__()
        self.f2_channels = f2_channels
        self.f3_channels = f3_channels
        self.f4_channels = f4_channels

        self.lat2 = ConvBNAct(p2_channels, f2_channels, 1)
        self.lat3 = ConvBNAct(p3_channels, f3_channels, 1)
        self.lat4 = ConvBNAct(p4_channels, f4_channels, 1)

        self.top3 = nn.Sequential(
            ConvBNAct(f3_channels + f4_channels, f3_channels, 1),
            DepthwiseSeparable(f3_channels),
        )
        self.top2 = nn.Sequential(
            ConvBNAct(f2_channels + f3_channels, f2_channels, 1),
            DepthwiseSeparable(f2_channels),
        )

        self.down2 = DownsampleDW(f2_channels, f3_channels)
        self.bottom3 = nn.Sequential(
            ConvBNAct(f3_channels + f3_channels, f3_channels, 1),
            DepthwiseSeparable(f3_channels),
        )

        self.down3 = DownsampleDW(f3_channels, f4_channels)
        self.bottom4 = nn.Sequential(
            ConvBNAct(f4_channels + f4_channels, f4_channels, 1),
            DepthwiseSeparable(f4_channels),
        )

    def forward(
        self,
        p2: torch.Tensor,
        p3: torch.Tensor,
        p4: torch.Tensor,
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        p2 = self.lat2(p2)
        p3 = self.lat3(p3)
        p4 = self.lat4(p4)

        p4_to_p3 = F.interpolate(p4, size=p3.shape[-2:], mode="nearest")
        f3 = self.top3(torch.cat((p3, p4_to_p3), dim=1))

        f3_to_p2 = F.interpolate(f3, size=p2.shape[-2:], mode="nearest")
        f2 = self.top2(torch.cat((p2, f3_to_p2), dim=1))

        f2_to_p3 = self.down2(f2)
        f3 = self.bottom3(torch.cat((f3, f2_to_p3), dim=1))

        f3_to_p4 = self.down3(f3)
        f4 = self.bottom4(torch.cat((p4, f3_to_p4), dim=1))

        return f2, f3, f4
