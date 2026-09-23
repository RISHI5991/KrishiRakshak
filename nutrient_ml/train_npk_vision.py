import os
import random
import hashlib
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from PIL import Image
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
    f1_score,
)

from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
import timm


# ============================================================
# CONFIGURATION
# ============================================================

DATA_DIR = Path(r"D:\Dhurandhar\nutrient_ml\data\HARN_Rice")
MODEL_DIR = Path(r"D:\Dhurandhar\nutrient_ml\models")
REPORT_DIR = Path(r"D:\Dhurandhar\nutrient_ml\reports")

IMG_SIZE = 224
BATCH_SIZE = 32
EPOCHS = 20

LEARNING_RATE = 1e-4
WEIGHT_DECAY = 1e-4

SEED = 42

MODEL_NAME = "mobilenetv4_conv_small.e2400_r224_in1k"

CLASS_NAMES = [
    "Healthy",
    "K_Deficiency",
    "N_Deficiency",
    "P_Deficiency",
]

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp",
}


# ============================================================
# REPRODUCIBILITY
# ============================================================

random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)

if torch.cuda.is_available():
    torch.cuda.manual_seed_all(SEED)


# ============================================================
# DEVICE
# ============================================================

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

print("=" * 60)
print("DEVICE:", DEVICE)
print("=" * 60)


# ============================================================
# DIRECTORIES
# ============================================================

MODEL_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# COLLECT IMAGES
# ============================================================

def collect_images():

    samples = []

    for class_name in CLASS_NAMES:

        class_dir = DATA_DIR / class_name

        if not class_dir.exists():
            raise FileNotFoundError(
                f"Missing class folder: {class_dir}"
            )

        for path in class_dir.rglob("*"):

            if (
                path.is_file()
                and path.suffix.lower() in IMAGE_EXTENSIONS
            ):
                samples.append(
                    (str(path), class_name)
                )

    return samples


samples = collect_images()

print("\nTotal images:", len(samples))


# ============================================================
# CLASS DISTRIBUTION
# ============================================================

print("\nClass distribution:")

for class_name in CLASS_NAMES:

    count = sum(
        label == class_name
        for _, label in samples
    )

    print(
        f"{class_name:15s}: {count}"
    )


# ============================================================
# EXACT DUPLICATE CHECK
# ============================================================

print("\nChecking exact duplicate images...")

hash_to_paths = {}

for path, _ in samples:

    try:
        with open(path, "rb") as f:
            file_hash = hashlib.sha256(
                f.read()
            ).hexdigest()

        hash_to_paths.setdefault(
            file_hash, []
        ).append(path)

    except Exception as e:

        print(
            "Could not hash:",
            path,
            e
        )


duplicate_groups = [
    paths
    for paths in hash_to_paths.values()
    if len(paths) > 1
]

duplicate_files = sum(
    len(group)
    for group in duplicate_groups
)

print(
    "Duplicate groups:",
    len(duplicate_groups)
)

print(
    "Files involved in duplicates:",
    duplicate_files
)


# ============================================================
# LABEL ENCODING
# ============================================================

class_to_idx = {
    name: idx
    for idx, name in enumerate(CLASS_NAMES)
}

paths = np.array(
    [x[0] for x in samples]
)

labels = np.array(
    [
        class_to_idx[x[1]]
        for x in samples
    ]
)


# ============================================================
# STRATIFIED SPLIT
# ============================================================

train_paths, temp_paths, train_labels, temp_labels = (
    train_test_split(
        paths,
        labels,
        test_size=0.30,
        random_state=SEED,
        stratify=labels,
    )
)

val_paths, test_paths, val_labels, test_labels = (
    train_test_split(
        temp_paths,
        temp_labels,
        test_size=0.50,
        random_state=SEED,
        stratify=temp_labels,
    )
)


print("\nDataset split:")

print(
    "Train:",
    len(train_paths)
)

