"""Train StudentPestDetector directly on Pest24 without distillation.

This is the fastest path to an ESP32-S3 deployable model.
The student model architecture is a lightweight inverted-residual network
with a LitePAN neck and anchor-free head, fitting within 300KB INT8.
"""
from __future__ import annotations

import argparse
import copy
import json
import math
import random
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR
from torch.utils.data import DataLoader
from tqdm import tqdm

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pest_ml.src.dataset import Pest24Dataset, pest24_collate
from pest_ml.src.loss import M3Loss
from pest_ml.src.metrics import evaluate_predictions
from pest_ml.src.student import StudentPestDetector


class ModelEMA:
    def __init__(self, model, decay=0.9999):
        self.ema = copy.deepcopy(model).eval()
        self.updates = 0
        self.base_decay = decay
        for p in self.ema.parameters():
            p.requires_grad_(False)

    def update(self, model):
        self.updates += 1
        d = self.base_decay * (1 - math.exp(-self.updates / 2000))
        with torch.no_grad():
            msd = model.state_dict()
            for k, v in self.ema.state_dict().items():
                if v.dtype.is_floating_point:
                    v.copy_(v * d + (1.0 - d) * msd[k].detach())


def seed_all(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def get_device() -> torch.device:
    if torch.cuda.is_available():
        return torch.device("cuda")
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def run_validation(model, loader, criterion, dev, collect_metrics=True):
    model.eval()
    loss_sum = box_sum = cls_sum = 0.0
    all_preds, all_targets = [], []
    batches = 0

    with torch.no_grad():
        for images, targets, _paths in tqdm(loader, desc="VAL", leave=False):
            images = images.to(dev)
            outputs = model(images)
            losses = criterion(outputs, targets)
            loss_sum += float(losses["loss"])
            box_sum += float(losses["box_loss"])
            cls_sum += float(losses["cls_loss"])
            if collect_metrics:
                all_preds.extend(model.head.predict_from_outputs(outputs, conf=0.05, max_det=100))
                all_targets.extend([t.detach().cpu() for t in targets])
            batches += 1

    denom = max(batches, 1)
    result = {"loss": loss_sum / denom, "box_loss": box_sum / denom, "cls_loss": cls_sum / denom}
    if collect_metrics and all_preds:
        result.update(evaluate_predictions(all_preds, all_targets, criterion.nc))
    return result


def train_one_epoch(model, loader, criterion, optimizer, dev, epoch, ema=None):
    model.train()
    loss_sum = box_sum = cls_sum = pos_total = 0.0
    batches = 0
    t0 = time.perf_counter()

    bar = tqdm(loader, desc=f"TRAIN {epoch}", leave=True)
    for batch_idx, (images, targets, _) in enumerate(bar, 1):
        images = images.to(dev)
        optimizer.zero_grad(set_to_none=True)

        outputs = model(images)
        losses = criterion(outputs, targets)
        loss = losses["loss"]

        if not torch.isfinite(loss):
            print(f"[!] Non-finite loss at batch {batch_idx}, skipping")
            continue

        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=10.0)
        optimizer.step()

        if ema is not None:
            ema.update(model)

        loss_sum += float(loss)
        box_sum += float(losses["box_loss"])
        cls_sum += float(losses["cls_loss"])
        pos_total += losses["positive_assignments"]
        batches += 1

        if batch_idx == 1 or batch_idx % 25 == 0:
            bar.set_postfix(
                loss=f"{float(loss):.4f}",
                pos=pos_total,
                t=f"{time.perf_counter() - t0:.0f}s",
            )

    denom = max(batches, 1)
    return {
        "loss": loss_sum / denom,
        "box_loss": box_sum / denom,
        "cls_loss": cls_sum / denom,
        "positive_assignments": pos_total,
        "seconds": time.perf_counter() - t0,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--image-size", type=int, default=192)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--eval-every", type=int, default=5)
    args = parser.parse_args()

    seed_all(args.seed)
    dev = get_device()

    train_manifest = PROJECT_ROOT / "pest_ml/manifests/pest24_train.txt"
    val_manifest = PROJECT_ROOT / "pest_ml/manifests/pest24_val.txt"
    ckpt_dir = PROJECT_ROOT / "pest_ml/checkpoints"
    results_dir = PROJECT_ROOT / "pest_ml/results"
    ckpt_dir.mkdir(parents=True, exist_ok=True)
    results_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("DHURANDHAR — DIRECT STUDENT TRAINING")
    print("=" * 80)
    print(f"Device     : {dev}")
    print(f"Input      : {args.image_size}x{args.image_size}")
    print(f"Batch      : {args.batch_size}")
    print(f"Epochs     : {args.epochs}")
    print("=" * 80)

    nw = 0 if dev.type == "mps" else 4
    train_ds = Pest24Dataset(train_manifest, args.image_size, True)
    val_ds = Pest24Dataset(val_manifest, args.image_size, False)
    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True,
                              num_workers=nw, pin_memory=(dev.type == "cuda"), collate_fn=pest24_collate)
    val_loader = DataLoader(val_ds, batch_size=args.batch_size, shuffle=False,
                            num_workers=nw, pin_memory=(dev.type == "cuda"), collate_fn=pest24_collate)

    model = StudentPestDetector(24).to(dev)
    ema = ModelEMA(model)
    print(f"Parameters : {sum(p.numel() for p in model.parameters()):,}")

    # Use strides (8, 16, 32) and relu decoding for the Student
    criterion = M3Loss(
        num_classes=24,
        image_size=args.image_size,
        strides=(8, 16, 32),
        decode_mode="relu"
    )

    optimizer = AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
    scheduler = CosineAnnealingLR(optimizer, T_max=args.epochs, eta_min=1e-6)

    best_map = -float("inf")
    best_path = ckpt_dir / "student_direct_best.pt"
    last_path = ckpt_dir / "student_direct_last.pt"
    history = []

    for epoch in range(1, args.epochs + 1):
        print(f"\nEpoch {epoch}/{args.epochs}")
        train_m = train_one_epoch(model, train_loader, criterion, optimizer, dev, epoch, ema)
        scheduler.step()

        do_metrics = (epoch % args.eval_every == 0) or (epoch == args.epochs)
        val_m = run_validation(ema.ema, val_loader, criterion, dev, collect_metrics=do_metrics)

        row = {"epoch": epoch, "lr": optimizer.param_groups[0]["lr"], "train": train_m, "val": val_m}
        history.append(row)
        
        print(f"TRAIN: loss={train_m['loss']:.4f} pos={train_m['positive_assignments']}")
        print(f"VAL  : loss={val_m['loss']:.4f}")
        if do_metrics:
            print(f"       mAP50={val_m.get('mAP50', 0):.4f} mAP50-95={val_m.get('mAP50_95', 0):.4f} AP_s={val_m.get('AP_small', 0):.4f}")

        ckpt_data = {
            "model_state_dict": model.state_dict(),
            "ema_state_dict": ema.ema.state_dict(),
            "epoch": epoch,
            "image_size": args.image_size,
        }
        torch.save(ckpt_data, last_path)

        score = val_m.get("mAP50_95", -1)
        if score > best_map:
            best_map = score
            torch.save(ckpt_data, best_path)
            if do_metrics:
                print(f"  >> New best mAP50-95: {best_map:.4f}")

        with (results_dir / "direct_training_history.json").open("w") as f:
            json.dump(history, f, indent=2)

    print("\n" + "=" * 80)
    print(f"TRAINING COMPLETE - Best mAP50-95: {best_map:.4f}")
    print("=" * 80)


if __name__ == "__main__":
    main()
