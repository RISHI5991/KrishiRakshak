from __future__ import annotations

import sys
from pathlib import Path

import torch

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pest_ml.src.dataset import Pest24Dataset
from pest_ml.src.loss import M3Loss
from pest_ml.src.model import DhurandharM3


def main():
    dev = torch.device("mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu")
    ds = Pest24Dataset(PROJECT_ROOT / "pest_ml/manifests/pest24_train.txt", 640, True)
    model = DhurandharM3(24, True).to(dev)
    model.train()
    x, targets, _ = ds[0]
    x = x.unsqueeze(0).to(dev)
    out = model(x)
    loss = M3Loss(24, 640)(out, [targets])
    loss["loss"].backward()
    print("Device:", dev)
    print("Image:", tuple(x.shape))
    print("Targets:", tuple(targets.shape))
    print("Loss:", float(loss["loss"].detach().cpu()))
    print("Positives:", loss["positive_assignments"])
    print("M3 final forward/loss/backward smoke test PASSED")


if __name__ == "__main__":
    main()
