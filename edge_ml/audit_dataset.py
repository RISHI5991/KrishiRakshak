from __future__ import annotations

import csv
import hashlib
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from PIL import Image, UnidentifiedImageError


# ============================================================
# CONFIG
# ============================================================

ROOT = Path(
    "/Users/rishisharma/Dhurandhar/"
    "Plant_leave_diseases_dataset_with_augmentation"
)

OUTPUT_DIR = Path(
    "/Users/rishisharma/Dhurandhar/edge_ml/dataset_audit"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

SUPPORTED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp",
}

# Perceptual near-duplicate threshold.
# Lower = stricter.
HAMMING_THRESHOLD = 4

# We use a 64-bit perceptual hash.
HASH_SIZE = 8

# ============================================================
# HELPERS
# ============================================================


def get_image_files(root: Path) -> list[Path]:
    return sorted(
        p
        for p in root.rglob("*")
        if p.is_file()
        and p.suffix.lower() in SUPPORTED_EXTENSIONS
    )


def sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()

    with path.open("rb") as f:
        while True:
            chunk = f.read(1024 * 1024)

            if not chunk:
                break

            hasher.update(chunk)

    return hasher.hexdigest()


def perceptual_hash(path: Path) -> int:
    """
    Simple 64-bit average hash.

    This is intended for finding likely near-duplicates,
    not for cryptographic identity.
    """
    with Image.open(path) as img:
        img = img.convert("L")
        img = img.resize(
            (HASH_SIZE, HASH_SIZE),
            Image.Resampling.LANCZOS
        )

        pixels = np.asarray(
            img,
            dtype=np.float32
        )

    threshold = pixels.mean()

    bits = pixels >= threshold

    value = 0

    for bit in bits.flatten():
        value = (value << 1) | int(bit)

    return value


def hamming_distance(a: int, b: int) -> int:
    return (a ^ b).bit_count()


def dimension_histogram(
    image_files: list[Path]
) -> tuple[Counter, list[Path]]:

    sizes = Counter()
    corrupt = []

    for i, path in enumerate(image_files, start=1):

        try:
            with Image.open(path) as img:
                img.verify()

            with Image.open(path) as img:
                sizes[img.size] += 1

        except (
            OSError,
            UnidentifiedImageError,
            ValueError
        ):
            corrupt.append(path)

        if i % 5000 == 0:
            print(
                f"Dimension scan: "
                f"{i}/{len(image_files)}"
            )

    return sizes, corrupt


# ============================================================
# START
# ============================================================

start_time = time.time()

print("=" * 80)
print("DHURANDHAR DATASET AUDIT")
print("=" * 80)

print(f"Dataset: {ROOT}")

if not ROOT.exists():
    print("\nERROR: Dataset directory does not exist.")
    sys.exit(1)

# ============================================================
# COLLECT FILES
# ============================================================

print("\n[1/5] Collecting image files...")

image_files = get_image_files(ROOT)

print(
    f"Total images found: "
    f"{len(image_files):,}"
)

if not image_files:
    print("ERROR: No images found.")
    sys.exit(1)


# ============================================================
# CLASS COUNTS
# ============================================================

print("\n[2/5] Counting classes...")

class_counts = Counter(
    path.parent.name
    for path in image_files
)

print(
    f"Classes found: "
    f"{len(class_counts)}"
)

for class_name, count in sorted(
    class_counts.items(),
    key=lambda x: (-x[1], x[0])
):
    print(
        f"{class_name:55s} "
        f"{count:6d}"
    )


# ============================================================
# DIMENSIONS + CORRUPTION
# ============================================================

print("\n[3/5] Checking image dimensions and corruption...")

dimensions, corrupt_files = dimension_histogram(
    image_files
)

print("\nImage dimensions:")

for size, count in dimensions.most_common():
    print(
        f"{str(size):15s} "
        f"{count:7d}"
    )

print(
    f"\nCorrupt/unreadable images: "
    f"{len(corrupt_files)}"
)

if corrupt_files:

    corrupt_path = (
        OUTPUT_DIR / "corrupt_images.txt"
    )

    with corrupt_path.open(
        "w",
        encoding="utf-8"
    ) as f:

        for path in corrupt_files:
            f.write(
                str(path)
                + "\n"
            )

    print(
        f"Corrupt list saved to:\n"
        f"{corrupt_path}"
    )


# ============================================================
# EXACT DUPLICATES
# ============================================================

print("\n[4/5] Checking exact duplicates...")

sha_to_files: dict[str, list[str]] = defaultdict(list)

for i, path in enumerate(
    image_files,
    start=1
):

    # Skip files already identified as corrupt.
    if path in corrupt_files:
        continue

    try:
        digest = sha256_file(path)
        sha_to_files[digest].append(
            str(path)
        )

    except OSError as exc:
        print(
            f"WARNING: could not hash "
            f"{path}: {exc}"
        )

    if i % 5000 == 0:
        print(
            f"SHA-256 scan: "
            f"{i}/{len(image_files)}"
        )