print(
    "Validation:",
    len(val_paths)
)

print(
    "Test:",
    len(test_paths)
)


# ============================================================
# TRANSFORMS
# ============================================================

train_transform = transforms.Compose([

    transforms.Resize(
        (IMG_SIZE, IMG_SIZE)
    ),

    transforms.RandomHorizontalFlip(
        p=0.5
    ),

    transforms.RandomRotation(
        12
    ),

    transforms.ColorJitter(
        brightness=0.10,
        contrast=0.10,
        saturation=0.08,
        hue=0.02,
    ),

    transforms.ToTensor(),

    transforms.Normalize(
        mean=[
            0.485,
            0.456,
            0.406,
        ],
        std=[
            0.229,
            0.224,
            0.225,
        ],
    ),
])


eval_transform = transforms.Compose([

    transforms.Resize(
        (IMG_SIZE, IMG_SIZE)
    ),

    transforms.ToTensor(),

    transforms.Normalize(
        mean=[
            0.485,
            0.456,
            0.406,
        ],
        std=[
            0.229,
            0.224,
            0.225,
        ],
    ),
])


# ============================================================
# DATASET
# ============================================================

class LeafDataset(Dataset):

    def __init__(
        self,
        paths,
        labels,
        transform=None,
    ):

        self.paths = list(paths)
        self.labels = list(labels)
        self.transform = transform

    def __len__(self):

        return len(self.paths)

    def __getitem__(self, index):

        image_path = self.paths[index]

        label = self.labels[index]

        image = Image.open(
            image_path
        ).convert("RGB")

        if self.transform:

            image = self.transform(
                image
            )

        return image, label


train_dataset = LeafDataset(
    train_paths,
    train_labels,
    train_transform,
)

val_dataset = LeafDataset(
    val_paths,
    val_labels,
    eval_transform,
)

test_dataset = LeafDataset(
    test_paths,
    test_labels,
    eval_transform,
)


# ============================================================
# DATALOADERS
# ============================================================

train_loader = DataLoader(
    train_dataset,
    batch_size=BATCH_SIZE,
    shuffle=True,
    num_workers=0,
)

val_loader = DataLoader(
    val_dataset,
    batch_size=BATCH_SIZE,
    shuffle=False,
    num_workers=0,
)

test_loader = DataLoader(
    test_dataset,
    batch_size=BATCH_SIZE,
    shuffle=False,
    num_workers=0,
)


# ============================================================
# MODEL
# ============================================================

print("\nLoading:")
print(MODEL_NAME)

model = timm.create_model(
    MODEL_NAME,
    pretrained=True,
    num_classes=len(CLASS_NAMES),
)

model = model.to(DEVICE)

print(
    "Trainable parameters:",
    sum(
        p.numel()
        for p in model.parameters()
        if p.requires_grad
    ),
)


# ============================================================
# CLASS WEIGHTS
# ============================================================

class_counts = np.bincount(
    train_labels,
    minlength=len(CLASS_NAMES),
)

class_weights = (
    len(train_labels)
    /
    (
        len(CLASS_NAMES)
        * class_counts
    )
)

class_weights = torch.tensor(
    class_weights,
    dtype=torch.float32,
).to(DEVICE)


criterion = nn.CrossEntropyLoss(
    weight=class_weights
)


# ============================================================
# OPTIMIZER
# ============================================================

optimizer = torch.optim.AdamW(
    model.parameters(),
    lr=LEARNING_RATE,
    weight_decay=WEIGHT_DECAY,
)


scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
    optimizer,
    mode="max",
    factor=0.5,
    patience=2,
)


# ============================================================
# EVALUATION FUNCTION
# ============================================================

