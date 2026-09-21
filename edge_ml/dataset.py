from __future__ import annotations

import random
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from PIL import Image, ImageEnhance, ImageOps
from torch.utils.data import Dataset

MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)


def _random_zoom(img: Image.Image, low=0.80, high=1.20) -> Image.Image:
    w, h = img.size
    scale = random.uniform(low, high)
    if scale >= 1.0:
        nw, nh = int(w / scale), int(h / scale)
        left = random.randint(0, max(0, w - nw))
        top = random.randint(0, max(0, h - nh))
        img = img.crop((left, top, left + nw, top + nh))
        return img.resize((w, h), Image.Resampling.BILINEAR)
    nw, nh = int(w * scale), int(h * scale)
    resized = img.resize((nw, nh), Image.Resampling.BILINEAR)
    canvas = Image.new('RGB', (w, h), (0, 0, 0))
    left = (w - nw) // 2
    top = (h - nh) // 2
    canvas.paste(resized, (left, top))
    return canvas


def _random_translate(img: Image.Image, frac=0.20) -> Image.Image:
    w, h = img.size
    tx = int(random.uniform(-frac, frac) * w)
    ty = int(random.uniform(-frac, frac) * h)
    canvas = Image.new('RGB', (w, h), (0, 0, 0))
    src_left = max(0, -tx)
    src_top = max(0, -ty)
    src_right = min(w, w - tx) if tx >= 0 else w
    src_bottom = min(h, h - ty) if ty >= 0 else h
    crop = img.crop((src_left, src_top, src_right, src_bottom))
    dst_x = max(0, tx)
    dst_y = max(0, ty)
    canvas.paste(crop, (dst_x, dst_y))
    return canvas


def augment(img: Image.Image) -> Image.Image:
    if random.random() < 0.85:
        angle = random.uniform(-40, 40)
        img = img.rotate(angle, resample=Image.Resampling.BILINEAR, expand=False, fillcolor=(0, 0, 0))
    if random.random() < 0.85:
        img = _random_translate(img, 0.20)
    if random.random() < 0.80:
        img = _random_zoom(img, 0.80, 1.20)
    if random.random() < 0.50:
        img = ImageOps.mirror(img)
    if random.random() < 0.50:
        img = ImageOps.flip(img)
    if random.random() < 0.80:
        img = ImageEnhance.Brightness(img).enhance(random.uniform(0.70, 1.30))
    if random.random() < 0.60:
        img = ImageEnhance.Contrast(img).enhance(random.uniform(0.80, 1.20))
    return img


def preprocess(img: Image.Image, image_size: int, train: bool) -> torch.Tensor:
    img = img.convert('RGB')
    img = img.resize((image_size, image_size), Image.Resampling.BILINEAR)
    if train:
        img = augment(img)
    arr = np.asarray(img, dtype=np.float32) / 255.0
    arr = (arr - MEAN) / STD
    arr = np.transpose(arr, (2, 0, 1)).copy()
    return torch.from_numpy(arr).float()


class DhurandharDataset(Dataset):
    def __init__(self, csv_path: str | Path, m1_labels_csv: str | Path, m2_labels_csv: str | Path, image_size: int = 256, train: bool = False):
        self.df = pd.read_csv(csv_path)
        m1_df = pd.read_csv(m1_labels_csv)
        m2_df = pd.read_csv(m2_labels_csv)
        self.m1_to_idx = dict(zip(m1_df['label'], m1_df['index']))
        self.m2_to_idx = dict(zip(m2_df['label'], m2_df['index']))
        self.image_size = image_size
        self.train = train

    def __len__(self):
        return len(self.df)

    def __getitem__(self, index: int):
        row = self.df.iloc[index]
        path = Path(row['path'])
        if not path.exists():
            raise FileNotFoundError(path)
        with Image.open(path) as img:
            x = preprocess(img, self.image_size, self.train)
        m1 = int(self.m1_to_idx[str(row['m1_label'])])
        raw_m2 = row['m2_label']
        if pd.isna(raw_m2) or str(raw_m2).strip() == '':
            m2 = -100
        else:
            m2 = int(self.m2_to_idx[str(raw_m2)])
        return x, torch.tensor(m1, dtype=torch.long), torch.tensor(m2, dtype=torch.long), str(path)
