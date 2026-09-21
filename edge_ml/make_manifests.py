from __future__ import annotations

import csv
import hashlib
import random
from collections import defaultdict
from pathlib import Path


# ============================================================
# CONFIG
# ============================================================

ROOT = Path(
    "/Users/rishisharma/Dhurandhar/"
    "Plant_leave_diseases_dataset_with_augmentation"
)

OUTPUT = Path(
    "/Users/rishisharma/Dhurandhar/edge_ml/manifests"
)

OUTPUT.mkdir(
    parents=True,
    exist_ok=True
)

SEED = 42

TRAIN_RATIO = 0.80
VAL_RATIO = 0.10
TEST_RATIO = 0.10

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp",
}


# ============================================================
# HELPERS
# ============================================================

def sha256_file(path: Path) -> str:

    h = hashlib.sha256()

    with path.open("rb") as f:

        while True:

            chunk = f.read(1024 * 1024)

            if not chunk:
                break

            h.update(chunk)

    return h.hexdigest()


def parse_class_name(dirname: str):

    if dirname == "Background_without_leaves":

        return (
            "Unknown",
            None,
        )

    if "___" not in dirname:

        raise ValueError(
            f"Unexpected class directory: {dirname}"
        )

    crop, condition = dirname.split(
        "___",
        1
    )

    # Normalize crop naming.
    crop = crop.replace(
        ",_",
        ", "
    )

    crop = crop.replace(
        "_",
        " "
    )

    return (
        crop,
        condition,
    )


def collect_images():

    return sorted(
        p
        for p in ROOT.rglob("*")
        if p.is_file()
        and p.suffix.lower()
        in IMAGE_EXTENSIONS
    )


# ============================================================
# LOAD FILES
# ============================================================

print("=" * 80)
print("DHURANDHAR MANIFEST GENERATION")
print("=" * 80)

images = collect_images()

print(
    f"Images found: {len(images):,}"
)

# ============================================================
# BUILD EXACT-DUPLICATE GROUPS
# ============================================================

print("\nBuilding exact-duplicate groups...")

sha_groups = defaultdict(list)

for i, path in enumerate(
    images,
    start=1
):

    digest = sha256_file(path)

    sha_groups[digest].append(path)

    if (
        i % 10000 == 0
        or i == len(images)
    ):

        print(
            f"Hashed: "
            f"{i:,}/{len(images):,}"
        )


# ============================================================
# CREATE GROUPS
# ============================================================

groups = []

group_counter = 0

for digest, paths in sha_groups.items():

    group_counter += 1

    for path in paths:
        crop, condition = parse_class_name(
            path.parent.name
        )

    groups.append(
        {
            "group_id": f"G{group_counter:06d}",
            "sha256": digest,
            "paths": sorted(paths),
            "class_dir": paths[0].parent.name,
            "crop": crop,
            "condition": condition,
        }
    )


print(
    f"\nTotal exact-duplicate groups: "
    f"{sum(1 for g in groups if len(g['paths']) > 1):,}"
)


# ============================================================
# SPLIT GROUPS BY CLASS
# ============================================================

groups_by_class = defaultdict(list)

for group in groups:

    groups_by_class[
        group["class_dir"]
    ].append(group)


rng = random.Random(SEED)

assignments = {}

print("\nCreating stratified split...")

for class_dir in sorted(
    groups_by_class
):

    class_groups = groups_by_class[
        class_dir
    ]

    rng.shuffle(
        class_groups
    )

    n = len(class_groups)

    # Initial boundaries.
    n_train = round(
        n * TRAIN_RATIO
    )

    n_val = round(
        n * VAL_RATIO
    )

    # Make sure every non-trivial class has
    # at least one test group.
    n_train = min(
        n_train,
        n - 1
    )

    n_val = min(
        n_val,
        n - n_train - 1
    )

    train_groups = class_groups[
        :n_train
    ]

    val_groups = class_groups[
        n_train:
        n_train + n_val
    ]

    test_groups = class_groups[
        n_train + n_val:
    ]

    for group in train_groups:
        assignments[
            group["group_id"]
        ] = "train"

    for group in val_groups:
        assignments[
            group["group_id"]
        ] = "val"

    for group in test_groups:
        assignments[
            group["group_id"]
        ] = "test"


# ============================================================
# CREATE ROWS
# ============================================================

rows = []

for group in groups:

    split = assignments[
        group["group_id"]
    ]

    for path in group["paths"]:

        crop, condition = parse_class_name(
            path.parent.name
        )

        rows.append(
            {
            "path": str(path),
            "split": split,
            "group_id": group["group_id"],
            "class_dir": path.parent.name,

             # M1 = crop identity
            "m1_label": crop,
            "m1_class": crop,

            # M2 = complete crop-condition identity
            # Example:
            # Apple___Apple_scab
            # Tomato___Early_blight
            # Potato___healthy
            "m2_label": (
                path.parent.name
                if condition is not None
                else ""
            ),
            "m2_class": (
                path.parent.name
                if condition is not None
                else ""
        ),
    }
)
        


