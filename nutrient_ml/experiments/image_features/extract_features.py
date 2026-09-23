from pathlib import Path

import torch
import timm
import numpy as np
from PIL import Image
from torchvision import transforms


# =========================================================
# PATHS
# =========================================================

MODEL_PATH = Path(
    r"D:\Dhurandhar\nutrient_ml\models\npk_vision_baseline_v1.pt"
)

DATA_DIR = Path(
    r"D:\Dhurandhar\nutrient_ml\data\HARN_Rice"
)

OUTPUT_DIR = Path(
    r"D:\Dhurandhar\nutrient_ml\sensor_ml\data\processed\image_features"
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# =========================================================
# MODEL
# =========================================================

MODEL_NAME = "mobilenetv4_conv_small.e2400_r224_in1k"

CLASS_NAMES = [
    "Healthy",
    "K_Deficiency",
    "N_Deficiency",
    "P_Deficiency",
]

IMG_SIZE = 224

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)


# =========================================================
# LOAD MODEL
# =========================================================

print("Loading MobileNetV4...")

model = timm.create_model(
    MODEL_NAME,
    pretrained=False,
    num_classes=4,
)

checkpoint = torch.load(
    MODEL_PATH,
    map_location=DEVICE,
)

model.load_state_dict(
    checkpoint["model_state_dict"]
)

model = model.to(DEVICE)
model.eval()

print("Model loaded.")
print("Device:", DEVICE)


# =========================================================
# IMAGE TRANSFORM
# =========================================================

transform = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(
        [0.485, 0.456, 0.406],
        [0.229, 0.224, 0.225],
    ),
])


# =========================================================
# FEATURE EXTRACTION
# =========================================================

def extract_image_features(image_path):

    image = Image.open(image_path).convert("RGB")

    tensor = transform(image).unsqueeze(0)
    tensor = tensor.to(DEVICE)

    with torch.no_grad():

        # Final spatial feature map
        feature_map = model.forward_features(tensor)

        # Pooled feature embedding before classifier
        embedding = model.forward_head(
            feature_map,
            pre_logits=True,
        )

        # Classification output
        logits = model.forward_head(
            feature_map,
            pre_logits=False,
        )

        probabilities = torch.softmax(
            logits,
            dim=1,
        )

        predicted_index = int(
            logits.argmax(dim=1).item()
        )

        confidence = float(
            probabilities[
                0,
                predicted_index
            ].item()
        )

    embedding = embedding.squeeze(0).cpu().numpy()

    return (
        embedding,
        predicted_index,
        confidence,
    )


# =========================================================
# PROCESS DATASET
# =========================================================

print()
print("Extracting image features...")
print()

total = 0

for class_name in CLASS_NAMES:

    class_dir = DATA_DIR / class_name

    if not class_dir.exists():
        print(
            f"WARNING: missing folder: {class_dir}"
        )
        continue

    output_class_dir = OUTPUT_DIR / class_name
    output_class_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    image_files = sorted(
        list(class_dir.glob("*.jpg"))
        + list(class_dir.glob("*.jpeg"))
        + list(class_dir.glob("*.png"))
    )

    print(
        f"{class_name}: {len(image_files)} images"
    )

    for image_path in image_files:

        try:

            (
                embedding,
                predicted_index,
                confidence,
            ) = extract_image_features(
                image_path
            )

            output_path = (
                output_class_dir
                / f"{image_path.stem}.npz"
            )

            np.savez_compressed(
                output_path,
                embedding=embedding,
                true_class=class_name,
                predicted_class=CLASS_NAMES[
                    predicted_index
                ],
                confidence=confidence,
                image_path=str(image_path),
            )

            total += 1

        except Exception as e:

            print(
                f"ERROR: {image_path.name}"
            )

            print(e)


# =========================================================
# DONE
# =========================================================

print()
print("======================================")
print("IMAGE FEATURE EXTRACTION COMPLETE")
print("======================================")
print("Total images:", total)
print("Output folder:")
print(OUTPUT_DIR)