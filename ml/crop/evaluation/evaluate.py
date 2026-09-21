from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from torch.utils.data import DataLoader

import config
from dataset import DhurandharDataset
from model import DhurandharVision


def main():
    dev = torch.device('mps') if torch.backends.mps.is_available() else torch.device('cpu')
    ckpt_path = config.CHECKPOINT_DIR / 'dhurandhar_mv4_256_best.pt'
    if not ckpt_path.exists():
        raise FileNotFoundError(ckpt_path)

    ds = DhurandharDataset(config.MANIFEST_DIR / 'test.csv', config.MANIFEST_DIR / 'm1_labels.csv', config.MANIFEST_DIR / 'm2_labels.csv', config.IMAGE_SIZE, False)
    loader = DataLoader(ds, batch_size=config.BATCH_SIZE, shuffle=False, num_workers=config.NUM_WORKERS, pin_memory=False)
    m1_df = pd.read_csv(config.MANIFEST_DIR / 'm1_labels.csv')
    m2_df = pd.read_csv(config.MANIFEST_DIR / 'm2_labels.csv')
    m1_names = m1_df.sort_values('index')['label'].tolist()
    m2_names = m2_df.sort_values('index')['label'].tolist()

    model = DhurandharVision(15, 38, config.DROPOUT, False).to(dev)
    state = torch.load(ckpt_path, map_location='cpu')
    model.load_state_dict(state['model_state_dict'])
    model.eval()

    y1_true, y1_pred, y2_true, y2_pred = [], [], [], []
    with torch.no_grad():
        for x, y1, y2, _ in loader:
            a, b = model(x.to(dev))
            y1_true.extend(y1.numpy())
            y1_pred.extend(a.argmax(1).cpu().numpy())
            mask = y2.numpy() != -100
            if mask.any():
                y2_true.extend(y2.numpy()[mask])
                y2_pred.extend(b.argmax(1).cpu().numpy()[mask])

    m1_acc = accuracy_score(y1_true, y1_pred)
    m2_acc = accuracy_score(y2_true, y2_pred)
    print('=' * 80)
    print('DHURANDHAR TEST RESULTS')
    print('=' * 80)
    print(f'M1 accuracy : {m1_acc * 100:.4f}%')
    print(f'M1 macro-F1 : {f1_score(y1_true, y1_pred, average="macro", zero_division=0):.4f}')
    print(f'M2 accuracy : {m2_acc * 100:.4f}%')
    print(f'M2 macro-F1 : {f1_score(y2_true, y2_pred, average="macro", zero_division=0):.4f}')
    print('\nM1 report:')
    print(classification_report(y1_true, y1_pred, labels=list(range(15)), target_names=m1_names, digits=4, zero_division=0))
    print('\nM2 report:')
    print(classification_report(y2_true, y2_pred, labels=list(range(38)), target_names=m2_names, digits=4, zero_division=0))

    out = config.RESULT_DIR / 'test_evaluation'
    out.mkdir(parents=True, exist_ok=True)
    np.save(out / 'm1_confusion_matrix.npy', confusion_matrix(y1_true, y1_pred, labels=list(range(15))))
    np.save(out / 'm2_confusion_matrix.npy', confusion_matrix(y2_true, y2_pred, labels=list(range(38))))
    with (out / 'metrics.json').open('w') as f:
        json.dump({'m1_accuracy': m1_acc, 'm1_macro_f1': f1_score(y1_true, y1_pred, average='macro', zero_division=0), 'm2_accuracy': m2_acc, 'm2_macro_f1': f1_score(y2_true, y2_pred, average='macro', zero_division=0), 'checkpoint_epoch': int(state['epoch'])}, f, indent=2)


if __name__ == '__main__':
    main()