# ============================================================
# SORT
# ============================================================

rows.sort(
    key=lambda r: (
        r["split"],
        r["class_dir"],
        r["path"],
    )
)


# ============================================================
# SAVE
# ============================================================

fieldnames = [
    "path",
    "split",
    "group_id",
    "class_dir",
    "m1_label",
    "m2_label",
    "m1_class",
    "m2_class",
]

all_csv = OUTPUT / "all.csv"

with all_csv.open(
    "w",
    newline="",
    encoding="utf-8"
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=fieldnames
    )

    writer.writeheader()
    writer.writerows(rows)


for split in [
    "train",
    "val",
    "test",
]:

    split_rows = [
        r
        for r in rows
        if r["split"] == split
    ]

    output_file = (
        OUTPUT / f"{split}.csv"
    )

    with output_file.open(
        "w",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(
            split_rows
        )


# ============================================================
# SUMMARY
# ============================================================

print("\n")
print("=" * 80)
print("SPLIT SUMMARY")
print("=" * 80)

for split in [
    "train",
    "val",
    "test",
]:

    split_rows = [
        r
        for r in rows
        if r["split"] == split
    ]

    unique_groups = len({
        r["group_id"]
        for r in split_rows
    })

    print(
        f"{split.upper():6s}: "
        f"{len(split_rows):7,} images | "
        f"{unique_groups:7,} groups"
    )


# ============================================================
# CLASS DISTRIBUTION
# ============================================================

print("\nClass distribution:")

for class_dir in sorted(
    groups_by_class
):

    counts = {}

    for split in [
        "train",
        "val",
        "test",
    ]:

        counts[split] = sum(
            1
            for r in rows
            if (
                r["class_dir"]
                == class_dir
                and r["split"]
                == split
            )
        )

    print(
        f"{class_dir:55s} "
        f"{counts['train']:5d} "
        f"{counts['val']:5d} "
        f"{counts['test']:5d}"
    )


# ============================================================
# DUPLICATE SAFETY CHECK
# ============================================================

print("\nChecking duplicate-group leakage...")

group_splits = defaultdict(set)

for row in rows:

    group_splits[
        row["group_id"]
    ].add(
        row["split"]
    )

leaking_groups = {
    group_id: splits
    for group_id, splits
    in group_splits.items()
    if len(splits) > 1
}

print(
    f"Groups crossing splits: "
    f"{len(leaking_groups)}"
)

if leaking_groups:

    raise RuntimeError(
        "ERROR: exact duplicate group leakage detected."
    )


# ============================================================
# M1/M2 LABEL SUMMARY
# ============================================================

m1_classes = sorted({
    r["m1_label"]
    for r in rows
})

m2_classes = sorted({
    r["m2_label"]
    for r in rows
    if r["m2_label"]
})


print("\n")
print("=" * 80)
print("LABEL SUMMARY")
print("=" * 80)

print(
    f"M1 classes: {len(m1_classes)}"
)

for i, label in enumerate(
    m1_classes
):
    print(
        f"  {i:2d}: {label}"
    )


print(
    f"\nM2 classes: {len(m2_classes)}"
)

for i, label in enumerate(
    m2_classes
):
    print(
        f"  {i:2d}: {label}"
    )


# ============================================================
# SAVE LABEL MAPS
# ============================================================

m1_map = {
    label: i
    for i, label in enumerate(
        m1_classes
    )
}

m2_map = {
    label: i
    for i, label in enumerate(
        m2_classes
    )
}

with (
    OUTPUT / "m1_labels.csv"
).open(
    "w",
    newline="",
    encoding="utf-8"
) as f:

    writer = csv.writer(f)

    writer.writerow([
        "index",
        "label",
    ])

    for label, index in m1_map.items():

        writer.writerow([
            index,
            label,
        ])


with (
    OUTPUT / "m2_labels.csv"
).open(
    "w",
    newline="",
    encoding="utf-8"
) as f:

    writer = csv.writer(f)

    writer.writerow([
        "index",
        "label",
    ])

    for label, index in m2_map.items():

        writer.writerow([
            index,
            label,
        ])


print("\n")
print("Manifests written to:")
print(OUTPUT)

print("\nFiles:")
print("  all.csv")
print("  train.csv")
print("  val.csv")
print("  test.csv")
print("  m1_labels.csv")
print("  m2_labels.csv")

print("=" * 80)