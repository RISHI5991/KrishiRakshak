from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import torch

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pest_ml.src.model import DhurandharM3


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--image-size", type=int, default=640)
    ap.add_argument("--batch-size", type=int, default=1)
    args = ap.parse_args()

    dev = torch.device("mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu")
    model = DhurandharM3(24, pretrained_backbone=True).to(dev).eval()
    x = torch.randn(args.batch_size, 3, args.image_size, args.image_size, device=dev)
    params = sum(p.numel() for p in model.parameters())

    with torch.no_grad():
        _ = model(x)
        if dev.type == "mps":
            torch.mps.synchronize()
        elif dev.type == "cuda":
            torch.cuda.synchronize()
        t0 = time.perf_counter()
        for _ in range(20):
            _ = model(x)
        if dev.type == "mps":
            torch.mps.synchronize()
        elif dev.type == "cuda":
            torch.cuda.synchronize()
        elapsed = (time.perf_counter() - t0) / 20

    print("Device:", dev)
    print("Parameters:", f"{params:,}")
    print("Input:", args.batch_size, args.image_size, "x", args.image_size)
    print("Average forward latency (s):", f"{elapsed:.4f}")
    print("Average images/s:", f"{args.batch_size / elapsed:.2f}")


if __name__ == "__main__":
    main()
