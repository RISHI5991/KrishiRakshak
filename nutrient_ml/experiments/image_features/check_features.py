from pathlib import Path
import numpy as np

FEATURE_DIR = Path(
    r"D:\Dhurandhar\nutrient_ml\sensor_ml\data\processed\image_features"
)

files = list(FEATURE_DIR.rglob("*.npz"))

print("======================================")
print("IMAGE FEATURE CHECK")
print("======================================")

print("Total feature files:", len(files))

if not files:
    raise RuntimeError("No .npz feature files found.")

sample = files[0]

data = np.load(sample)

embedding = data["embedding"]

print()
print("Sample file:")
print(sample)

print()
print("Embedding shape:", embedding.shape)
print("Embedding dtype:", embedding.dtype)

print()
print("True class:", data["true_class"])
print("Predicted class:", data["predicted_class"])
print("Confidence:", float(data["confidence"]))

print()
print("======================================")
print("CHECK COMPLETE")
print("======================================")