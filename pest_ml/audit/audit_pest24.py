from __future__ import annotations

import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
import xml.etree.ElementTree as ET

from PIL import Image

ROOT = Path("datasets/Pest24/VOCdevkit/voc2007")

IMAGE_DIR = ROOT / "images"
XML_DIR = ROOT / "Annotations"
YOLO_DIR = ROOT / "labels"
SPLIT_DIR = ROOT / "ImageSets" / "Main"

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG"}

EXPECTED_CLASSES = 24


def sha256(path: Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(chunk_size):
            h.update(chunk)
    return h.hexdigest()


def load_yolo(path: Path):
    rows = []
    text = path.read_text(errors="ignore").strip()

    if not text:
        return rows

    for line_no, line in enumerate(text.splitlines(), start=1):
        parts = line.split()

        if len(parts) != 5:
            raise ValueError(
                f"{path.name}: line {line_no}: expected 5 fields, got {len(parts)}"
            )

        cls = int(parts[0])
        x, y, w, h = map(float, parts[1:])

        rows.append((cls, x, y, w, h))

    return rows


def load_xml(path: Path):
    tree = ET.parse(path)
    root = tree.getroot()

    objects = []

    for obj in root.findall("object"):
        name = obj.findtext("name", default="").strip()
        bbox = obj.find("bndbox")

        if bbox is None:
            raise ValueError(f"{path.name}: object without bndbox")

        xmin = float(bbox.findtext("xmin"))
        ymin = float(bbox.findtext("ymin"))
        xmax = float(bbox.findtext("xmax"))
        ymax = float(bbox.findtext("ymax"))

        objects.append(
            (name, xmin, ymin, xmax, ymax)
        )

    return objects


def numeric_stem(stem: str) -> str:
    m = re.search(r"\d+$", stem)
    return m.group(0) if m else stem


def main():
    print("=" * 80)
    print("Pest24 DATASET AUDIT")
    print("=" * 80)
    print("Root:", ROOT.resolve())

    if not ROOT.exists():
        raise FileNotFoundError(f"Dataset root not found: {ROOT}")

    # ------------------------------------------------------------
    # 1. Collect images / annotations
    # ------------------------------------------------------------

    print("\n[1/7] Collecting files...")

    images = sorted(
        p for p in IMAGE_DIR.iterdir()
        if p.is_file() and p.suffix in IMAGE_EXTS
    )

    xmls = sorted(XML_DIR.glob("*.xml"))
    yolos = sorted(YOLO_DIR.glob("*.txt"))

    image_map = {p.stem: p for p in images}
    xml_map = {p.stem: p for p in xmls}
    yolo_map = {p.stem: p for p in yolos}

    print("Images:", len(images))
    print("XML:", len(xmls))
    print("YOLO:", len(yolos))

    # ------------------------------------------------------------
    # 2. Image integrity
    # ------------------------------------------------------------

    print("\n[2/7] Checking images...")

    corrupt = []
    dimensions = Counter()

    for i, path in enumerate(images, start=1):
        try:
            with Image.open(path) as im:
                im.verify()

            with Image.open(path) as im:
                dimensions[im.size] += 1

        except Exception as e:
            corrupt.append((path.name, str(e)))

        if i % 5000 == 0 or i == len(images):
            print(f"Images checked: {i}/{len(images)}")

    print("\nImage dimensions:")
    for size, count in dimensions.most_common():
        print(f"  {size}: {count}")

    print("Corrupt images:", len(corrupt))

    # ------------------------------------------------------------
    # 3. Annotation integrity + cross-format comparison
    # ------------------------------------------------------------

    print("\n[3/7] Checking annotations...")

    missing_xml = []
    missing_yolo = []

    empty_yolo = []
    invalid_yolo = []
    invalid_class = []
    invalid_box = []

    class_counts = Counter()
    image_object_counts = Counter()

    # XML classes, by exact string
    xml_class_counts = Counter()

    # YOLO → XML consistency based on geometric boxes
    conversion_mismatches = 0

    # We first establish the 24 class names from XML.
    all_xml_classes = set()

    for stem, image_path in image_map.items():

        xml_path = xml_map.get(stem)
        yolo_path = yolo_map.get(stem)

        if xml_path is None:
            missing_xml.append(stem)

        if yolo_path is None:
            missing_yolo.append(stem)

        if xml_path is not None:
            try:
                xml_objects = load_xml(xml_path)
            except Exception as e:
                conversion_mismatches += 1
                xml_objects = []

            image_object_counts["xml"] += len(xml_objects)

            for name, xmin, ymin, xmax, ymax in xml_objects:
                all_xml_classes.add(name)
                xml_class_counts[name] += 1

        else:
            xml_objects = []

        if yolo_path is not None:

            text = yolo_path.read_text(errors="ignore").strip()

            if not text:
                empty_yolo.append(stem)
                yolo_objects = []

            else:
                try:
                    yolo_objects = load_yolo(yolo_path)
                except Exception as e:
                    invalid_yolo.append((stem, str(e)))
                    yolo_objects = []

            image_object_counts["yolo"] += len(yolo_objects)

            for cls, x, y, w, h in yolo_objects:

                if not (0 <= cls < EXPECTED_CLASSES):
                    invalid_class.append(
                        (stem, cls)
                    )
                    continue

                if not (
                    0.0 <= x <= 1.0 and
                    0.0 <= y <= 1.0 and
                    0.0 < w <= 1.0 and
                    0.0 < h <= 1.0
                ):
                    invalid_box.append(
                        (stem, cls, x, y, w, h)
                    )
                    continue

                class_counts[cls] += 1

    print("Missing XML:", len(missing_xml))
    print("Missing YOLO:", len(missing_yolo))
    print("Empty YOLO:", len(empty_yolo))
    print("Invalid YOLO files/lines:", len(invalid_yolo))
    print("Invalid class IDs:", len(invalid_class))
    print("Invalid boxes:", len(invalid_box))

    print("\nXML classes discovered:", len(all_xml_classes))
    for name in sorted(all_xml_classes):
        print(" ", name)

    print("\nYOLO object count:", sum(class_counts.values()))
    print("XML object count :", sum(xml_class_counts.values()))

    # ------------------------------------------------------------
    # 4. Split integrity
    # ------------------------------------------------------------

    print("\n[4/7] Checking train / val / test splits...")

    splits = {}

    for split in ["train", "val", "test"]:
        path = SPLIT_DIR / f"{split}.txt"

        if not path.exists():
            print(f"{split}: MISSING")
            continue

        stems = []
        for line in path.read_text(errors="ignore").splitlines():
            line = line.strip()
            if not line:
                continue

            # Handles paths or plain IDs.
            stems.append(Path(line).stem)

        splits[split] = stems

        missing_from_images = [
            s for s in stems if s not in image_map
        ]

        print(
            f"{split.upper():5s}: {len(stems):6d} images | "
            f"missing from images: {len(missing_from_images)}"
        )

    split_sets = {
        k: set(v) for k, v in splits.items()
    }

    names = list(split_sets)

    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a = names[i]
            b = names[j]
            overlap = split_sets[a] & split_sets[b]
            print(
                f"Overlap {a}/{b}: {len(overlap)}"
            )

    # ------------------------------------------------------------
    # 5. Duplicate analysis
    # ------------------------------------------------------------

    print("\n[5/7] Checking exact duplicates...")

    hash_groups = defaultdict(list)

    for i, path in enumerate(images, start=1):
        digest = sha256(path)
        hash_groups[digest].append(path.stem)

        if i % 5000 == 0 or i == len(images):
            print(f"Hashed: {i}/{len(images)}")

    duplicate_groups = {
        h: stems
        for h, stems in hash_groups.items()
        if len(stems) > 1
    }

    print("Unique hashes:", len(hash_groups))
    print("Duplicate groups:", len(duplicate_groups))
    print(
        "Images in duplicate groups:",
        sum(len(v) for v in duplicate_groups.values())
    )

    # ------------------------------------------------------------
    # 6. Bounding box statistics
    # ------------------------------------------------------------

    print("\n[6/7] Bounding-box statistics...")

    area_values = []
    boxes_per_image = []

    size_bins = Counter()

    for stem, yolo_path in yolo_map.items():

        try:
            rows = load_yolo(yolo_path)
        except Exception:
            continue

        valid_rows = []

        for cls, x, y, w, h in rows:

            if 0 <= cls < EXPECTED_CLASSES and \
               0 <= x <= 1 and \
               0 <= y <= 1 and \
               0 < w <= 1 and \
               0 < h <= 1:

                valid_rows.append((cls, x, y, w, h))

        boxes_per_image.append(len(valid_rows))

        for cls, x, y, w, h in valid_rows:

            area = w * h
            area_values.append(area)

            if area < 0.01:
                size_bins["<1%"] += 1
            elif area < 0.03:
                size_bins["1-3%"] += 1
            elif area < 0.10:
                size_bins["3-10%"] += 1
            elif area < 0.25:
                size_bins["10-25%"] += 1
            else:
                size_bins[">25%"] += 1

    if area_values:
        print(
            "Minimum box area:",
            f"{min(area_values) * 100:.4f}%"
        )
        print(
            "Maximum box area:",
            f"{max(area_values) * 100:.2f}%"
        )
        print(
            "Mean box area:",
            f"{sum(area_values) / len(area_values) * 100:.2f}%"
        )

    print("\nBox-size distribution:")
    for key in ["<1%", "1-3%", "3-10%", "10-25%", ">25%"]:
        print(f"  {key:>7}: {size_bins[key]}")

    if boxes_per_image:
        print(
            "\nMean boxes/image:",
            round(
                sum(boxes_per_image) / len(boxes_per_image),
                3,
            ),
        )

    # ------------------------------------------------------------
    # 7. Save report
    # ------------------------------------------------------------

    print("\n[7/7] Saving report...")

    report = {
        "root": str(ROOT.resolve()),
        "images": len(images),
        "xml_annotations": len(xmls),
        "yolo_labels": len(yolos),
        "corrupt_images": len(corrupt),
        "missing_xml": len(missing_xml),
        "missing_yolo": len(missing_yolo),
        "empty_yolo": len(empty_yolo),
        "invalid_yolo": len(invalid_yolo),
        "invalid_class_ids": len(invalid_class),
        "invalid_boxes": len(invalid_box),
        "xml_class_count": len(all_xml_classes),
        "xml_classes": sorted(all_xml_classes),
        "yolo_object_count": sum(class_counts.values()),
        "xml_object_count": sum(xml_class_counts.values()),
        "duplicate_groups": len(duplicate_groups),
        "duplicate_images": sum(len(v) for v in duplicate_groups.values()),
        "dimensions": {
            f"{w}x{h}": c
            for (w, h), c in dimensions.items()
        },
        "bbox_size_bins": dict(size_bins),
    }

    out = Path("pest_ml/results/pest24_audit.json")
    out.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    print("\nReport:", out.resolve())

    print("\n" + "=" * 80)
    print("AUDIT COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
