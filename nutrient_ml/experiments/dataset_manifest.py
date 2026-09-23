from pathlib import Path
import csv


# =========================================================
# DHURANDHAR - IMAGE DATASET MANIFEST
# =========================================================

DATA_DIR = Path(
    r"D:\Dhurandhar\nutrient_ml\data\HARN_Rice"
)

OUTPUT_FILE = Path(
    r"D:\Dhurandhar\nutrient_ml\data\npk_dataset_manifest.csv"
)

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


# =========================================================
# COLLECT IMAGES
# =========================================================

records = []

print("======================================")
print("DHURANDHAR IMAGE DATASET MANIFEST")
print("======================================")

print()
print("Dataset:")
print(DATA_DIR)

for class_name in CLASS_NAMES:

    class_dir = DATA_DIR / class_name

    if not class_dir.exists():

        print(
            f"WARNING: missing folder: {class_dir}"
        )

        continue

    image_files = sorted(
        [
            p
            for p in class_dir.rglob("*")
            if p.is_file()
            and p.suffix.lower() in IMAGE_EXTENSIONS
        ]
    )

    print(
        f"{class_name}: {len(image_files)} images"
    )

    for image_path in image_files:

        records.append({
            "image_path": str(image_path),
            "class": class_name,
            "filename": image_path.name,
        })


# =========================================================
# WRITE MANIFEST
# =========================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True,
)

with open(
    OUTPUT_FILE,
    "w",
    newline="",
    encoding="utf-8",
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=[
            "image_path",
            "class",
            "filename",
        ],
    )

    writer.writeheader()

    writer.writerows(records)


# =========================================================
# SUMMARY
# =========================================================

print()
print("======================================")
print("MANIFEST CREATED")
print("======================================")

print()
print("Total images:", len(records))

print()
print("Output:")
print(OUTPUT_FILE)

print()
print("Class counts:")

for class_name in CLASS_NAMES:

    count = sum(
        1
        for record in records
        if record["class"] == class_name
    )

    print(
        f"  {class_name:18s}: {count}"
    )

print()
print("======================================")
print("DONE")
print("======================================")