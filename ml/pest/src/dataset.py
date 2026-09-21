from __future__ import annotations

from pathlib import Path

import numpy as np
import torch
from PIL import Image, ImageEnhance
from torch.utils.data import Dataset


IMAGENET_MEAN = torch.tensor([0.485, 0.456, 0.406], dtype=torch.float32).view(3, 1, 1)
IMAGENET_STD = torch.tensor([0.229, 0.224, 0.225], dtype=torch.float32).view(3, 1, 1)


class Pest24Dataset(Dataset):
    """Pest24 YOLO dataset with deterministic letterbox and safe augmentation."""

    def __init__(self, manifest: str | Path, image_size: int = 640, train: bool = False) -> None:
        self.manifest = Path(manifest)
        self.image_size = image_size
        self.train = train
        self.images = [Path(line.strip()) for line in self.manifest.read_text().splitlines() if line.strip()]
        if not self.images:
            raise RuntimeError(f"No images found in {self.manifest}")

    def __len__(self) -> int:
        return len(self.images)

    @staticmethod
    def _label_path(image_path: Path) -> Path:
        return Path(str(image_path).replace("/images/", "/labels/")).with_suffix(".txt")

    def _read_labels(self, image_path: Path, width: int, height: int) -> torch.Tensor:
        label_path = self._label_path(image_path)
        if not label_path.exists():
            raise FileNotFoundError(f"Missing label: {label_path}")
        rows = []
        seen = set()
        for line in label_path.read_text(errors="ignore").splitlines():
            parts = line.split()
            if len(parts) != 5:
                continue
            cls, xc, yc, w, h = map(float, parts)
            cls = int(cls)
            key = (cls, xc, yc, w, h)
            if key in seen:
                continue
            seen.add(key)
            if not (0 <= cls < 24 and 0 <= w <= 1 and 0 <= h <= 1):
                raise ValueError(f"Invalid Pest24 label in {label_path}: {line}")
            x1 = (xc - w / 2) * width
            y1 = (yc - h / 2) * height
            x2 = (xc + w / 2) * width
            y2 = (yc + h / 2) * height
            rows.append([cls, x1, y1, x2, y2])
        if not rows:
            return torch.zeros((0, 5), dtype=torch.float32)
        return torch.tensor(rows, dtype=torch.float32)

    def _letterbox(self, image: Image.Image, targets: torch.Tensor):
        size = self.image_size
        width, height = image.size
        scale = min(size / width, size / height)
        new_w = max(1, int(round(width * scale)))
        new_h = max(1, int(round(height * scale)))
        image = image.resize((new_w, new_h), Image.Resampling.BILINEAR)
        canvas = Image.new("RGB", (size, size), (114, 114, 114))
        pad_x = (size - new_w) // 2
        pad_y = (size - new_h) // 2
        canvas.paste(image, (pad_x, pad_y))
        if targets.numel():
            targets = targets.clone()
            targets[:, 1::2] = targets[:, 1::2] * scale
            targets[:, 2::2] = targets[:, 2::2] * scale
            # The alternating slice above does not include the desired layout;
            # apply explicit coordinates for clarity and correctness.
            targets[:, 1] = targets[:, 1] + pad_x
            targets[:, 3] = targets[:, 3] + pad_x
            targets[:, 2] = targets[:, 2] + pad_y
            targets[:, 4] = targets[:, 4] + pad_y
        return canvas, targets

    def __getitem__(self, index: int):
        image_path = self.images[index]
        image = Image.open(image_path).convert("RGB")
        width, height = image.size
        targets = self._read_labels(image_path, width, height)
        image, targets = self._letterbox(image, targets)

        if self.train and np.random.random() < 0.5:
            image = image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            if targets.numel():
                old_x1 = targets[:, 1].clone()
                old_x2 = targets[:, 3].clone()
                targets[:, 1] = self.image_size - old_x2
                targets[:, 3] = self.image_size - old_x1

        if self.train and np.random.random() < 0.25:
            image = ImageEnhance.Brightness(image).enhance(float(np.random.uniform(0.85, 1.15)))
            image = ImageEnhance.Contrast(image).enhance(float(np.random.uniform(0.85, 1.15)))

        arr = np.asarray(image, dtype=np.float32) / 255.0
        tensor = torch.from_numpy(arr).permute(2, 0, 1).contiguous()
        tensor = (tensor - IMAGENET_MEAN) / IMAGENET_STD

        if targets.numel():
            targets[:, 1:].clamp_(0, self.image_size)
            keep = (targets[:, 3] > targets[:, 1]) & (targets[:, 4] > targets[:, 2])
            targets = targets[keep]
        return tensor, targets, str(image_path)


def pest24_collate(batch):
    images = torch.stack([item[0] for item in batch], 0)
    targets = [item[1] for item in batch]
    paths = [item[2] for item in batch]
    return images, targets, paths
