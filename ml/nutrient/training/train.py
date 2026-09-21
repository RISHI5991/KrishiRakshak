import random
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from PIL import Image

import timm

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    classification_report,
    confusion_matrix,
)


# ============================================================
# CONFIG
# ============================================================

DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent / 'nutrient_ml' / 'data' / 'HARN_Rice'

MODEL_DIR = Path(__file__).resolve().parent.parent / 'models'

RESULT_DIR = Path(__file__).resolve().parent.parent / 'evaluation'

MODEL_DIR.mkdir(exist_ok=True)
RESULT_DIR.mkdir(exist_ok=True)

IMG_SIZE = 224
BATCH_SIZE = 32
EPOCHS = 8
LR = 1e-4

SEED = 42

CLASS_NAMES = [
    "Healthy",
    "K_Deficiency",
    "N_Deficiency",
    "P_Deficiency",
]

MODEL_NAME = (
    "mobilenetv4_conv_small.e2400_r224_in1k"
)


# ============================================================
# SEED
# ============================================================

random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)


# ============================================================
# DEVICE
# ============================================================

DEVICE = torch.device(
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)

print("=" * 60)
print("NPK VISION MODEL - BASELINE V1")
print("=" * 60)

print("Device:", DEVICE)
print("Model:", MODEL_NAME)


# ============================================================
# COLLECT IMAGES
# ============================================================

extensions = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp",
}


samples = []

for class_name in CLASS_NAMES:

    folder = DATA_DIR / class_name

    if not folder.exists():
        raise FileNotFoundError(
            f"Missing folder: {folder}"
        )

    for file in folder.rglob("*"):

        if (
            file.is_file()
            and file.suffix.lower()
            in extensions
        ):
            samples.append(
                (
                    str(file),
                    class_name,
                )
            )


print("\nTotal images:", len(samples))


# ============================================================
# CLASS COUNTS
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
# LABEL ENCODING
# ============================================================

class_to_idx = {
    name: i
    for i, name in enumerate(CLASS_NAMES)
}


paths = np.array([
    x[0] for x in samples
])

labels = np.array([
    class_to_idx[x[1]]
    for x in samples
])


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

print("Train:", len(train_paths))
print("Validation:", len(val_paths))
print("Test:", len(test_paths))


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
        10
    ),

    transforms.ToTensor(),

    transforms.Normalize(
        [0.485, 0.456, 0.406],
        [0.229, 0.224, 0.225],
    ),
])


eval_transform = transforms.Compose([

    transforms.Resize(
        (IMG_SIZE, IMG_SIZE)
    ),

    transforms.ToTensor(),

    transforms.Normalize(
        [0.485, 0.456, 0.406],
        [0.229, 0.224, 0.225],
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
        transform,
    ):

        self.paths = list(paths)
        self.labels = list(labels)
        self.transform = transform

    def __len__(self):

        return len(self.paths)

    def __getitem__(self, index):

        image = Image.open(
            self.paths[index]
        ).convert("RGB")

        image = self.transform(
            image
        )

        label = self.labels[index]

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
# LOADERS
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

print("\nLoading pretrained MobileNetV4...")

model = timm.create_model(
    MODEL_NAME,
    pretrained=True,
    num_classes=4,
)

model = model.to(DEVICE)


print(
    "Parameters:",
    sum(
        p.numel()
        for p in model.parameters()
    ),
)


# ============================================================
# LOSS + OPTIMIZER
# ============================================================

criterion = nn.CrossEntropyLoss()

optimizer = torch.optim.AdamW(
    model.parameters(),
    lr=LR,
    weight_decay=1e-4,
)


# ============================================================
# EVALUATION
# ============================================================

def evaluate(loader):

    model.eval()

    all_labels = []
    all_predictions = []

    total_loss = 0
    total_samples = 0

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

            total_samples += images.size(0)

            predictions = outputs.argmax(
                dim=1
            )

            all_labels.extend(
                labels_batch.cpu().numpy()
            )

            all_predictions.extend(
                predictions.cpu().numpy()
            )

    loss = total_loss / total_samples

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
        loss,
        accuracy,
        macro_f1,
        all_labels,
        all_predictions,
    )


# ============================================================
# TRAIN
# ============================================================

best_f1 = -1

best_model_path = (
    MODEL_DIR
    / "npk_vision_baseline_v1.pt"
)


for epoch in range(EPOCHS):

    model.train()

    running_loss = 0
    correct = 0
    total = 0

    for batch_idx, (images, labels_batch) in enumerate(train_loader, start=1):
        if batch_idx % 10 == 0 or batch_idx == len(train_loader):
            print(
            f"  Batch {batch_idx}/{len(train_loader)}",
            flush=True
            )

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

        predictions = outputs.argmax(
            dim=1
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
        val_loader
    )


    print(
        f"\nEpoch "
        f"{epoch + 1}/{EPOCHS}"
    )

    print(
        f"Train Loss: "
        f"{train_loss:.4f}"
    )

    print(
        f"Train Accuracy: "
        f"{train_accuracy:.4f}"
    )

    print(
        f"Val Loss: "
        f"{val_loss:.4f}"
    )

    print(
        f"Val Accuracy: "
        f"{val_accuracy:.4f}"
    )

    print(
        f"Val Macro-F1: "
        f"{val_f1:.4f}"
    )


    if val_f1 > best_f1:

        best_f1 = val_f1

        torch.save(
            {
                "model_state_dict":
                    model.state_dict(),

                "class_to_idx":
                    class_to_idx,

                "model_name":
                    MODEL_NAME,

                "img_size":
                    IMG_SIZE,
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
    test_loader
)


print(
    f"Test Loss: "
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


report = classification_report(
    true_labels,
    predictions,
    target_names=CLASS_NAMES,
    digits=4,
)


matrix = confusion_matrix(
    true_labels,
    predictions,
)


print("\nClassification Report:")
print(report)

print("\nConfusion Matrix:")
print(matrix)


# ============================================================
# SAVE RESULTS
# ============================================================

with open(
    RESULT_DIR / "classification_report.txt",
    "w",
) as f:

    f.write(report)

    f.write(
        "\n\nConfusion Matrix:\n"
    )

    f.write(
        str(matrix)
    )


print(
    "\nModel saved to:"
)

print(best_model_path)

print(
    "\nResults saved to:"
)

print(RESULT_DIR)
