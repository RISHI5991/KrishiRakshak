from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import torch
from torch.utils.data import DataLoader
from tqdm import tqdm

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pest_ml.src.dataset import Pest24Dataset, pest24_collate
from pest_ml.src.metrics import evaluate_predictions
from pest_ml.src.model import DhurandharM3

NAMES = [
    "Bollworm", "Meadow borer", "Gryllotalpa orientalis", "Little Gecko",
    "Agriotes fuscicollis Miwa", "Nematode trench", "Athetis lepigone",
    "Scotogramma trifolii Rottemberg", "Armyworm", "Spodoptera cabbage",
    "Anomala corpulenta", "Spodoptera exigua", "Plutella xylostella",
    "holotrichia parallela", "Rice planthopper", "Yellow tiger", "Land tiger",
    "eight-character tiger", "holotrichia oblita", "Stem borer", "Striped rice bore",
    "Rice Leaf Roller", "Spodoptera litura", "Melahotus",
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint", type=Path, required=True)
    ap.add_argument("--split", choices=["val", "test"], default="test")
    ap.add_argument("--batch-size", type=int, default=2)
    ap.add_argument("--image-size", type=int, default=640)
    ap.add_argument("--conf", type=float, default=0.05)
    args = ap.parse_args()

    dev = torch.device("mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu")
    manifest = PROJECT_ROOT / f"pest_ml/manifests/pest24_{args.split}.txt"
    ds = Pest24Dataset(manifest, args.image_size, False)
    loader = DataLoader(ds, batch_size=args.batch_size, shuffle=False, num_workers=0, pin_memory=False, collate_fn=pest24_collate)

    model = DhurandharM3(24, pretrained_backbone=False).to(dev)
    ckpt = torch.load(args.checkpoint, map_location="cpu")
    model.load_state_dict(ckpt["model_state_dict"], strict=True)
    model.eval()

    predictions, targets = [], []
    with torch.no_grad():
        for images, batch_targets, _ in tqdm(loader, desc=f"EVAL {args.split}"):
            images = images.to(dev)
            outputs = model(images)
            predictions.extend(model.head.predict_from_outputs(outputs, conf=args.conf, max_det=300))
            targets.extend([t.cpu() for t in batch_targets])

    metrics = evaluate_predictions(predictions, targets, 24)
    print(json.dumps(metrics, indent=2))
    with (PROJECT_ROOT / "pest_ml/results" / f"evaluation_{args.split}.json").open("w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)


if __name__ == "__main__":
    main()
