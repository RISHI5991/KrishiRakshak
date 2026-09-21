from __future__ import annotations

import csv
import hashlib
import sys
import time
from collections import defaultdict
from pathlib import Path

import faiss
import numpy as np
import torch
import torch.nn.functional as F
import timm

from PIL import Image
from torchvision import transforms


# ============================================================
# CONFIG
# ============================================================

DATASET_ROOT = Path(
    "/Users/rishisharma/Dhurandhar/"
    "Plant_leave_diseases_dataset_with_augmentation"
)

OUTPUT_DIR = Path(
    "/Users/rishisharma/Dhurandhar/edge_ml/"
    "dataset_audit_v2"
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

IMAGE_SIZE = 518
BATCH_SIZE = 32
TOP_K = 10

# IMPORTANT:
# This is a candidate threshold, NOT a final
# duplicate decision threshold.
DINO_THRESHOLD = 0.94


# ============================================================
# DEVICE
# ============================================================

DEVICE = torch.device("cpu")

print("Device:", DEVICE)


# ============================================================
# FILES
# ============================================================

def collect_images(root: Path):
    return sorted(
        p
        for p in root.rglob("*")
        if p.is_file()
        and p.suffix.lower() in SUPPORTED_EXTENSIONS
    )


# ============================================================
# SHA256
# ============================================================

def sha256_file(path: Path):

    h = hashlib.sha256()

    with path.open("rb") as f:

        while True:

            chunk = f.read(1024 * 1024)

            if not chunk:
                break

            h.update(chunk)

    return h.hexdigest()


# ============================================================
# DINO TRANSFORM
# ============================================================

transform = transforms.Compose(
    [
        transforms.Resize(
            IMAGE_SIZE,
            interpolation=
            transforms.InterpolationMode.BICUBIC,
        ),
        transforms.CenterCrop(
            IMAGE_SIZE
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
    ]
)


# ============================================================
# LOAD DINO
# ============================================================

def load_model():

    print(
        "\nLoading DINOv2..."
    )

    model = timm.create_model(
        "vit_small_patch14_dinov2.lvd142m",
        pretrained=True,
        num_classes=0,
    )

    model = model.to(
        DEVICE
    )

    model.eval()

    print(
        "DINOv2 loaded."
    )

    return model


# ============================================================
# EMBEDDINGS
# ============================================================

def compute_embeddings(
    paths,
    model,
):

    embedding_path = (
        OUTPUT_DIR /
        "dino_embeddings.npy"
    )

    # Reuse existing embeddings.
    if embedding_path.exists():

        print(
            "\nExisting embeddings found."
        )

        embeddings = np.load(
            embedding_path
        )

        print(
            "Embedding shape:",
            embeddings.shape
        )

        return embeddings


    embeddings = []

    total = len(paths)

    print(
        f"\nComputing embeddings "
        f"for {total:,} images..."
    )

    with torch.inference_mode():

        for start in range(
            0,
            total,
            BATCH_SIZE,
        ):

            batch_paths = paths[
                start:
                start + BATCH_SIZE
            ]

            tensors = []

            valid = []

            for path in batch_paths:

                try:

                    with Image.open(
                        path
                    ) as img:

                        img = img.convert(
                            "RGB"
                        )

                        tensors.append(
                            transform(img)
                        )

                        valid.append(path)

                except Exception as exc:

                    print(
                        f"Skipping {path}: "
                        f"{exc}"
                    )

            if not tensors:
                continue

            x = torch.stack(
                tensors
            ).to(
                DEVICE
            )

            features = model(x)

            features = F.normalize(
                features,
                p=2,
                dim=1,
            )

            embeddings.append(
                features.cpu().numpy()
            )

            done = min(
                start + BATCH_SIZE,
                total,
            )

            if (
                done % 500 == 0
                or done == total
            ):

                print(
                    f"Embeddings: "
                    f"{done:,}/{total:,}"
                )

    embeddings = np.concatenate(
        embeddings,
        axis=0,
    ).astype(
        np.float32
    )

    np.save(
        embedding_path,
        embeddings
    )

    print(
        "\nSaved embeddings:"
    )

    print(
        embedding_path
    )

    return embeddings


# ============================================================
# FAISS SEARCH
# ============================================================

def find_nearest_neighbors(
    embeddings
):

    print(
        "\nBuilding FAISS index..."
    )

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatIP(
        dimension
    )

    # Embeddings are normalized.
    # Therefore inner product = cosine similarity.
    index.add(
        embeddings
    )

    print(
        f"Indexed {index.ntotal:,} embeddings."
    )

    print(
        "\nSearching nearest neighbors..."
    )

    # Search TOP_K + 1 because every image
    # will find itself as nearest neighbor.
    similarities, indices = index.search(
        embeddings,
        TOP_K + 1,
    )

    return similarities, indices


# ============================================================
# SAVE NEAREST NEIGHBORS
# ============================================================

def save_pairs(
    paths,
    similarities,
    indices,
):

    output_csv = (
        OUTPUT_DIR /
        "dino_nearest_neighbors.csv"
    )

    seen = set()

    rows = []

    for i in range(
        len(paths)
    ):

        for rank in range(
            1,
            TOP_K + 1
        ):

            j = int(
                indices[i, rank]
            )

            score = float(
                similarities[i, rank]
            )

            if score < DINO_THRESHOLD:
                continue

            a, b = sorted(
                (i, j)
            )

            if a == b:
                continue

            key = (
                a,
                b
            )

            if key in seen:
                continue

            seen.add(key)

            class_a = (
                paths[a].parent.name
            )

            class_b = (
                paths[b].parent.name
            )

            rows.append(
                (
                    str(paths[a]),
                    str(paths[b]),
                    score,
                    class_a,
                    class_b,
                    class_a == class_b,
                )
            )

    rows.sort(
        key=lambda x: -x[2]
    )

    with output_csv.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as f:

        writer = csv.writer(f)

        writer.writerow(
            [
                "file_a",
                "file_b",
                "cosine_similarity",
                "class_a",
                "class_b",
                "same_class",
            ]
        )

        writer.writerows(
            rows
        )

    return rows


# ============================================================
# BUILD CONNECTED COMPONENTS
# ============================================================

class UnionFind:

    def __init__(self, n):

        self.parent = list(
            range(n)
        )

        self.rank = [0] * n

    def find(self, x):

        while (
            self.parent[x] != x
        ):

            self.parent[x] = (
                self.parent[
                    self.parent[x]
                ]
            )

            x = self.parent[x]

        return x

    def union(self, a, b):

        ra = self.find(a)
        rb = self.find(b)

        if ra == rb:
            return

        if self.rank[ra] < self.rank[rb]:

            self.parent[ra] = rb

        elif self.rank[ra] > self.rank[rb]:

            self.parent[rb] = ra

        else:

            self.parent[rb] = ra
            self.rank[ra] += 1


# ============================================================
# GROUPING
# ============================================================

def build_groups(
    paths,
    rows,
):

    path_to_index = {
        str(path): i
        for i, path in enumerate(paths)
    }

    uf = UnionFind(
        len(paths)
    )

    for (
        file_a,
        file_b,
        score,
        class_a,
        class_b,
        same_class,
    ) in rows:

        a = path_to_index[
            file_a
        ]

        b = path_to_index[
            file_b
        ]

        uf.union(
            a,
            b
        )

    groups = defaultdict(list)

    for i in range(
        len(paths)
    ):

        root = uf.find(i)

        groups[root].append(i)

    groups = [
        group
        for group in groups.values()
        if len(group) > 1
    ]

    cross_class_groups = []

    for group in groups:

        classes = {
            paths[i].parent.name
            for i in group
        }

        if len(classes) > 1:

            cross_class_groups.append(
                (
                    group,
                    classes,
                )
            )

    output_csv = (
        OUTPUT_DIR /
        "dino_duplicate_groups.csv"
    )

    with output_csv.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as f:

        writer = csv.writer(f)

        writer.writerow(
            [
                "group_id",
                "file_path",
                "class",
            ]
        )

        for group_id, group in enumerate(
            groups,
            start=1
        ):

            for i in group:

                writer.writerow(
                    [
                        group_id,
                        str(paths[i]),
                        paths[i].parent.name,
                    ]
                )

    return groups, cross_class_groups


# ============================================================
# MAIN
# ============================================================

def main():

    start = time.time()

    print("=" * 80)
    print("DHURANDHAR DATASET AUDIT V2")
    print("=" * 80)

    if not DATASET_ROOT.exists():

        print(
            "Dataset not found:"
        )

        print(
            DATASET_ROOT
        )

        sys.exit(1)

    paths = collect_images(
        DATASET_ROOT
    )

    print(
        f"\nImages: {len(paths):,}"
    )

    # --------------------------------------------------------
    # Exact duplicate check
    # --------------------------------------------------------

    print(
        "\nChecking SHA-256..."
    )

    sha_groups = defaultdict(list)

    for i, path in enumerate(
        paths,
        start=1
    ):

        digest = sha256_file(
            path
        )

        sha_groups[
            digest
        ].append(i - 1)

        if (
            i % 10000 == 0
            or i == len(paths)
        ):

            print(
                f"SHA: "
                f"{i:,}/{len(paths):,}"
            )

    exact_groups = [
        group
        for group in sha_groups.values()
        if len(group) > 1
    ]

    cross_exact = 0

    for group in exact_groups:

        classes = {
            paths[i].parent.name
            for i in group
        }

        if len(classes) > 1:

            cross_exact += 1

    print(
        f"\nExact duplicate groups: "
        f"{len(exact_groups):,}"
    )

    print(
        f"Cross-class exact groups: "
        f"{cross_exact:,}"
    )

    # --------------------------------------------------------
    # DINO
    # --------------------------------------------------------

    model = load_model()

    embeddings = compute_embeddings(
        paths,
        model
    )

    # --------------------------------------------------------
    # FAISS
    # --------------------------------------------------------

    similarities, indices = (
        find_nearest_neighbors(
            embeddings
        )
    )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    rows = save_pairs(
        paths,
        similarities,
        indices
    )

    print(
        f"\nPairs above threshold "
        f"({DINO_THRESHOLD}): "
        f"{len(rows):,}"
    )

    # --------------------------------------------------------
    # Groups
    # --------------------------------------------------------

    groups, cross_class_groups = (
        build_groups(
            paths,
            rows
        )
    )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    print("\n")
    print("=" * 80)
    print("V2 SUMMARY")
    print("=" * 80)

    print(
        f"Images:                    {len(paths):,}"
    )

    print(
        f"Exact duplicate groups:    {len(exact_groups):,}"
    )

    print(
        f"Cross-class exact groups:  {cross_exact:,}"
    )

    print(
        f"DINO candidate pairs:      {len(rows):,}"
    )

    print(
        f"DINO duplicate groups:     {len(groups):,}"
    )

    print(
        f"Cross-class DINO groups:   "
        f"{len(cross_class_groups):,}"
    )

    print(
        "\nOutput directory:"
    )

    print(
        OUTPUT_DIR
    )

    print(
        f"\nRuntime: "
        f"{(time.time() - start) / 60:.2f} minutes"
    )

    print("=" * 80)


if __name__ == "__main__":
    main()