exact_duplicate_groups = [
    files
    for files in sha_to_files.values()
    if len(files) > 1
]

exact_duplicate_file_count = sum(
    len(group)
    for group in exact_duplicate_groups
)

print(
    f"\nUnique file hashes: "
    f"{len(sha_to_files):,}"
)

print(
    f"Exact duplicate groups: "
    f"{len(exact_duplicate_groups):,}"
)

print(
    f"Files belonging to exact-duplicate groups: "
    f"{exact_duplicate_file_count:,}"
)

exact_csv = (
    OUTPUT_DIR / "exact_duplicates.csv"
)

with exact_csv.open(
    "w",
    newline="",
    encoding="utf-8"
) as f:

    writer = csv.writer(f)

    writer.writerow([
        "group_id",
        "file_path",
    ])

    for group_id, group in enumerate(
        exact_duplicate_groups,
        start=1
    ):

        for file_path in group:
            writer.writerow([
                group_id,
                file_path,
            ])

print(
    f"Exact duplicate report:\n"
    f"{exact_csv}"
)


# ============================================================
# PERCEPTUAL HASH
# ============================================================

print(
    "\n[5/5] Checking likely near-duplicates..."
)

print(
    "This can take a while on 61k images."
)

# ------------------------------------------------------------
# We create three buckets based on three 16-bit chunks
# of the 64-bit perceptual hash.
#
# Two hashes with a small Hamming distance are likely
# to share at least one of these chunks.
# ------------------------------------------------------------

bucket_maps = [
    defaultdict(list),
    defaultdict(list),
    defaultdict(list),
]

hash_records = []

valid_counter = 0

for i, path in enumerate(
    image_files,
    start=1
):

    if path in corrupt_files:
        continue

    try:
        phash = perceptual_hash(path)

    except (
        OSError,
        UnidentifiedImageError,
        ValueError
    ):
        continue

    hash_records.append(
        (
            str(path),
            phash,
        )
    )

    valid_counter += 1

    parts = [
        (phash >> 48) & 0xFFFF,
        (phash >> 32) & 0xFFFF,
        (phash >> 16) & 0xFFFF,
    ]

    for bucket_id, part in enumerate(parts):
        bucket_maps[bucket_id][part].append(
            valid_counter - 1
        )

    if i % 5000 == 0:
        print(
            f"Perceptual hash: "
            f"{i}/{len(image_files)}"
        )


# ------------------------------------------------------------
# Candidate comparisons
# ------------------------------------------------------------

near_pairs = set()

for idx, (path_a, hash_a) in enumerate(
    hash_records
):

    candidate_indices = set()

    parts = [
        (hash_a >> 48) & 0xFFFF,
        (hash_a >> 32) & 0xFFFF,
        (hash_a >> 16) & 0xFFFF,
    ]

    for bucket_id, part in enumerate(parts):

        candidate_indices.update(
            bucket_maps[bucket_id][part]
        )

    for other_idx in candidate_indices:

        if other_idx <= idx:
            continue

        path_b, hash_b = hash_records[
            other_idx
        ]

        distance = hamming_distance(
            hash_a,
            hash_b
        )

        if distance <= HAMMING_THRESHOLD:

            # Canonical ordering prevents duplicate pairs.
            pair = (
                min(path_a, path_b),
                max(path_a, path_b),
            )

            near_pairs.add(
                (
                    pair[0],
                    pair[1],
                    distance,
                )
            )


print(
    f"\nLikely near-duplicate pairs: "
    f"{len(near_pairs):,}"
)

near_csv = (
    OUTPUT_DIR /
    "near_duplicates.csv"
)

with near_csv.open(
    "w",
    newline="",
    encoding="utf-8"
) as f:

    writer = csv.writer(f)

    writer.writerow([
        "file_a",
        "file_b",
        "hamming_distance",
        "same_class",
    ])

    for path_a, path_b, distance in sorted(
        near_pairs,
        key=lambda x: x[2]
    ):

        class_a = Path(path_a).parent.name
        class_b = Path(path_b).parent.name

        writer.writerow([
            path_a,
            path_b,
            distance,
            class_a == class_b,
        ])


# ============================================================
# SUMMARY
# ============================================================

print("\n")
print("=" * 80)
print("AUDIT SUMMARY")
print("=" * 80)

print(
    f"Total images:                "
    f"{len(image_files):,}"
)

print(
    f"Classes:                     "
    f"{len(class_counts)}"
)

print(
    f"Corrupt/unreadable:          "
    f"{len(corrupt_files):,}"
)

print(
    f"Exact duplicate groups:      "
    f"{len(exact_duplicate_groups):,}"
)

print(
    f"Exact duplicate files:       "
    f"{exact_duplicate_file_count:,}"
)

print(
    f"Likely near-duplicate pairs: "
    f"{len(near_pairs):,}"
)

print(
    f"\nReports saved in:\n"
    f"{OUTPUT_DIR}"
)

elapsed = time.time() - start_time

print(
    f"\nAudit time: "
    f"{elapsed / 60:.2f} minutes"
)

print("=" * 80)