def evaluate(model, loader):

    model.eval()

    all_predictions = []
    all_labels = []

    total_loss = 0.0
    total_items = 0

    with torch.no_grad():

        for images, labels_batch in loader:

            images = images.to(DEVICE)
            labels_batch = labels_batch.to(DEVICE)

            outputs = model(images)

            loss = criterion(
                outputs,
                labels_batch,
            )

            total_loss += (
                loss.item()
                * images.size(0)
            )

            total_items += images.size(0)

            predictions = (
                outputs.argmax(dim=1)
            )

            all_predictions.extend(
                predictions.cpu().numpy()
            )

            all_labels.extend(
                labels_batch.cpu().numpy()
            )

    avg_loss = (
        total_loss / total_items
    )

    accuracy = accuracy_score(
        all_labels,
        all_predictions,
    )

    macro_f1 = f1_score(
        all_labels,
        all_predictions,
        average="macro",
    )

    return (
        avg_loss,
        accuracy,
        macro_f1,
        all_labels,
        all_predictions,
    )


# ============================================================
# TRAINING
# ============================================================

best_val_f1 = -1.0

best_model_path = (
    MODEL_DIR
    / "npk_vision_mobilenetv4_best.pt"
)


for epoch in range(EPOCHS):

    model.train()

    running_loss = 0.0
    correct = 0
    total = 0

    for images, labels_batch in train_loader:

        images = images.to(DEVICE)
        labels_batch = labels_batch.to(DEVICE)

        optimizer.zero_grad()

        outputs = model(images)

        loss = criterion(
            outputs,
            labels_batch,
        )

        loss.backward()

        optimizer.step()

        running_loss += (
            loss.item()
            * images.size(0)
        )

        predictions = (
            outputs.argmax(dim=1)
        )

        correct += (
            predictions
            == labels_batch
        ).sum().item()

        total += labels_batch.size(0)

    train_loss = (
        running_loss / total
    )

    train_accuracy = (
        correct / total
    )


    (
        val_loss,
        val_accuracy,
        val_f1,
        _,
        _,
    ) = evaluate(
        model,
        val_loader,
    )


    scheduler.step(
        val_f1
    )


    print(
        f"\nEpoch "
        f"{epoch + 1:02d}/{EPOCHS}"
    )

    print(
        f"Train Loss: {train_loss:.4f}"
    )

    print(
        f"Train Accuracy: "
        f"{train_accuracy:.4f}"
    )

    print(
        f"Val Loss: {val_loss:.4f}"
    )

    print(
        f"Val Accuracy: "
        f"{val_accuracy:.4f}"
    )

    print(
        f"Val Macro-F1: "
        f"{val_f1:.4f}"
    )


    if val_f1 > best_val_f1:

        best_val_f1 = val_f1

        torch.save(
            {
                "model_state_dict":
                    model.state_dict(),

                "class_to_idx":
                    class_to_idx,

                "img_size":
                    IMG_SIZE,

                "model_name":
                    MODEL_NAME,

                "best_val_f1":
                    best_val_f1,
            },
            best_model_path,
        )

        print(
            ">>> BEST MODEL SAVED"
        )


# ============================================================
# FINAL TEST
# ============================================================

print("\n")
print("=" * 60)
print("FINAL TEST")
print("=" * 60)


checkpoint = torch.load(
    best_model_path,
    map_location=DEVICE,
)

model.load_state_dict(
    checkpoint["model_state_dict"]
)


(
    test_loss,
    test_accuracy,
    test_f1,
    true_labels,
    predictions,
) = evaluate(
    model,
    test_loader,
)


print(
    f"\nTest Loss: "
    f"{test_loss:.4f}"
)

print(
    f"Test Accuracy: "
    f"{test_accuracy:.4f}"
)

print(
    f"Test Macro-F1: "
    f"{test_f1:.4f}"
)


print("\nClassification Report:\n")

print(
    classification_report(
        true_labels,
        predictions,
        target_names=CLASS_NAMES,
        digits=4,
    )
)


print("\nConfusion Matrix:\n")

print(
    confusion_matrix(
        true_labels,
        predictions,
    )
)


print("\nBest model:")

print(best_model_path)