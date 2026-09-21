from __future__ import annotations

import argparse
import json
import random

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.metrics import accuracy_score, f1_score
from torch.optim import AdamW
from torch.optim.lr_scheduler import ReduceLROnPlateau
from torch.utils.data import DataLoader
from tqdm import tqdm

import config
from dataset import DhurandharDataset
from model import DhurandharVision


def seed_all(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def device():
    return torch.device('mps') if torch.backends.mps.is_available() else torch.device('cpu')


def balanced_weights(csv_path, label_csv, column):
    df = pd.read_csv(csv_path)
    labels = pd.read_csv(label_csv)
    mapping = dict(zip(labels['label'], labels['index']))
    counts = np.zeros(len(labels), dtype=np.float64)
    for v in df[column]:
        if pd.isna(v) or str(v).strip() == '':
            continue
        counts[int(mapping[str(v)])] += 1
    total = counts.sum()
    weights = np.ones_like(counts)
    for i, c in enumerate(counts):
        if c > 0:
            weights[i] = total / (len(counts) * c)
    return torch.tensor(weights, dtype=torch.float32)


def run_epoch(
    model,
    loader,
    criterion_m1,
    criterion_m2,
    optimizer,
    device,
    train: bool,
):
    model.train(train)

    total_loss_sum = 0.0

    m1_loss_sum = 0.0
    m2_loss_sum = 0.0

    m1_count = 0
    m2_count = 0

    m1_true = []
    m1_pred = []

    m2_true = []
    m2_pred = []

    iterator = tqdm(
        loader,
        desc="TRAIN" if train else "VAL",
        leave=False,
    )

    for images, y1, y2, _paths in iterator:

        images = images.to(device)
        y1 = y1.to(device)
        y2 = y2.to(device)

        if train:
            optimizer.zero_grad(
                set_to_none=True
            )

        m1_logits, m2_logits = model(images)

        # M1 LOSS

        loss_m1 = criterion_m1(
            m1_logits,
            y1,
        )

        # M2 LOSS
        # Only valid M2 targets participate.
        # Background samples use -100.

        valid_m2 = y2 != -100

        if valid_m2.any():

            loss_m2 = criterion_m2(
                m2_logits[valid_m2],
                y2[valid_m2],
            )

            valid_m2_count = int(
                valid_m2.sum().item()
            )

        else:

            # IMPORTANT:
            # No valid M2 examples in this batch.
            # Don't calculate CrossEntropyLoss here,
            # because mean over zero valid samples = NaN.
            loss_m2 = torch.zeros(
                (),
                device=device,
                dtype=loss_m1.dtype,
            )

            valid_m2_count = 0

        # JOINT LOSS

        loss = (
            0.5 * loss_m1
            + 0.5 * loss_m2
        )

        if train:
            loss.backward()
            optimizer.step()

        # ACCUMULATE LOSS BY VALID SAMPLE COUNTS

        batch_size = images.size(0)

        total_loss_sum += (
            loss.item() * batch_size
        )

        m1_loss_sum += (
            loss_m1.item() * batch_size
        )

        m1_count += batch_size

        if valid_m2_count > 0:

            m2_loss_sum += (
                loss_m2.item()
                * valid_m2_count
            )

            m2_count += valid_m2_count

        # M1 METRICS

        m1_predictions = (
            m1_logits
            .argmax(dim=1)
            .detach()
            .cpu()
            .numpy()
        )

        m1_true.extend(
            y1.detach()
            .cpu()
            .numpy()
        )

        m1_pred.extend(
            m1_predictions
        )

        # M2 METRICS

        if valid_m2_count > 0:

            m2_predictions = (
                m2_logits[valid_m2]
                .argmax(dim=1)
                .detach()
                .cpu()
                .numpy()
            )

            m2_targets = (
                y2[valid_m2]
                .detach()
                .cpu()
                .numpy()
            )

            m2_true.extend(
                m2_targets
            )

            m2_pred.extend(
                m2_predictions
            )

    # FINAL LOSS VALUES

    total_items = max(
        m1_count,
        1,
    )

    epoch_loss = (
        total_loss_sum
        / total_items
    )

    epoch_m1_loss = (
        m1_loss_sum
        / max(m1_count, 1)
    )

    epoch_m2_loss = (
        m2_loss_sum
        / max(m2_count, 1)
    )

    # ACCURACY / F1

    m1_accuracy = accuracy_score(
        m1_true,
        m1_pred,
    )

    m1_macro_f1 = f1_score(
        m1_true,
        m1_pred,
        average="macro",
        zero_division=0,
    )

    if m2_count > 0:

        m2_accuracy = accuracy_score(
            m2_true,
            m2_pred,
        )

        m2_macro_f1 = f1_score(
            m2_true,
            m2_pred,
            average="macro",
            zero_division=0,
        )

    else:

        m2_accuracy = 0.0
        m2_macro_f1 = 0.0

    return {
        "loss": epoch_loss,
        "m1_loss": epoch_m1_loss,
        "m2_loss": epoch_m2_loss,
        "m1_accuracy": m1_accuracy,
        "m2_accuracy": m2_accuracy,
        "m1_macro_f1": m1_macro_f1,
        "m2_macro_f1": m2_macro_f1,
        "m2_valid_samples": m2_count,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--epochs', type=int, default=config.EPOCHS)
    ap.add_argument('--batch-size', type=int, default=config.BATCH_SIZE)
    ap.add_argument('--lr', type=float, default=config.LEARNING_RATE)
    args = ap.parse_args()

    seed_all(config.SEED)
    dev = device()

    print('=' * 80)
    print('DHURANDHAR M1 + M2 — MOBILENETV4-CONVSMALL')
    print('=' * 80)
    print('Device:', dev)
    print('Input:', f'{config.IMAGE_SIZE}x{config.IMAGE_SIZE}')
    print('Batch:', args.batch_size)
    print('Epochs:', args.epochs)
    print('Learning rate:', args.lr)
    print('=' * 80)

    train_ds = DhurandharDataset(config.MANIFEST_DIR / 'train.csv', config.MANIFEST_DIR / 'm1_labels.csv', config.MANIFEST_DIR / 'm2_labels.csv', config.IMAGE_SIZE, True)
    val_ds = DhurandharDataset(config.MANIFEST_DIR / 'val.csv', config.MANIFEST_DIR / 'm1_labels.csv', config.MANIFEST_DIR / 'm2_labels.csv', config.IMAGE_SIZE, False)

    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True, num_workers=config.NUM_WORKERS, pin_memory=False)
    val_loader = DataLoader(val_ds, batch_size=args.batch_size, shuffle=False, num_workers=config.NUM_WORKERS, pin_memory=False)

    m1w = balanced_weights(config.MANIFEST_DIR / 'train.csv', config.MANIFEST_DIR / 'm1_labels.csv', 'm1_label').to(dev)
    m2w = balanced_weights(config.MANIFEST_DIR / 'train.csv', config.MANIFEST_DIR / 'm2_labels.csv', 'm2_label').to(dev)

    model = DhurandharVision(15, 38, config.DROPOUT, True).to(dev)
    params = sum(p.numel() for p in model.parameters())
    print('Parameters:', f'{params:,}')
    print('Feature dim:', model.feature_dim)

    criterion1 = nn.CrossEntropyLoss(weight=m1w)
    criterion2 = nn.CrossEntropyLoss(weight=m2w, ignore_index=-100)

    optimizer = AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)
    scheduler = ReduceLROnPlateau(optimizer, mode='min', factor=config.LR_FACTOR, patience=config.LR_PATIENCE, min_lr=config.MIN_LR)

    best = float('inf')
    stale = 0
    history = []
    ckpt = config.CHECKPOINT_DIR / 'dhurandhar_mv4_256_best.pt'

    for epoch in range(1, args.epochs + 1):
        print(f'\nEpoch {epoch}/{args.epochs}')
        train_m = run_epoch(model, train_loader, criterion1, criterion2, optimizer, dev, True)
        val_m = run_epoch(model, val_loader, criterion1, criterion2, optimizer, dev, False)
        lr = optimizer.param_groups[0]['lr']
        print('TRAIN:', train_m, 'LR=', lr)
        print('VAL  :', val_m)
        row = {'epoch': epoch, 'lr': lr}
        row.update({f'train_{k}': v for k, v in train_m.items()})
        row.update({f'val_{k}': v for k, v in val_m.items()})
        history.append(row)
        scheduler.step(val_m['loss'])
        if val_m['loss'] < best:
            best = val_m['loss']
            stale = 0
            torch.save({'model_state_dict': model.state_dict(), 'epoch': epoch, 'best_val_loss': best, 'model_name': config.MODEL_NAME, 'image_size': config.IMAGE_SIZE}, ckpt)
            print('✓ Saved best checkpoint:', ckpt)
        else:
            stale += 1
            if stale >= config.EARLY_STOPPING_PATIENCE:
                print('Early stopping.')
                break

    pd.DataFrame(history).to_csv(config.RESULT_DIR / 'training_history.csv', index=False)
    with (config.RESULT_DIR / 'training_metadata.json').open('w') as f:
        json.dump({'best_val_loss': best, 'epochs_completed': len(history), 'model': config.MODEL_NAME, 'input_size': config.IMAGE_SIZE, 'm1_classes': 15, 'm2_classes': 38}, f, indent=2)

    print('\nTraining finished.')
    print('Best checkpoint:', ckpt)

if __name__ == '__main__':
    main()
